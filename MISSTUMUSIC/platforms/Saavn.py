# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   GitHub : github.com/TOXICE765425/MisstuMusic
#   Developer : @misstu_pro | Telegram
#   Module : Misstu Music API (Saavn) — Search & Download
# ═══════════════════════════════════════════════════════════
#
# Ye platform module YouTube/yt-dlp ke bajaye seedha
# "https://misstu-music-api.vercel.app" API se gaana search
# aur download karta hai — isliye YouTube cookies ki zarurat
# is flow ke liye bilkul nahi padti.
#
# API contract (jo tumne bheja):
#   GET {BASE}/search?song=<naam>
#   -> {"success": true, "results": [
#         {"title", "artists", "album", "duration", "download_url"}, ...
#      ]}
#
# Saavn ke paas YouTube jaisi permanent "video id" nahi hoti,
# isliye har search result ko ek chhoti si in-memory cache me
# store karke uska apna "vidid" (sv... se shuru) generate karte
# hain. Slider/inline button click hone par usi id se dobara
# details nikal lete hain.

import asyncio
import logging
import os
import random
import string
from typing import Dict, List, Optional, Tuple, Union

import aiofiles
import aiohttp

import config

logger = logging.getLogger(__name__)

# .env me SAAVN_API_URL set karke apni API ka URL override bhi kar sakte ho.
SAAVN_API_BASE = (os.getenv("SAAVN_API_URL") or "https://misstu-music-api.vercel.app").rstrip("/")

DOWNLOAD_DIR = "downloads"

# ── In-memory track cache (id -> track record) ─────────────────────────────
_TRACK_CACHE: Dict[str, Dict] = {}
_CACHE_MAX = 1000

_session: Optional[aiohttp.ClientSession] = None
_session_lock = asyncio.Lock()


async def _get_session() -> aiohttp.ClientSession:
    global _session
    async with _session_lock:
        if _session is None or _session.closed:
            _session = aiohttp.ClientSession()
        return _session


def _gen_id() -> str:
    return "sv" + "".join(random.choices(string.ascii_lowercase + string.digits, k=9))


def _store(track: Dict) -> str:
    if len(_TRACK_CACHE) > _CACHE_MAX:
        for k in list(_TRACK_CACHE.keys())[: _CACHE_MAX // 2]:
            _TRACK_CACHE.pop(k, None)
    tid = _gen_id()
    _TRACK_CACHE[tid] = track
    return tid


def is_saavn_id(vidid: Union[str, None]) -> bool:
    """True agar ye id humari Saavn cache ki hai (YouTube id nahi)."""
    return bool(vidid) and str(vidid).startswith("sv") and str(vidid) in _TRACK_CACHE


class SaavnAPI:
    """Misstu Music API (Saavn) client — YouTube.py jaisa hi interface deta hai
    (`track`, `download`) taaki play.py / stream.py me drop-in use ho sake."""

    def __init__(self):
        self.base = SAAVN_API_BASE

    # ── Search ──────────────────────────────────────────────────────────────
    async def search(self, query: str, limit: int = 8) -> List[Dict]:
        session = await _get_session()
        try:
            async with session.get(
                f"{self.base}/search",
                params={"song": query},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Saavn API status {resp.status} for query={query!r}")
                    return []
                data = await resp.json(content_type=None)
        except Exception as e:
            logger.error(f"Saavn search error: {e}")
            return []

        if not data or not data.get("success"):
            return []
        return (data.get("results") or [])[:limit]

    def _build_details(self, item: Dict) -> Tuple[Dict, str]:
        title = (item.get("title") or "Unknown").strip()
        download_url = item.get("download_url")
        if not download_url:
            raise ValueError("Track has no download_url")

        record = {
            "title": title,
            "artists": item.get("artists") or "",
            "album": item.get("album") or "",
            "duration_min": item.get("duration") or None,
            "download_url": download_url,
        }
        tid = _store(record)
        details = {
            "title": title,
            "link": download_url,
            "vidid": tid,
            "duration_min": record["duration_min"],
            "thumb": config.STREAM_IMG_URL,
        }
        return details, tid

    # ── Public API mirroring YouTube.track() ────────────────────────────────
    async def track(self, query: str) -> Tuple[Dict, str]:
        """query se top result dhoondo — YouTube.track() jaisa (details, track_id)."""
        results = await self.search(query, limit=1)
        if not results:
            raise ValueError("Saavn API par koi result nahi mila")
        return self._build_details(results[0])

    async def track_by_id(self, track_id: str) -> Tuple[Dict, str]:
        """Cache se pehle-search-kiya hua track wapas nikalo (button click flow)."""
        record = _TRACK_CACHE.get(track_id)
        if not record:
            raise ValueError("Ye track expire ho gaya, dobara /play karke search karo")
        details = {
            "title": record["title"],
            "link": record["download_url"],
            "vidid": track_id,
            "duration_min": record["duration_min"],
            "thumb": config.STREAM_IMG_URL,
        }
        return details, track_id

    # ── Download (direct CDN url -> local file, jaisa YouTube.download() karta hai) ──
    async def download(self, track_id: str, mystic=None, **_ignored) -> Union[Tuple[str, bool], Tuple[None, None]]:
        record = _TRACK_CACHE.get(track_id)
        if not record:
            logger.error(f"Saavn download: unknown track_id {track_id}")
            return None, None

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, f"{track_id}.mp3")

        if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
            return file_path, True

        download_url = record["download_url"]
        try:
            session = await _get_session()
            async with session.get(
                download_url, timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Saavn CDN status {resp.status} for {download_url}")
                    return None, None
                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1 << 20):
                        await f.write(chunk)

            if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
                return file_path, True
            return None, None
        except Exception as e:
            logger.error(f"Saavn download error: {e}")
            return None, None


# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   github.com/TOXICE765425/MisstuMusic
# ═══════════════════════════════════════════════════════════
