from pyrogram import filters
from pyrogram.types import Message

from MISSTUMUSIC import app
from MISSTUMUSIC.core.call import MISSTU
from MISSTUMUSIC.utils.database import set_loop
from MISSTUMUSIC.utils.decorators import AdminRightsCheck
from MISSTUMUSIC.utils.colored_buttons import (
    buttons_to_inline_markup,
    smart_send_message as send_message_colored,
    smart_edit_message_text as edit_message_text_colored,
    edit_reply_markup_colored,
)
from MISSTUMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(
    filters.command(["end"], prefixes=["/", "!"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, chat_id):
    if not len(message.command) == 1:
        return
    await MISSTU.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    await send_message_colored(chat_id=message.chat.id, 
        text=_["admin_5"].format(message.from_user.mention),
        reply_markup=close_markup(_)
    )
