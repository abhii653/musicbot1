import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp

# Environment variable token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Channels to force join
CHANNEL_1 = "LighZYagami"
CHANNEL_2 = "antishu72"

app = Client(
    "musicbot",
    bot_token=BOT_TOKEN
)

vc = PyTgCalls(app)
queue = []

# ---------- /start command ----------
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        member1 = await client.get_chat_member(CHANNEL_1, user_id)
        member2 = await client.get_chat_member(CHANNEL_2, user_id)
    except:
        member1 = None
        member2 = None

    if member1 is None or member2 is None:
        buttons = [
            [
                InlineKeyboardButton("🔔 Join Channel 1", url=f"https://t.me/{CHANNEL_1}"),
                InlineKeyboardButton("🔔 Join Channel 2", url=f"https://t.me/{CHANNEL_2}")
            ]
        ]
        await message.reply_photo(
            photo="music.jpg",
            caption="⚠️ You must join both channels to use this bot.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # If user joined both channels
    buttons = [
        [
            InlineKeyboardButton("➕ Add Bot To Your Channel", url="https://t.me/LulzZec_Bot?startchannel=true")
        ]
    ]
    await message.reply_photo(
        photo="music.jpg",
        caption=(
            "🎧 Welcome to YouTube Music Bot\n\n"
            "▶️ Play unlimited music from YouTube\n\n"
            "Bot was created by LulzSec"
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------- /play command ----------
@app.on_message(filters.command("play"))
async def play(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Please provide a song name!\nUsage: /play song name")
        return

    song_name = " ".join(message.command[1:])
    results = YoutubeSearch(song_name, max_results=1).to_dict()
    if not results:
        await message.reply("❌ Song not found on YouTube!")
        return

    url = "https://www.youtube.com" + results[0]["url_suffix"]

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extractaudio': True,
        'audioformat': "mp3",
        'outtmpl': 'song.%(ext)s',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info)

    queue.append(audio_file)

    try:
        if not vc.is_connected:
            await vc.join_group_call(message.chat.id, AudioPiped(queue[0]))
            await message.reply(f"▶️ Now Playing: {song_name}")
            queue.pop(0)
        else:
            await message.reply(f"✅ Added to queue: {song_name}")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# ---------- /stop command ----------
@app.on_message(filters.command("stop"))
async def stop(client: Client, message: Message):
    try:
        await vc.leave_group_call(message.chat.id)
        queue.clear()
        await message.reply("⏹ Music stopped and queue cleared.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

print("Bot Started...")
app.run()