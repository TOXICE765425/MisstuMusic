# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   GitHub : github.com/TOXICE765425/MisstuMusic
#   Developer : @misstu_pro | Telegram
#   Module : Package Initialization & App Setup
# ═══════════════════════════════════════════════════════════

from MISSTUMUSIC.core.bot import MISSTU
from MISSTUMUSIC.core.dir import dirr
from MISSTUMUSIC.core.git import git
from MISSTUMUSIC.core.userbot import Userbot
from MISSTUMUSIC.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = MISSTU()
userbot = Userbot()

# ── Kurigram mention fix ──────────────────────────────────────
# Kurigram ka User.mention bina quotes ka anchor banata hai:
#     <a href=tg://user?id=123>Name</a>
# Telegram Bot API usse parse nahi kar pata ("Unexpected end of name
# token") → Bot API path fail → buttons colorless fallback me jaate
# hain. Isliye mention ko QUOTED anchor ke saath override karte hain.
try:
    from pyrogram.types import User as _KurigramUser

    def _quoted_mention(self):
        name = self.first_name or "Deleted Account"
        return f'<a href="tg://user?id={self.id}">{name}</a>'

    _KurigramUser.mention = property(_quoted_mention)
    LOGGER("MISSTUMUSIC").info("✔ mention HTML quote fix applied")
except Exception as _e:
    LOGGER("MISSTUMUSIC").warning(f"mention fix failed: {_e}")


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
Saavn = SaavnAPI()

# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   github.com/TOXICE765425/MisstuMusic
# ═══════════════════════════════════════════════════════════
