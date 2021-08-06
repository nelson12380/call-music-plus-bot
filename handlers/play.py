

from os import path

from pyrogram import Client, filters 
from pyrogram.types import Message, Voice, InlineKeyboardMarkup, InlineKeyboardButton, Chat, CallbackQuery
from youtube_search import YoutubeSearch
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, UsernameNotOccupied
from callsmusic import callsmusic, queues

import converter
import youtube
import requests
import aiohttp
import wget

from helpers.database import db, Database
from helpers.dbthings import handle_user_status
from config import DURATION_LIMIT, LOG_CHANNEL, BOT_USERNAME, THUMB_URL
from helpers.errors import DurationLimitError
from helpers.filters import command, other_filters
from helpers.decorators import errors
from converter.converter import convert
from . import que


@Client.on_message(filters.private)
async def _(bot: Client, cmd: command):
    await handle_user_status(bot, cmd)



PLAYMSG_BUTTONS = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏸ Pause ⏸",callback_data="cbpause"),
                    InlineKeyboardButton("⏩ Next song⏩", callback_data="cbskip"),
                ],
                [
                    InlineKeyboardButton(text="Watch On YouTube 🎬",url="https://www.youtube.com/watch?v=G58pr-Ro5aY&t=22s"),
                    InlineKeyboardButton(text="🔔Bot Updates", url="https://t.me/SL_bot_zone"),
                ],
                [
                    InlineKeyboardButton(text="❌ Close",callback_data="close")],
            ]
        )


JOIN_ASAP = "<b>You Need To Join My updates channel  For Executing This Command 👮‍♀️...</b>"

FSUBB = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton(text="🔔 Join My Channel", url=f"https://t.me/sl_bot_zone")
        ]]
    )


@Client.on_message(command(["nplay", f"nplay@{BOT_USERNAME}"]) & other_filters)
@errors
async def play(_, message: Message):
    try:
        await message._client.get_chat_member(int("-1001325914694"), message.from_user.id)
    except UserNotParticipant:
        await message.reply_text(
        text=JOIN_ASAP, disable_web_page_preview=True, reply_markup=FSUBB
    )
        return
    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None

    response = await message.reply_text("<b> Please Wait ⏳ ...🎵 Processing Your Song ... </b>")

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"no! Videos longer than `{DURATION_LIMIT}` minute(s) aren’t allowed, the provided audio is {round(audio.duration / 60)} minute(s) 😒"
            )

        file_name = audio.file_unique_id + "." + (
            (
                audio.file_name.split(".")[-1]
            ) if (
                not isinstance(audio, Voice)
            ) else "ogg"
        )

        file = await converter.convert(
            (
                await message.reply_to_message.download(file_name)
            )
            if (
                not path.isfile(path.join("downloads", file_name))
            ) else file_name
        )
    else:
        messages = [message]
        text = ""
        offset = None
        length = None

        if message.reply_to_message:
            messages.append(message.reply_to_message)

        for _message in messages:
            if offset:
                break

            if _message.entities:
                for entity in _message.entities:
                    if entity.type == "url":
                        text = _message.text or _message.caption
                        offset, length = entity.offset, entity.length
                        break

        if offset in (None,):
            await response.edit_text(f" You did not give me anything to play!")
            return

        url = text[offset:offset + length]
        file = await converter.convert(youtube.download(url))

    if message.chat.id in callsmusic.active_chats:
        thumb = THUMB_URL
        position = await queues.put(message.chat.id, file=file)
        MENTMEH = message.from_user.mention()
        await response.delete()
        await message.reply_photo(thumb, caption=f"Your Song Queued at position💡** `{position}`! \n**Requested by: {MENTMEH}**", reply_markup=PLAYMSG_BUTTONS)
    else:
        thumb = THUMB_URL
        await callsmusic.set_stream(message.chat.id, file)
        await response.delete()
        await message.reply_photo(thumb, caption="<b>Playing Your Song 🎸... </b>\n**Requested by: {}**\nvia @sl_bot_zone 🎙".format(message.from_user.mention()), reply_markup=PLAYMSG_BUTTONS)


# Pros reading this code be like: Wait wut? wtf? dumb? Me gonna die, lol etc.

@Client.on_message(command("play") & other_filters)
async def nplay(_, message: Message): 
    try:
        await message._client.get_chat_member(int("-1001325914694"), message.from_user.id)
    except UserNotParticipant:
        await message.reply_text(
        text=JOIN_ASAP, disable_web_page_preview=True, reply_markup=FSUBB
    )
        return
    global que
    
    lel = await message.reply_text("<b> Please Wait ⏳ ...🎵 Processing Your Song ... </b>")
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
          results = YoutubeSearch(query, max_results=5).to_dict()
      except:   
          await lel.edit("Give me something to play")
        # Looks like hell. Aren't it?? FUCK OFF
        try:
            toxxt = "**Select the song you want to play**\n\n"
            j = 0
            useer=user_name
            emojilist = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣",]

            while j < 5:
                toxxt += f"{emojilist[j]} <b>Title - [{results[j]['title']}](https://youtube.com{results[j]['url_suffix']})</b>\n"
                toxxt += f" ╚ <b>Duration</b> - {results[j]['duration']}\n"
                toxxt += f" ╚ <b>Views</b> - {results[j]['views']}\n"
                toxxt += f" ╚ <b>Channel</b> - {results[j]['channel']}\n\n"

                j += 1            
            koyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("1️⃣", callback_data=f'plll 0|{query}|{user_id}'),
                        InlineKeyboardButton("2️⃣", callback_data=f'plll 1|{query}|{user_id}'),
                        InlineKeyboardButton("3️⃣", callback_data=f'plll 2|{query}|{user_id}'),
                    ],
                    [
                        InlineKeyboardButton("4️⃣", callback_data=f'plll 3|{query}|{user_id}'),
                        InlineKeyboardButton("5️⃣", callback_data=f'plll 4|{query}|{user_id}'),
                    ],
                    [InlineKeyboardButton(text="Close 🗑", callback_data="cls")],
                ]
            )       
            await lel.edit(toxxt,reply_markup=koyboard,disable_web_page_preview=True)
            # WHY PEOPLE ALWAYS LOVE PORN ?? (A point to think)
            return
            # Returning to pornhub
        except:
            await lel.edit("No Enough results to choose.. Starting direct play..")
                        
            # print(results)
            try:
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:40]
                thumbnail = results[0]["thumbnails"][0]
                thumb_name = f"thumb{title}.jpg"
                thumb = requests.get(thumbnail, allow_redirects=True)
                open(thumb_name, "wb").write(thumb.content)
                duration = results[0]["duration"]
                results[0]["url_suffix"]
                views = results[0]["views"]

            except Exception as e:
                await lel.edit(
                    "Song not found.Try another song or maybe spell it properly."
                )
        print(str(e))
        return
    try:    
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
             await lel.edit(f"No! Videos longer than `{DURATION_LIMIT}` minute(s) aren’t allowed, the provided audio is {round(audio.duration / 60)} minute(s) 😒")
             return
    except:
        pass    

    file = await convert(youtube.download(url))
    if message.chat.id in callsmusic.active_chats:
        thumb = THUMB_URL
        position = await queues.put(message.chat.id, file=file)
        MENTMEH = message.from_user.mention()
        await lel.delete()
        await message.reply_photo(thumb, caption=f"**Your Song Queued at position💡** `{position}`! \n**Requested by: {MENTMEH}**", reply_markup=PLAYMSG_BUTTONS)
    else:
        thumb = THUMB_URL
        await callsmusic.set_stream(message.chat.id, file)
        await lel.delete()
        await message.reply_photo(thumb, caption="<b>Playing Your Song 🎸... </b>\n**Requested by: {}**\nvia @sl_bot_zone 🎙".format(message.from_user.mention()), reply_markup=PLAYMSG_BUTTONS)
