# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   GitHub : github.com/TOXICE765425/MisstuMusic
#   Developer : @misstu_pro | Telegram
#   Module : Loop Play Command
# ═══════════════════════════════════════════════════════════

from pyrogram import filters
from pyrogram.types import Message

from MISSTUMUSIC import app
from MISSTUMUSIC.utils.database import get_loop, set_loop
from MISSTUMUSIC.utils.decorators import AdminRightsCheck
from MISSTUMUSIC.utils.colored_buttons import (
    buttons_to_inline_markup,
    smart_send_message as send_message_colored,
    smart_edit_message_text as edit_message_text_colored,
    edit_reply_markup_colored,
)
from MISSTUMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(filters.command(["loop", "cloop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def admins(cli, message: Message, _, chat_id):
    usage = _["admin_17"]
    if len(message.command) != 2:
        return await send_message_colored(chat_id=message.chat.id, text=usage)
    state = message.text.split(None, 1)[1].strip()
    if state.isnumeric():
        state = int(state)
        if 1 <= state <= 10:
            got = await get_loop(chat_id)
            if got != 0:
                state = got + state
            if int(state) > 10:
                state = 10
            await set_loop(chat_id, state)
            return await send_message_colored(chat_id=message.chat.id, 
                text=_["admin_18"].format(state, message.from_user.mention),
                reply_markup=close_markup(_),
            )
        else:
            return await send_message_colored(chat_id=message.chat.id, text=_["admin_17"])
    elif state.lower() == "enable":
        await set_loop(chat_id, 10)
        return await send_message_colored(chat_id=message.chat.id, 
            text=_["admin_18"].format(state, message.from_user.mention),
            reply_markup=close_markup(_),
        )
    elif state.lower() == "disable":
        await set_loop(chat_id, 0)
        return await send_message_colored(chat_id=message.chat.id, 
            text=_["admin_19"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )
    else:
        return await send_message_colored(chat_id=message.chat.id, text=usage)

# ═══════════════════════════════════════════════════════════
#        😎  MISSTU MUSIC BOT  😎
#   github.com/TOXICE765425/MisstuMusic
# ═══════════════════════════════════════════════════════════
