# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   GitHub : github.com/TOXICE765425/MisstuMusic
#   Developer : @misstu_pro | Telegram
#   Module : Resume Stream Command
# ═══════════════════════════════════════════════════════════

from pyrogram import filters
from pyrogram.types import Message

from MISSTUMUSIC import app
from MISSTUMUSIC.core.call import MISSTU
from MISSTUMUSIC.utils.database import is_music_playing, music_on
from MISSTUMUSIC.utils.decorators import AdminRightsCheck
from MISSTUMUSIC.utils.colored_buttons import (
    buttons_to_inline_markup,
    smart_send_message as send_message_colored,
    smart_edit_message_text as edit_message_text_colored,
    edit_reply_markup_colored,
)
from MISSTUMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(filters.command(["resume", "cresume"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def resume_com(cli, message: Message, _, chat_id):
    if await is_music_playing(chat_id):
        return await send_message_colored(chat_id=message.chat.id, text=_["admin_3"])
    await music_on(chat_id)
    await MISSTU.resume_stream(chat_id)
    await send_message_colored(chat_id=message.chat.id, 
        text=_["admin_4"].format(message.from_user.mention),
        reply_markup=close_markup(_)
    )

# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   github.com/TOXICE765425/MisstuMusic
# ═══════════════════════════════════════════════════════════
