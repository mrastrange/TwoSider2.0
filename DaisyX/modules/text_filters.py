# This filte is ported from WilliamButcherBot
# Credits goes to TheHamkerCat


# Ported from https://github.com/TheHamkerCat/WilliamButcherBot
"""
MIT License
Copyright (c) 2021 TheHamkerCat
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from pyrogram import filters

from DaisyX.db.mongo_helpers.filterdb import (
    delete_filter,
    get_filter,
    get_filters_names,
    save_filter,
)
from DaisyX.function.pluginhelpers import member_permissions
from DaisyX.services.pyrogram import pbot as app

# Original file >> https://github.com/TheHamkerCat/WilliamButcherBot/blob/dev/wbb/modules/filters.py


@app.on_message(filters.command("filter") & ~filters.edited & ~filters.private)
async def save_filters(_, message):
    if len(message.command) < 2 or not message.reply_to_message:
        await message.reply_text(
            "Usage:\nReply to a text or sticker with /filter <textfilter name> to save it. \n\n NOTE: **TRY OUR NEW FILTER SYSTEM WITH /addfilter**"
        )

    elif not message.reply_to_message.text and not message.reply_to_message.sticker:
        await message.reply_text(
            "__**You can only save text or stickers as text filters.**__\n\n NOTE: **TRY /addfilter FOR OTHER FILE TYPES**"
        )

    elif len(await member_permissions(message.chat.id, message.from_user.id)) < 1:
        await message.reply_text("**You don't have enough permissions**")
    elif "can_change_info" not in await member_permissions(
        message.chat.id, message.from_user.id
    ):
        await message.reply_text("**You don't have enough permissions**")
    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            await message.reply_text("**Usage**\n__/filter <textfilter name>__")
            return
        _type = "text" if message.reply_to_message.text else "sticker"
        _filter = {
            "type": _type,
            "data": message.reply_to_message.text.markdown
            if _type == "text"
            else message.reply_to_message.sticker.file_id,
        }
        await save_filter(message.chat.id, name, _filter)
        await message.reply_text(f"__**Saved filter {name}.**__")


@app.on_message(filters.command("filters") & ~filters.edited & ~filters.private)
async def get_filterss(_, message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        return
    msg = f"Text filters in {message.chat.title}\n"
    for _filter in _filters:
        msg += f"**-** `{_filter}`\n"
    await message.reply_text(msg)


@app.on_message(filters.command("stop") & ~filters.edited & ~filters.private)
async def del_filter(_, message):
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage**\n__/stop <textfilter name> \nIf filter /delfilter <filtername>__"
        )

    elif len(await member_permissions(message.chat.id, message.from_user.id)) < 1:
        await message.reply_text("**You don't have enough permissions**")

    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            await message.reply_text(
                "**Usage**\n__/stop <textfilter name> \nIf filter /delfilter <filtername> __"
            )
            return
        chat_id = message.chat.id
        deleted = await delete_filter(chat_id, name)
        if deleted:
            await message.reply_text(f"**Deleted filter {name}.**")
        else:
            await message.reply_text('**No such filter.**')


@app.on_message(
    filters.incoming & filters.text & ~filters.private & ~filters.channel & ~filters.bot
)
async def filters_re(_, message):
    try:
        if message.text[0] != "/":
            text = message.text.lower().strip().split(" ")
            if text:
                chat_id = message.chat.id
                list_of_filters = await get_filters_names(chat_id)
                for word in text:
                    if word in list_of_filters:
                        _filter = await get_filter(chat_id, word)
                        data_type = _filter["type"]
                        data = _filter["data"]
                        if data_type == "text":
                            await message.reply_text(data)
                        else:
                            await message.reply_sticker(data)
                        message.continue_propagation()
    except Exception:
        pass
