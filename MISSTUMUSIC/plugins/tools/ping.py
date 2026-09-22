from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
from config import *
from MISSTUMUSIC import app
from MISSTUMUSIC.core.call import MISSTU
from MISSTUMUSIC.utils import bot_sys_stats
from MISSTUMUSIC.utils.decorators.language import language
from MISSTUMUSIC.utils.colored_buttons import buttons_to_inline_markup, smart_edit_message_text as edit_message_text_colored
from MISSTUMUSIC.utils.inline import supp_markup
from config import BANNED_USERS, PING_VID_URL


@app.on_message(filters.command("ping", prefixes=["/"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_video(
        video=PING_VID_URL,
        caption=_["ping_1"].format(app.mention),
    )
    pytgping = await MISSTU.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await edit_message_text_colored(
        chat_id=response.chat.id,
        message_id=response.id,
        text=_["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(_),
    )
