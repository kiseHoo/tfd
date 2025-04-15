import asyncio
import re
import aiohttp
import os
import time
from uuid import uuid4
from datetime import datetime
import redis
import telethon
import telethon.tl.types
from telethon import events
from telethon import TelegramClient, events
from telethon.tl.functions.messages import ForwardMessagesRequest
from telethon.types import Message, UpdateNewMessage
from telethon import Button
from cansend import CanSend
from config import *
from terabox import get_data
from stats import (
    track_message,
    get_message_count,
    get_new_user_count_today,
    get_top_active_users,
    get_file_type_stats,
)
from tools import (
    convert_seconds,
    download_file,
    download_image_to_bytesio,
    extract_code_from_url,
    get_formatted_size,
    get_urls_from_string,
    is_user_on_chat,
    get_bot_username,
)

BOT_USERNAME = get_bot_username(BOT_TOKEN)

bot = TelegramClient("tele", API_ID, API_HASH)

db = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


bot_start_time = time.time()
user_count = db.scard("users")
user_ids = db.smembers("users")  # Retrieve user IDs


def format_top_users(top_users):
    """Formats the top active users data for display."""
    formatted = ""
    for i, (user_id, score) in enumerate(top_users, start=1):
        formatted += (
            f"{i}. User ID: [{user_id}](tg://user?id={user_id}) (Score: {score})\n"
        )
    return formatted


def format_file_stats(file_stats):
    """Formats the file type statistics for display."""
    formatted = ""
    for file_type, count in file_stats.items():
        formatted += f"{file_type}: {count}\n"
    return formatted


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        pattern="/ban (.*)", incoming=True, outgoing=False, from_users=ADMINS
    )
)
async def ban_user(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    try:
        user_id = int(m.pattern_match.group(1))  # Get user ID to ban
    except ValueError:
        return await m.reply("Invalid user ID format.")

    if db.sismember("banned_users", user_id):
        await m.reply("User is already banned.")
    else:
        db.sadd("banned_users", user_id)
        await m.reply(f"User ID {user_id} has been banned.")


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        pattern="/unban (.*)", incoming=True, outgoing=False, from_users=ADMINS
    )
)
async def unban_user(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    try:
        user_id = int(m.pattern_match.group(1))
    except ValueError:
        return await m.reply("Invalid user ID format.")

    if db.srem("banned_users", user_id):
        await m.reply(f"User ID {user_id} has been unbanned.")
    else:
        await m.reply("User is not banned.")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/stats$", incoming=True, outgoing=False))
async def stats_command(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    check_if = await is_user_on_chat(bot, f"@RishuCoder", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @RishuCoder then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@Rishu_mood", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @Rishu_mood then send me the link again.")

    uptime = convert_seconds(time.time() - bot_start_time)
    message_count = get_message_count()
    new_users_today = get_new_user_count_today()
    top_users = get_top_active_users()
    file_stats = get_file_type_stats()

    stats_message = f"""
**Bot Statistics:**

** Total Messages: {message_count}**
** New Users Today: {new_users_today}**
** Top Active Users:\n {format_top_users(top_users)}**
** File Types: {format_file_stats(file_stats)}**

** Uptime: {uptime}**
** Users: {user_count}**

@{BOT_USERNAME}
"""

    if m.sender_id == OWNER_ID:
        await m.reply(stats_message)
    else:
        await m.reply("Sorry, this command is restricted to the bot owner.")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/start$", incoming=True, outgoing=False))
async def start(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return

    first_name = m.sender.first_name
    user_id = m.sender_id
    reply_text = f"""
**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼──────•
┆◍ ʜᴇʏ [{first_name}](tg://user?id={m.sender.id})!
└──────────────────────•
» ✦ ϻσsᴛ ᴘσᴡєꝛғυʟʟ ᴛєꝛᴧʙσx ʙσᴛ  
» ✦ ʙєsᴛ ғєᴧᴛυꝛє ʙσᴛ ση ᴛєʟєɢꝛᴧϻ 
» ✦ ғᴧsᴛ ᴅσᴡηʟσᴧᴅ sυᴘᴘσꝛᴛєᴅ
» ✦ ησ ʟᴧɢ, ғᴧsᴛ ᴧηᴅ sєᴄυꝛє 
» ✦ ᴘꝛєϻɪυϻ ғєᴧᴛυꝛєs
•──────────────────────•
❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ  »»  [˹ʀɪsʜυ ʙσᴛ˼ ](t.me/ur_rishu_143) 
•──────────────────────•**
"""
    if not db.sismember("users", str(m.sender_id)):
        db.sadd("users", str(m.sender_id))
    if not db.sismember("new_users", str(user_id)):  # Check Redis
        # Send new user notification (only if it's the first time)
        await bot.send_message(
            USER_CHANNEL,
            f"**New User Joined**\nName: {first_name} \nUser ID: [{user_id}](tg://user?id={user_id})\n@{BOT_USERNAME}",
            parse_mode="markdown",
        )
        db.sadd("new_users", str(user_id))

    check_if = await is_user_on_chat(bot, f"@rishucoder", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @rishucoder then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@rishu_mood", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @rishu_mood then send me the link again.")
    await m.reply(
        reply_text,
        buttons = [
    [
        Button.url("˹ υᴘᴅᴧᴛє ˼", "https://t.me/Ur_rishu_143"),
        Button.url("˹ sυᴘᴘσꝛᴛ ˼", "https://t.me/ur_support07")
    ],
    [
        Button.url("˹ ᴧʟʟ ᴧᴘɪ ˼", "https://t.me/RishuApi"),
        Button.url("˹ ᴧʟʟ ʙᴏᴛ ˼", "https://t.me/Vip_robotz/4")
    ]
        ],
        link_preview=False,
        parse_mode="markdown",
    )


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/broadcast$", incoming=True, outgoing=False))
async def broadcast(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    user_id = m.sender_id
    if m.sender_id != OWNER_ID:  # Check if user is authorized
        await m.reply("Sorry, you don't have permission to broadcast.")
        return

    message_text = await m.get_reply_message()  # Get message to broadcast
    if not message_text:
        await m.reply("Please reply with the message you want to broadcast.")
        return
    for user_id in user_ids:
        try:
            await bot.send_message(int(user_id), message_text.message)
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")

    await m.reply("Broadcast sent successfully!")


# ----------------------------------------------------------------------------------------------------


@bot.on(events.NewMessage(pattern="/help$", incoming=True, outgoing=False))
async def help_command(m: UpdateNewMessage):
    if m.is_group or m.is_channel:
        return
    check_if = await is_user_on_chat(bot, f"@rishucoder", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @rishucoder then send me the link again.")
    check_if = await is_user_on_chat(bot, f"@rishu_mood", m.peer_id)
    if not check_if:
        return await m.reply(f"Please join @rishu_mood then send me the link again.")
    help_text = """**     ⍟─── ϻʏ ᴅᴇᴛᴀɪʟꜱ ───⍟
    
───────────────────────
❖ ɪ ᴧϻ ϻσsᴛ ᴘσᴡєʀғυʟʟ ᴛєꝛᴧʙσx ʙσᴛ   
───────────────────────
● ᴡʀɪᴛᴛєη ɪη ᴩʏᴛʜση ᴡɪᴛʜ sǫʟᴧʟᴄʜєϻʏ
   ᴧηᴅ ϻσηɢσᴅʙ ᴧs ᴅᴧᴛᴧʙᴧsє
───────────────────────
● ɪ ᴄᴧη ᴅσᴡηʟσᴧᴅ ᴛєꝛᴧʙσx ᴠɪᴅєσ 
● ɪ ᴄᴧη ʀєꜱᴛʀɪᴄᴛ υꜱєʀꜱ
● ɪ ʜᴧᴠє ғᴧsᴛ ᴅσᴡηʟσᴧᴅ sυᴘᴘσꝛᴛєᴅ
● ɪ ʜᴧᴠє ᴘꝛєϻɪυϻ ғєᴧᴛυꝛєs
● ɪ ʜᴧᴠє ᴧɪ ɪηᴛєɢʀᴧᴛɪση
───────────────────────
❖ υᴘᴅᴧᴛєs ᴄʜᴧηηєʟ ➥ [ʀɪsʜυ υᴘᴅᴧᴛє](https://t.me/UR_RISHU_143) 
❖ sυᴘᴘσʀᴛ ᴄʜᴧᴛ ➥ [ʀɪsʜυ υᴘᴅᴧᴛє](https://t.me/UR_Support07)
❖ ʀєᴧʟ σᴡηєʀ ➥ [ʀɪsʜυ ](https://t.me/rishu1286)
───────────────────────
❖sєηᴅ ϻє ʏσυꝛ ᴛєꝛᴧʙσx ʟɪηᴋ ᴛσ ᴅσᴡηʟσᴧᴅ ʏσυꝛ ᴠɪᴅєσ 

───────────────────────**"""
    link_preview = (False,)
    await m.reply(
        help_text,
        parse_mode="markdown",
        buttons = [
    [
        Button.url("˹ υᴘᴅᴧᴛє ˼", "https://t.me/Ur_rishu_143"),
        Button.url("˹ sυᴘᴘσꝛᴛ ˼", "https://t.me/ur_support07")
    ],
    [
        Button.url("˹ ᴧʟʟ ᴧᴘɪ ˼", "https://t.me/RishuApi"),
        Button.url("˹ ᴧʟʟ ʙᴏᴛ ˼", "https://t.me/Vip_robotz/4")
    ]
        ],
    )


# Extract File ID from TeraBox URL
def extract_file_id(url: str) -> str:
    match = re.search(r'/s/([\w]+)', url)
    return match.group(1) if match else None

# Get file details from custom API
async def get_file_details(terabox_url):
    file_id = extract_file_id(terabox_url)
    if not file_id:
        return None, "Invalid TeraBox URL"

    api_url = f"https://tight-leaf-6d92.brendanav492.workers.dev/?id={file_id}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return None, f"API returned status code: {response.status}"
                data = await response.json()
                return data, None
        except Exception as e:
            return None, str(e)


# ----------------------------------------------------------------------------------------------------


@bot.on(
    events.NewMessage(
        incoming=True,
        outgoing=False,
        func=lambda message: message.text and get_urls_from_string(message.text),
    )
)
async def get_message(m: Message):
    asyncio.create_task(handle_message(m))


async def handle_message(m: Message):
    if m.is_group or m.is_channel:
        return
    username = m.sender.username
    first_name = m.sender.first_name
    user_id = m.sender_id
    if db.sismember("banned_users", user_id):
        await m.reply(
            "You are banned from using this bot. Conntact support for more info."
        )
        return

    url = get_urls_from_string(m.text)
    if not url:
        return await m.reply("Please enter a valid url.")
    check_if = await is_user_on_chat(bot, "@rishucoder", m.peer_id)
    if not check_if:
        return await m.reply("Please join @rishucoder  then send me the link again.")
    check_if = await is_user_on_chat(bot, "@rishu_mood", m.peer_id)
    if not check_if:
        return await m.reply("Please join @rishu_mood then send me the link again.")
    is_spam = db.get(m.sender_id)
    if is_spam and m.sender_id not in [5738579437]:
        return await m.reply("You are spamming. Please wait a 1 minute and try again.")
    hm = await m.reply("Sending you the media wait...")
    count = db.get(f"check_{m.sender_id}")
    if count and int(count) > 15:
        return await hm.edit(
            "You are limited now. Please come back after 2 hours or use another account."
        )
    shorturl = extract_code_from_url(url)
    if not shorturl:
        return await hm.edit("Seems like your link is invalid.")
    fileid = db.get(shorturl)
    if fileid:
        try:
            await hm.delete()
        except:
            pass

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[int(fileid)],
                to_peer=m.chat.id,
                drop_author=True,
                # noforwards=True, #Uncomment it if you dont want to forward the media.
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        db.set(m.sender_id, time.monotonic(), ex=60)
        db.set(
            f"check_{m.sender_id}",
            int(count) + 1 if count else 1,
            ex=7200,
        )

        return
    track_message(m.sender_id)
    data = get_data(url)
    if not data:
        return await hm.edit("Sorry! API is dead or maybe your link is broken.")
    db.set(m.sender_id, time.monotonic(), ex=60)
    if (
        not data["file_name"].endswith(".mp4")
        and not data["file_name"].endswith(".mkv")
        and not data["file_name"].endswith(".Mkv")
        and not data["file_name"].endswith(".webm")
        and not data["file_name"].endswith(".ts")
        and not data["file_name"].endswith(".mov")
        and not data["file_name"].endswith(".hevc")
        and not data["file_name"].endswith(".png")
        and not data["file_name"].endswith(".jpg")
        and not data["file_name"].endswith(".jpeg")
    ):
        return await hm.edit(
            f"Sorry! File is not supported for now. I can download only .mp4, .mkv, .webm, .ts, .mov, .hevc, .png, .jpg, .jpeg files."
        )
    if int(data["sizebytes"]) > 524288000 and m.sender_id not in [5738579437]:
        return await hm.edit(
            f"Sorry! File is too big. I can download only 500MB and this file is of {data['size']} ."
        )

    start_time = time.time()
    cansend = CanSend()

    async def progress_bar(current_downloaded, total_downloaded, state="Sending"):

        if not cansend.can_send():
            return
        bar_length = 20
        percent = current_downloaded / total_downloaded
        arrow = "█" * int(percent * bar_length)
        spaces = "░" * (bar_length - len(arrow))

        elapsed_time = time.time() - start_time

        head_text = f"{state} `{data['file_name']}`"
        progress_bar = f"[{arrow + spaces}] {percent:.2%}"
        upload_speed = current_downloaded / elapsed_time if elapsed_time > 0 else 0
        speed_line = f"Speed: **{get_formatted_size(upload_speed)}/s**"

        time_remaining = (
            (total_downloaded - current_downloaded) / upload_speed
            if upload_speed > 0
            else 0
        )
        time_line = f"Time Remaining: `{convert_seconds(time_remaining)}`"

        size_line = f"Size: **{get_formatted_size(current_downloaded)}** / **{get_formatted_size(total_downloaded)}**"

        await hm.edit(
            f"{head_text}\n{progress_bar}\n{speed_line}\n{time_line}\n{size_line}",
            parse_mode="markdown",
        )

    uuid = str(uuid4())
    thumbnail = download_image_to_bytesio(data["thumb"], "thumbnail.png")

    try:
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            file=data["direct_link"],
            thumb=thumbnail if thumbnail else None,
            progress_callback=progress_bar,
            caption=f"""
File Name: `{data['file_name']}`
Size: **{data["size"]}**

@Ur_Rishu_143

link {api_url}
""",
            supports_streaming=True,
            spoiler=True,
        )

        # pm2 start python3 --name "terabox" -- main.py
    except telethon.errors.rpcerrorlist.WebpageCurlFailedError:
        download = await download_file(
            data["direct_link"], data["file_name"], progress_bar
        )
        if not download:
            return await hm.edit(
                f"Sorry! Download Failed but you can download it from [here]({data['direct_link']}).",
                parse_mode="markdown",
            )
        file = await bot.send_file(
            PRIVATE_CHAT_ID,
            download,
            caption=f"""
File Name: `{data['file_name']}`
Size: **{data["size"]}**

@Ur_Rishu_143

Link {api_url}
""",
            progress_callback=progress_bar,
            thumb=thumbnail if thumbnail else None,
            supports_streaming=True,
            spoiler=True,
        )
        try:
            os.unlink(download)
        except Exception as e:
            print(e)
    except Exception:
        return await hm.edit(
            f"Sorry! Download Failed but you can download it from [here]({data['direct_link']}).",
            parse_mode="markdown",
        )
    try:
        os.unlink(download)
    except Exception as e:
        pass
    try:
        await hm.delete()
    except Exception as e:
        print(e)

    if shorturl:
        db.set(shorturl, file.id)
    if file:
        db.set(uuid, file.id)

        await bot(
            ForwardMessagesRequest(
                from_peer=PRIVATE_CHAT_ID,
                id=[file.id],
                to_peer=m.chat.id,
                top_msg_id=m.id,
                drop_author=True,
                # noforwards=True,  #Uncomment it if you dont want to forward the media.
                background=True,
                drop_media_captions=False,
                with_my_score=True,
            )
        )
        db.set(m.sender_id, time.monotonic(), ex=60)
        db.set(
            f"check_{m.sender_id}",
            int(count) + 1 if count else 1,
            ex=7200,
        )


bot.start(bot_token=BOT_TOKEN)
print("Bot started!")
print(f"This bot is connected to {BOT_USERNAME}.")
print("This bot is deployed by @rishucoder kindly join this channel for more updates.")
bot.run_until_disconnected()
