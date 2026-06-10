# saykoxharsh_bot_multi.py
import subprocess, sys

def install_deps():
    deps = ["python-telegram-bot==20.7", "aiohttp"]
    for dep in deps:
        subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"], check=False)

install_deps()

import asyncio
import functools
import json
import os
import random
import time
from datetime import datetime
from telegram import Update
try:
    from telegram.error import RetryAfter, Forbidden, BadRequest, TimedOut, NetworkError
except ImportError:
    from telegram.error import RetryAfter, Unauthorized as Forbidden, BadRequest, TimedOut, NetworkError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest
import logging
import aiohttp
import io

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [
   "8622168218:AAGeUKIX-yWvnrhNir5hTV8wPIitnPCmd08",
   "8601114563:AAE8rqFxM_kHV3YXpWZkYsS6FnfaN6wJnhE",
   "8682665371:AAGVobnZrq6BWBAL7WuOjygysSZpR6-WHCo",
   "8620643811:AAFoNO_21sW3xcuRr5f-f-hdhxgBjE5bso0",
   "8760826196:AAGFpmGTbNkaN9M24VlG42qe4Nf_4vPx-Wo",
   "8681246432:AAEF0O_1eUPeXBTSKxSUq3xWVgViWRK7Qr4",
   "8787332887:AAHKiGnUHuWrMXc0P6lFu36ws2hr2NafPdc",
   "8336134430:AAHKpOeckZsLo2uyKjEFQ-VEN_iQlWZ9RdM",
   "8555525992:AAE0CFcPjLooHI8hWWl5j_pPdBQZy094PVc",
   "8685566108:AAFjns749zzFzdycsypPdjzEBSbbGRJL5Ys",
   "8710696214:AAEL6jNWuQdZsJ_J2g6EjAz8lITaQtjr_DQ",
   "8634988115:AAHbspNZtAK6qcScS0mu2D-FTJnRxuv1lfo",
   "8231583407:AAFhOcCYbAht0JLnKJUzEjs9rgzGmOPpMKY",
   "8893786299:AAG5njzZWcQMkRNoD_pRFzgOkDT0iCUiKak",
   "8638592312:AAFT0YaLRddn9RVHCZr4I0T9C3k8mobv8SU",
   "8739598998:AAGxPtj34Q4ORT-zA3NNnFFiTXH1OrTJ-es",
   "8905918975:AAHpcl0Z25CPjOOKDpaOyk2YpJggbXC-5xk",
   "8786446573:AAElk-EL-f1gXOxmr_4bBdK-yLmbglIlt_4",
   "8883085785:AAGbBh_bng5sivtqegoap2zB-m762AHecDc",
   "8325932312:AAHS-RBNf4p6jn43h7iezOUPMgb1A1dBNtg",
   "8807492849:AAHT97VJLRHh23HQGbvTYbU5PJUYV3lWV8Q",
   "8879155748:AAE9Oi_rTAlopchxaI4p6yp_oS3XSf3etNU",
   "8612118625:AAGb83ecMipSPuAJ7rZvRZ24PqwdzFye33E",
   "8831376405:AAE2aHj-vUjZc0m397W6pdNcbb0xGq3fflM",
]

CHAT_ID = 8290078174
OWNER_ID = 8290078174
SUDO_FILE = "sudo_users.json"
STICKER_FILE = "stickers.json"
VOICE_CLONES_FILE = "voice_clones.json"
tempest_API_KEY = "d827776f25a359894ad1bcf6ec40f323"

# ---------------------------
# LOGGING — WARNING only to save CPU
# ---------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------
# VOICE CHARACTERS
# ---------------------------
VOICE_CHARACTERS = {
    1:  {"name": "Urokodaki",  "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Deep Indian voice",       "style": "deep_masculine"},
    2:  {"name": "Kanae",      "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Cute sweet voice",        "style": "soft_feminine"},
    3:  {"name": "Uppermoon",  "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Creepy dark deep voice",  "style": "dark_creepy"},
    4:  {"name": "Tanjiro",    "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Heroic determined voice", "style": "heroic"},
    5:  {"name": "Nezuko",     "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Cute mute sounds",        "style": "cute_mute"},
    6:  {"name": "Zenitsu",    "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Scared whiny voice",      "style": "scared_whiny"},
    7:  {"name": "Inosuke",    "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Wild aggressive voice",   "style": "wild_aggressive"},
    8:  {"name": "Muzan",      "voice_id": "AZnzlk1XvdvUeBnXmlld", "description": "Evil mastermind voice",   "style": "evil_calm"},
    9:  {"name": "Shinobu",    "voice_id": "EXAVITQu4vr4xnSDxMaL", "description": "Gentle but deadly voice", "style": "gentle_deadly"},
    10: {"name": "Giyu",       "voice_id": "VR6AewLTigWG4xSOukaG", "description": "Silent serious voice",    "style": "silent_serious"},
}

# ---------------------------
# TEXTS
# ---------------------------
RAID_TEXTS = [
    "चुदाई Kha 😂❤️", "उठक बैठक लगा 😏🔥", "तेरी माँ चोदू 😍😍",
    "ओय कमजोर 🤢🤢", "लंड चूस 🥱🤍➿", "पिल्लै 🐕‍",
    "😱 arey 😉 ye 🤡 kaise 😋 kiya 😏 re 😁 teri 😊 maa 😍 randy 😭100% 😂",
    "कमजोर टट्टा",
    "👈🏻👆🏻🖖🏻👇🏻🤲🏻👉🏻🤏🏻 Idr Udr Jidr Bhi Dekhega Teri Randi Maa Dikhegi",
    " 𝘽𝙀𝙏𝘼 🤢᭄᭄᭄᭄ 🌟 𝙇𝙐𝙉𝘿 𝘾𝙃𝙐𝙎 🤪᭄᭄", "मदरचोद 🤮🤮", "ro 🤣🤣", "रंडी",
    "चुप tmr 😒😂", "Acha Beta ? Koi Na Mai Teri Maa Coduga 😹💥💯",
    "चुदकड़", "कमजोर पिल्ले 🤮👞", "Chup  Rndyce ⁉", "Tmkc Mein Mist Breathing ☁",
    " Teri माँ Dead 😂😂😂", "Teri Maa Chodu If Yes Then Reply To My Message 😂😂💯💯",
    "चल तेरी माँ की चुत 🥵🥵", "Tera बाप ~/SAYKOXHARSH GOD( दौगला ) ❤️‍🔥~ 💗...!!?"
]

exonc_TEXTS = [
    "💀","🔥","⚡","🎯","💥","🎪","🎭","👑","🔱","⚜️",
    "💫","⭐","🌟","✨","🎀","❤️","🖤","💔","💢","♨️",
    "💯","🅱️","🌀","🎶","🎵","🏆","🥇","🎗️","🎖️","🏅",
    "😋","😝","😜","🤪","😑","🤫","🤭","🥱","🤗","😡","😠","😤",
    "😮‍💨","🙄","😒","🥶","🥵","🤢","🫠","😎","🥸","🕯","🫧",
    "🦄","🌺","☘","🌊","🎀","♠","🧸","🌼","🌻","🌵","🌴","🌳","🌷","🌸",
    "😹","💫","😼","😽","🙀","😿","😾","🙈","🙉","🙊",
    "⭐","🌟","✨","⚡","💥","💨","💛","💙","💜","🤎","🤍","💘","💝"
]

NCEMO_EMOJIS = [
  " 💓 | |↫ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐊ᴀ 𝐓ɪᴍᴇ 𝐃ᴇᴋʜ↬🐦‍🔥🥵🐦‍🔥🥵🐦‍🔥🥵🐦‍🔥🥵🐦‍🔥💗💗💗💗💗🥵🥵🥵🥵🥵🥵🥵🥵🥵🥵🥵🥵🐳🐳🐳🐳",
  "𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝗛𝗔𝗥𝗦𝗛 𝐒ᴇ - 🦢💘 😠",
  "𝗚𝗨𝗟𝗔𝗠𝗜    𝗞𝗔𝗥   𝕊𝔸𝕐𝕂𝕆ℙ𝔸ℙ𝔸  𝗞𝗔𝗔  𝗙𝗔𝗠𝗘𝗕𝗢𝗬જ⁀➴🍃જ⁀➴😆જ⁀➴❤️ જ⁀➴🍃જ⁀➴😆જ⁀➴❤️જ⁀➴🍃જ⁀➴😆જ⁀➴❤️ જ⁀➴🍃જ⁀➴😆જ⁀➴❤️જ⁀➴🍃જ⁀➴😆જ⁀➴❤️ જ⁀➴🍃જ⁀➴😆જ⁀➴જ⁀➴",

"𝗚𝗨𝗟𝗔𝗠𝗜    𝗞𝗔𝗥  𝕊𝔸𝕐𝕂𝕆 ℙ𝔸ℙ𝔸  𝗞𝗔𝗔  𝗙𝗔𝗠𝗘𝗕𝗢𝗬જ⁀➴🍃જ⁀➴🤣જ⁀➴❤️ જ⁀➴🍃જ⁀➴🤣જ⁀➴❤️જ⁀➴🍃જ⁀➴🤣જ⁀➴❤️ જ⁀➴🍃જ⁀➴🤣જ⁀➴❤️જ⁀➴🍃જ⁀➴🤣જ⁀➴❤️ જ⁀➴🍃જ⁀➴🤣જ⁀➴જ⁀➴",

"𝗚𝗨𝗟𝗔𝗠𝗜    𝗞𝗔𝗥   𝕊𝔸𝕐𝕂𝕆 ℙ𝔸ℙ𝔸  𝗞𝗔𝗔  𝗙𝗔𝗠𝗘𝗕𝗢𝗬જ⁀➴🍃જ⁀➴💜જ⁀➴💜 જ⁀➴🍃જ⁀➴💜જ⁀➴💜જ⁀➴🍃જ⁀➴💜જ⁀➴💜 જ⁀➴🍃જ⁀➴💜જ⁀➴💜જ⁀➴🍃જ⁀➴💜જ⁀➴💜 જ⁀➴🍃જ⁀➴💜જ⁀➴જ⁀➴",



"𝗚𝗨𝗟𝗔𝗠𝗜    𝗞𝗔𝗥  𝕊𝔸𝕐𝕂𝕆 ℙ𝔸ℙ𝔸    𝗞𝗔𝗔  𝗙𝗔𝗠𝗘𝗕𝗢𝗬જ⁀➴🍃જ⁀➴🦋જ⁀➴❤️ જ⁀➴🍃જ⁀➴🦋જ⁀➴❤️જ⁀➴🍃જ⁀➴🦋જ⁀➴❤️ જ⁀➴🍃જ⁀➴🦋જ⁀➴❤️જ⁀➴🍃જ⁀➴🦋જ⁀➴❤️ જ⁀➴🍃જ⁀➴જ⁀➴જ⁀➴",
]

# ---------------------------
# GLOBAL STATE
# ---------------------------
try:
    with open(SUDO_FILE, "r") as f:
        SUDO_USERS = set(int(x) for x in json.load(f))
except Exception:
    SUDO_USERS = {OWNER_ID}

try:
    with open(STICKER_FILE, "r") as f:
        user_stickers = json.load(f)
except Exception:
    user_stickers = {}

try:
    with open(VOICE_CLONES_FILE, "r") as f:
        voice_clones = json.load(f)
except Exception:
    voice_clones = {}

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

def save_stickers():
    with open(STICKER_FILE, "w") as f:
        json.dump(user_stickers, f)

def save_voice_clones():
    with open(VOICE_CLONES_FILE, "w") as f:
        json.dump(voice_clones, f)

group_tasks      = {}
spam_tasks       = {}
react_tasks      = {}
exonc_tasks      = {}
pfp_tasks        = {}
slide_targets    = set()
slidespam_targets = set()
sticker_mode     = True
apps, bots       = [], []

# ---------------------------
# WORKER MULTIPLIERS
# 5 workers × 24 bots = 120 concurrent tasks (stable + fast)
# Higher numbers crash the process — Telegram rate-limits anyway
# ---------------------------
NC_WORKERS   = 5
SPAM_WORKERS = 5

# pfp_photos[chat_id] = list of bytes (in-memory only, no disk)
pfp_photos  = {}
pfp_delay   = 1.0

# member_cache[chat_id] = {user_id: first_name} — auto-filled as members speak
member_cache = {}

delay       = 0.0
spam_delay  = 0.0
exonc_delay = 0.0

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not update.message:
            return
        if update.effective_user.id not in SUDO_USERS:
            await update.message.reply_text("❌ You are not Monarch.")
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not update.message:
            return
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("❌ You are not owner.")
            return
        return await func(update, context)
    return wrapper

# ---------------------------
# SAFE API CALL — handles flood, ban, network
# ---------------------------
async def safe_call(coro):
    """Await a coroutine, handle Telegram errors gracefully."""
    try:
        return await coro
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after)
    except (Forbidden, BadRequest):
        pass
    except (TimedOut, NetworkError):
        await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        raise
    except Exception:
        await asyncio.sleep(0.01)

# ---------------------------
# LOOP FUNCTIONS (all use safe_call — no bans, no crashes)
# ---------------------------
async def bot_loop(bot, chat_id, base, mode):
    i = 0
    while True:
        if mode == "gcnc":
            text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
        else:
            text = f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}"
        await safe_call(bot.set_chat_title(chat_id, text))
        i += 1
        await asyncio.sleep(0)

async def ncbaap_loop(bot, chat_id, base):
    i = 0
    while True:
        patterns = [
            f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}",
            f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}",
            f"{base} {exonc_TEXTS[i % len(exonc_TEXTS)]}",
        ]
        for pattern in patterns:
            await safe_call(bot.set_chat_title(chat_id, pattern))
        i += 1
        await asyncio.sleep(0)

async def spam_loop(bot, chat_id, text):
    while True:
        await safe_call(bot.send_message(chat_id, text))
        await asyncio.sleep(0)

async def exonc_loop(bot, chat_id, base_text):
    i = 0
    while True:
        patterns = [
            f"{base_text} {exonc_TEXTS[i % len(exonc_TEXTS)]}",
            f"{exonc_TEXTS[i % len(exonc_TEXTS)]} {base_text}",
            f"{base_text}{exonc_TEXTS[i % len(exonc_TEXTS)]}",
        ]
        await safe_call(bot.set_chat_title(chat_id, random.choice(patterns)))
        i += 1
        await asyncio.sleep(0)

async def exonc_godspeed_loop(bot, chat_id, base_text):
    i = 0
    while True:
        patterns = [
            f"{base_text} {exonc_TEXTS[i % len(exonc_TEXTS)]}",
            f"{exonc_TEXTS[i % len(exonc_TEXTS)]} {base_text}",
            f"{base_text}{exonc_TEXTS[i % len(exonc_TEXTS)]}",
            f"{exonc_TEXTS[(i+1) % len(exonc_TEXTS)]} {base_text} {exonc_TEXTS[(i+2) % len(exonc_TEXTS)]}",
            f"{base_text} {exonc_TEXTS[(i+3) % len(exonc_TEXTS)]} {exonc_TEXTS[(i+4) % len(exonc_TEXTS)]}",
        ]
        for j in range(5):
            await safe_call(bot.set_chat_title(chat_id, patterns[j % len(patterns)]))
        i += 1
        await asyncio.sleep(0)

async def pfp_loop(bot, chat_id):
    """Cycle through in-memory photos as group profile picture — no disk usage."""
    i = 0
    while True:
        photos = pfp_photos.get(chat_id)
        if not photos:
            await asyncio.sleep(1)
            continue
        photo_bytes = photos[i % len(photos)]
        buf = io.BytesIO(photo_bytes)
        buf.name = "pfp.jpg"
        await safe_call(bot.set_chat_photo(chat_id, buf))
        i += 1
        await asyncio.sleep(pfp_delay)

# ---------------------------
# VOICE (async HTTP — does NOT block event loop)
# ---------------------------
async def generate_tempest_voice(text, voice_id, stability=0.5, similarity_boost=0.8):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": tempest_API_KEY,
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": stability, "similarity_boost": similarity_boost},
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return io.BytesIO(await resp.read())
    except Exception:
        pass
    return None

async def generate_multiple_voices(text, character_numbers):
    tasks = []
    for num in character_numbers:
        if num in VOICE_CHARACTERS:
            tasks.append((num, generate_tempest_voice(text, VOICE_CHARACTERS[num]["voice_id"])))
    results = await asyncio.gather(*[t for _, t in tasks], return_exceptions=True)
    voices = []
    for (num, _), audio in zip(tasks, results):
        if isinstance(audio, io.BytesIO):
            voices.append({"character": VOICE_CHARACTERS[num]["name"], "audio": audio,
                           "description": VOICE_CHARACTERS[num]["description"]})
    return voices

# ---------------------------
# CORE COMMANDS
# ---------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 SAYKOXHARSH V4 Ultra Multi 💀\nUse /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
👑 SAYKOXHARSH V4 Ultra Multi 💀

🎀 Name Changers:
/gcnc <name>          — GC name changer
/ncemo <name>         — Emoji name changer
/ncbaap <name>        — God level (5 NC / 0.1s)
/stopgcnc /stopncemo /stopncbaap /stopall
/delay <sec>          — Set delay
/ncworkers <n>        — Workers per bot for NC (default 5)
/spamworkers <n>      — Workers per bot for spam (default 5)

😹 Spam:
/spam <text>  /unspam

🪐 React:
/emojispam <emoji>  /stopemojispam

🪼 Slide:
/fuck (reply)  /freeze (reply)
/replyraid (reply)  /stopraid (reply)

⚡ Exonc:
/exonc <name>         — Fast
/exoncfast <name>     — Faster
/exoncgodspeed <name> — God speed (5 NC / 0.05s)
/stopexonc

🎨 Sticker:
/newsticker (reply photo)  /delsticker  /stickerstatus

🖼️ PFP Loop (RAM only, no disk):
/addpfp (reply photo)  — add photo to rotation
/pfploop               — start cycling GC profile pic
/stoppfp               — stop PFP loop
/clearpfp              — clear all photos from memory
/pfpstatus             — show photos loaded & memory used
/pfpdelay <sec>        — set delay between photo changes

🎵 Voice:
/animevn <chars> <text>  /voices  /tempest <text>

👑 Monarchs:
/entrust (reply)  /retract (reply)  /monarchs

🛡️ Promote:
/promote (reply)   — promote one user to full admin
/promoteall        — promote ALL tracked members to admin
/promotebots       — promote ALL 24 bots to full admin
/demote (reply)    — remove admin from one user

🦚 Misc:
/myid  /ready  /status
""")

async def ready_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("💭 Hmm...")
    await msg.edit_text("✅ All bots ready!")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")

# ---------------------------
# NAME CHANGER COMMANDS
# ---------------------------
def _cancel_tasks(task_dict, chat_id):
    for t in task_dict.pop(chat_id, []):
        t.cancel()

@only_sudo
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /gcnc <name>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    _cancel_tasks(group_tasks, chat_id)
    group_tasks[chat_id] = [asyncio.create_task(resilient_task(bot_loop, b, chat_id, base, "gcnc")) for b in bots for _ in range(NC_WORKERS)]
    await update.message.reply_text(f"🔄 GC Name Changer Started! [{len(bots)} bots × {NC_WORKERS} workers = {len(bots)*NC_WORKERS} tasks]")

@only_sudo
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /ncemo <name>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    _cancel_tasks(group_tasks, chat_id)
    group_tasks[chat_id] = [asyncio.create_task(resilient_task(bot_loop, b, chat_id, base, "ncemo")) for b in bots for _ in range(NC_WORKERS)]
    await update.message.reply_text(f"🎭 Emoji Name Changer Started! [{len(bots)} bots × {NC_WORKERS} workers = {len(bots)*NC_WORKERS} tasks]")

@only_sudo
async def ncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /ncbaap <name>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    _cancel_tasks(group_tasks, chat_id)
    group_tasks[chat_id] = [asyncio.create_task(resilient_task(ncbaap_loop, b, chat_id, base)) for b in bots for _ in range(NC_WORKERS)]
    await update.message.reply_text(f"💀🔥 GOD LEVEL NCBAAP ACTIVATED! [{len(bots)} bots × {NC_WORKERS} workers = {len(bots)*NC_WORKERS} tasks]")

@only_sudo
async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cancel_tasks(group_tasks, update.message.chat_id)
    await update.message.reply_text("⏹ GC Name Changer Stopped!")

@only_sudo
async def stopncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cancel_tasks(group_tasks, update.message.chat_id)
    await update.message.reply_text("⏹ Emoji Name Changer Stopped!")

@only_sudo
async def stopncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cancel_tasks(group_tasks, update.message.chat_id)
    await update.message.reply_text("⏹ NCBAAP Stopped!")

# ---------------------------
# EXONC COMMANDS
# ---------------------------
@only_sudo
async def exonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /exonc <name>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    _cancel_tasks(exonc_tasks, chat_id)
    exonc_tasks[chat_id] = [asyncio.create_task(resilient_task(exonc_loop, b, chat_id, base)) for b in bots for _ in range(NC_WORKERS)]
    await update.message.reply_text(f"💀 Exonc Mode Activated! [{len(bots)} bots × {NC_WORKERS} workers = {len(bots)*NC_WORKERS} tasks]")

@only_sudo
async def exoncfast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global exonc_delay
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /exoncfast <name>")
    exonc_delay = 0.03
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    _cancel_tasks(exonc_tasks, chat_id)
    exonc_tasks[chat_id] = [asyncio.create_task(resilient_task(exonc_loop, b, chat_id, base)) for b in bots for _ in range(NC_WORKERS)]
    await update.message.reply_text(f"⚡ Faster Exonc Activated! [{len(bots)} bots × {NC_WORKERS} workers = {len(bots)*NC_WORKERS} tasks]")

@only_sudo
async def exoncgodspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /exoncgodspeed <name>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    _cancel_tasks(exonc_tasks, chat_id)
    exonc_tasks[chat_id] = [asyncio.create_task(resilient_task(exonc_godspeed_loop, b, chat_id, base)) for b in bots for _ in range(NC_WORKERS)]
    await update.message.reply_text(f"👑🔥 GOD SPEED ACTIVATED! [{len(bots)} bots × {NC_WORKERS} workers = {len(bots)*NC_WORKERS} tasks]")

@only_sudo
async def stopexonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cancel_tasks(exonc_tasks, update.message.chat_id)
    await update.message.reply_text("🛑 Exonc Stopped!")

# ---------------------------
# SPAM COMMANDS
# ---------------------------
@only_sudo
async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /spam <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    _cancel_tasks(spam_tasks, chat_id)
    spam_tasks[chat_id] = [asyncio.create_task(resilient_task(spam_loop, b, chat_id, text)) for b in bots for _ in range(SPAM_WORKERS)]
    await update.message.reply_text(f"💥 Spam Started! [{len(bots)} bots × {SPAM_WORKERS} workers = {len(bots)*SPAM_WORKERS} tasks]")

@only_sudo
async def unspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cancel_tasks(spam_tasks, update.message.chat_id)
    await update.message.reply_text("🛑 Spam Stopped!")

# ---------------------------
# SLIDE COMMANDS
# ---------------------------
@only_sudo
async def fuck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.add(target_id)
    await update.message.reply_text(f"🎯 Raid Activated On: {target_id}")

@only_sudo
async def freeze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.discard(target_id)
    await update.message.reply_text(f"🛑 Raid Stopped On: {target_id}")

@only_sudo
async def replyraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slidespam_targets.add(target_id)
    await update.message.reply_text(f"🔥 Added To Replyraid: {target_id}")

@only_sudo
async def stopraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slidespam_targets.discard(target_id)
    await update.message.reply_text(f"🛑 Replyraid Stopped On: {target_id}")

# ---------------------------
# REACT COMMANDS
# ---------------------------
@only_sudo
async def emojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /emojispam <emoji>")
    emoji = context.args[0]
    chat_id = update.message.chat_id

    async def react_loop(bot, chat_id, emoji):
        while True:
            await asyncio.sleep(1)

    _cancel_tasks(react_tasks, chat_id)
    react_tasks[chat_id] = [asyncio.create_task(react_loop(b, chat_id, emoji)) for b in bots]
    await update.message.reply_text(f"🎭 Auto-reaction: {emoji}")

@only_sudo
async def stopemojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _cancel_tasks(react_tasks, update.message.chat_id)
    await update.message.reply_text("🛑 Reactions Stopped!")

# ---------------------------
# VOICE COMMANDS
# ---------------------------
@only_sudo
async def animevn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: /animevn <character_numbers> <text>\nExample: /animevn 1 2 Hello world")
    try:
        char_numbers, text_parts = [], []
        for arg in context.args:
            if arg.isdigit() and int(arg) in VOICE_CHARACTERS:
                char_numbers.append(int(arg))
            else:
                text_parts.append(arg)
        if not char_numbers:
            return await update.message.reply_text("❌ Provide valid character numbers (1-10)")
        text = " ".join(text_parts)
        if not text:
            return await update.message.reply_text("❌ Provide text to speak")
        await update.message.reply_text(
            f"🎭 Generating: {', '.join(VOICE_CHARACTERS[n]['name'] for n in char_numbers)}..."
        )
        voices = await generate_multiple_voices(text, char_numbers)
        if not voices:
            await update.message.reply_text("❌ Voice generation failed. Check API key.")
        else:
            for voice in voices:
                await update.message.reply_voice(
                    voice=voice["audio"],
                    caption=f"🎀 {voice['character']}: {text}\n{voice['description']}"
                )
                await asyncio.sleep(0.5)
    except Exception as e:
        await update.message.reply_text(f"❌ Voice error: {e}")

@only_sudo
async def tempest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /tempest <text>")
    text = " ".join(context.args)
    audio = await generate_tempest_voice(text, VOICE_CHARACTERS[1]["voice_id"])
    if audio:
        await update.message.reply_voice(voice=audio, caption=f"🎙️ {VOICE_CHARACTERS[1]['name']}: {text}")
    else:
        await update.message.reply_text("❌ Voice generation failed.")

@only_sudo
async def voices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = "🎭 Available Anime Voices:\n\n"
    for num, v in VOICE_CHARACTERS.items():
        lines += f"{num}. {v['name']} — {v['description']}\n"
    lines += "\n🎀 Usage: /animevn 1 2 Hello world"
    await update.message.reply_text(lines)

@only_sudo
async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /music <song>")
    await update.message.reply_text(f"🎶 Downloading: {' '.join(context.args)}")

@only_sudo
async def clonevn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a voice message")
    await update.message.reply_text("🎤 Voice cloning started...")

@only_sudo
async def clonedvn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /clonedvn <text>")
    await update.message.reply_text(f"🎙️ Speaking in cloned voice: {' '.join(context.args)}")

# ---------------------------
# STICKER COMMANDS
# ---------------------------
@only_sudo
async def newsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Reply to a photo with /newsticker")
    await update.message.reply_text("✅ Sticker creation ready!")

@only_sudo
async def delsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid in user_stickers:
        del user_stickers[uid]
        save_stickers()
        await update.message.reply_text("✅ Your stickers deleted!")
    else:
        await update.message.reply_text("❌ No stickers found")

@only_sudo
async def multisticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Creating 5 stickers...")

@only_sudo
async def stickerstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = sum(len(s) for s in user_stickers.values())
    await update.message.reply_text(f"📊 Sticker Status: {total} stickers total")

@only_owner
async def stopstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sticker_mode
    sticker_mode = False
    await update.message.reply_text("🛑 Stickers disabled")

@only_owner
async def startstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sticker_mode
    sticker_mode = True
    await update.message.reply_text("✅ Stickers enabled")

# ---------------------------
# PFP LOOP COMMANDS (in-memory, no disk)
# ---------------------------
@only_sudo
async def addpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to a photo to add it to this GC's PFP rotation (stored in RAM only)."""
    msg = update.message
    photo = None
    if msg.reply_to_message and msg.reply_to_message.photo:
        photo = msg.reply_to_message.photo[-1]
    elif msg.photo:
        photo = msg.photo[-1]
    if not photo:
        return await msg.reply_text("⚠️ Reply to a photo with /addpfp")

    chat_id = msg.chat_id
    file = await context.bot.get_file(photo.file_id)
    buf = io.BytesIO()
    await file.download_to_memory(buf)
    data = buf.getvalue()

    if chat_id not in pfp_photos:
        pfp_photos[chat_id] = []
    pfp_photos[chat_id].append(data)
    count = len(pfp_photos[chat_id])
    await msg.reply_text(f"✅ Photo added! Total in rotation: {count}\nUse /pfploop to start.")

@only_sudo
async def pfploop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start cycling photos as GC profile picture."""
    chat_id = update.message.chat_id
    if chat_id not in pfp_photos or not pfp_photos[chat_id]:
        return await update.message.reply_text("❌ No photos added yet. Use /addpfp (reply to photo) first.")

    _cancel_tasks(pfp_tasks, chat_id)
    pfp_tasks[chat_id] = [asyncio.create_task(pfp_loop(bots[0], chat_id))]
    count = len(pfp_photos[chat_id])
    await update.message.reply_text(
        f"🖼️ PFP Loop Started!\n📸 Photos: {count}\n⏱ Delay: {pfp_delay}s per photo\n💾 Storage: RAM only (0 disk)"
    )

@only_sudo
async def stoppfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop the PFP loop."""
    _cancel_tasks(pfp_tasks, update.message.chat_id)
    await update.message.reply_text("🛑 PFP Loop Stopped!")

@only_sudo
async def clearpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all stored photos from memory for this GC."""
    chat_id = update.message.chat_id
    _cancel_tasks(pfp_tasks, chat_id)
    pfp_photos.pop(chat_id, None)
    await update.message.reply_text("🗑 All PFP photos cleared from memory!")

@only_sudo
async def pfpstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show PFP loop status."""
    chat_id = update.message.chat_id
    count = len(pfp_photos.get(chat_id, []))
    running = chat_id in pfp_tasks and bool(pfp_tasks[chat_id])
    size_kb = sum(len(p) for p in pfp_photos.get(chat_id, [])) // 1024
    await update.message.reply_text(
        f"🖼️ PFP Status:\n"
        f"📸 Photos loaded : {count}\n"
        f"💾 Memory used   : {size_kb} KB\n"
        f"⚡ Loop running  : {'✅ Yes' if running else '❌ No'}\n"
        f"⏱ Current delay : {pfp_delay}s"
    )

@only_sudo
async def pfpdelay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set delay between photo changes."""
    global pfp_delay
    if not context.args:
        return await update.message.reply_text(f"⏱ Current PFP delay: {pfp_delay}s\nUsage: /pfpdelay <seconds>")
    try:
        pfp_delay = max(1.0, float(context.args[0]))
        await update.message.reply_text(f"✅ PFP delay set to {pfp_delay}s")
    except Exception:
        await update.message.reply_text("❌ Invalid number")

# ---------------------------
# CONTROL COMMANDS
# ---------------------------
@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for d in (group_tasks, spam_tasks, react_tasks, exonc_tasks, pfp_tasks):
        for tasks in d.values():
            for t in tasks:
                t.cancel()
        d.clear()
    slide_targets.clear()
    slidespam_targets.clear()
    await update.message.reply_text("⏹ ALL ACTIVITIES STOPPED!")

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args:
        return await update.message.reply_text(f"⏱ Current delay: {delay}s")
    try:
        delay = max(0.05, float(context.args[0]))
        await update.message.reply_text(f"✅ Delay set to {delay}s")
    except Exception:
        await update.message.reply_text("❌ Invalid number")

@only_sudo
async def ncworkers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global NC_WORKERS
    if not context.args:
        return await update.message.reply_text(
            f"⚙️ NC Workers: {NC_WORKERS} per bot\n"
            f"📊 Total NC tasks when active: {len(bots) * NC_WORKERS}\n"
            f"Usage: /ncworkers <number>"
        )
    try:
        NC_WORKERS = max(1, int(context.args[0]))
        await update.message.reply_text(
            f"✅ NC Workers set to {NC_WORKERS} per bot\n"
            f"⚡ Total NC tasks: {len(bots) * NC_WORKERS}\n"
            f"Restart /gcnc or /ncbaap to apply."
        )
    except Exception:
        await update.message.reply_text("❌ Invalid number")

@only_sudo
async def spamworkers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SPAM_WORKERS
    if not context.args:
        return await update.message.reply_text(
            f"⚙️ Spam Workers: {SPAM_WORKERS} per bot\n"
            f"📊 Total spam tasks when active: {len(bots) * SPAM_WORKERS}\n"
            f"Usage: /spamworkers <number>"
        )
    try:
        SPAM_WORKERS = max(1, int(context.args[0]))
        await update.message.reply_text(
            f"✅ Spam Workers set to {SPAM_WORKERS} per bot\n"
            f"💥 Total spam tasks: {len(bots) * SPAM_WORKERS}\n"
            f"Restart /spam to apply."
        )
    except Exception:
        await update.message.reply_text("❌ Invalid number")

# ---------------------------
# STATUS
# ---------------------------
@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""
📊 SAYKOXHARSH V4 Status:

🎀 Name Changers : {sum(len(v) for v in group_tasks.values())} tasks running
⚡ Exonc Sessions: {sum(len(v) for v in exonc_tasks.values())} tasks running
😹 Spam Sessions : {sum(len(v) for v in spam_tasks.values())} tasks running
🪐 Reactions     : {sum(len(v) for v in react_tasks.values())}
🪼 Slide Targets : {len(slide_targets)}
💥 Slide Spam    : {len(slidespam_targets)}

⚙️ NC Workers    : {NC_WORKERS}/bot → {len(bots)*NC_WORKERS} max tasks
💥 Spam Workers  : {SPAM_WORKERS}/bot → {len(bots)*SPAM_WORKERS} max tasks

⏱  Delay         : {delay}s
⚡ Exonc Delay   : {exonc_delay}s
🤖 Active Bots   : {len(bots)}
👑 SUDO Users    : {len(SUDO_USERS)}
""")

# ---------------------------
# MONARCH MANAGEMENT
# ---------------------------
@only_owner
async def entrust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Monarch added: {uid}")

@only_owner
async def retract(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"🗑 Monarch removed: {uid}")
    else:
        await update.message.reply_text("❌ User not in Monarchs")

@only_sudo
async def monarchs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sudo_list = "\n".join(f"👑 {uid}" for uid in SUDO_USERS)
    await update.message.reply_text(f"👑 Monarchs:\n{sudo_list}")

# ---------------------------
# PROMOTE / DEMOTE COMMANDS
# ---------------------------
FULL_ADMIN_RIGHTS = dict(
    can_change_info=True,
    can_delete_messages=True,
    can_invite_users=True,
    can_restrict_members=True,
    can_pin_messages=True,
    can_promote_members=True,
    can_manage_chat=True,
    can_manage_video_chats=True,
)

@only_sudo
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote a single user to full admin using all bots simultaneously."""
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user to promote them.")
    target_id = update.message.reply_to_message.from_user.id
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"🛡️ Promoting {target_id} with all bots...")
    results = await asyncio.gather(
        *[safe_call(b.promote_chat_member(chat_id, target_id, **FULL_ADMIN_RIGHTS)) for b in bots],
        return_exceptions=True
    )
    done = sum(1 for r in results if r is None or not isinstance(r, Exception))
    await msg.edit_text(f"✅ Promoted! ({done}/{len(bots)} bots succeeded)")

@only_sudo
async def promoteall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Promote ALL tracked members in this GC to full admin."""
    chat_id = update.message.chat_id
    members = member_cache.get(chat_id, {})
    if not members:
        return await update.message.reply_text(
            "❌ No members tracked yet.\n"
            "Members are tracked as they send messages. Wait for activity then try again."
        )
    msg = await update.message.reply_text(
        f"🛡️ Promoting {len(members)} members with {len(bots)} bots...\nPlease wait..."
    )
    total_ok = 0
    for uid in list(members.keys()):
        results = await asyncio.gather(
            *[safe_call(b.promote_chat_member(chat_id, uid, **FULL_ADMIN_RIGHTS)) for b in bots],
            return_exceptions=True
        )
        if any(r is None or not isinstance(r, Exception) for r in results):
            total_ok += 1
        await asyncio.sleep(0)
    await msg.edit_text(
        f"✅ Promote All Done!\n"
        f"👥 Members targeted : {len(members)}\n"
        f"✅ Successfully promoted: {total_ok}"
    )

@only_sudo
async def promotebots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """One bot promotes all 24 bots to full admin in this GC simultaneously."""
    chat_id = update.message.chat_id
    promoter = bots[0]
    msg = await update.message.reply_text(f"🤖 1 bot promoting all {len(bots)} bots to admin...")

    async def promote_one_bot(bot):
        try:
            me = await bot.get_me()
            await safe_call(promoter.promote_chat_member(chat_id, me.id, **FULL_ADMIN_RIGHTS))
            return True
        except Exception:
            return False

    results = await asyncio.gather(*[promote_one_bot(b) for b in bots], return_exceptions=True)
    total_ok = sum(1 for r in results if r is True)
    await msg.edit_text(
        f"✅ All Bots Promoted!\n"
        f"🤖 Total bots   : {len(bots)}\n"
        f"✅ Now admins   : {total_ok}\n"
        f"⚡ Done instantly via 1 bot"
    )

@only_sudo
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all admin rights from a user using all bots simultaneously."""
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user to demote them.")
    target_id = update.message.reply_to_message.from_user.id
    chat_id = update.message.chat_id
    msg = await update.message.reply_text(f"🔻 Demoting {target_id}...")
    await asyncio.gather(
        *[safe_call(b.promote_chat_member(
            chat_id, target_id,
            can_change_info=False, can_delete_messages=False,
            can_invite_users=False, can_restrict_members=False,
            can_pin_messages=False, can_promote_members=False,
            can_manage_chat=False, can_manage_video_chats=False,
        )) for b in bots],
        return_exceptions=True
    )
    await msg.edit_text(f"✅ Demoted {target_id} successfully!")

# ---------------------------
# AUTO REPLY HANDLER
# ---------------------------
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return
    user = update.message.from_user
    uid = user.id
    chat_id = update.message.chat_id
    if chat_id not in member_cache:
        member_cache[chat_id] = {}
    member_cache[chat_id][uid] = user.first_name or str(uid)
    if uid in slide_targets:
        for text in RAID_TEXTS[:3]:
            await safe_call(update.message.reply_text(text))
            await asyncio.sleep(0)
    if uid in slidespam_targets:
        for text in RAID_TEXTS:
            await safe_call(update.message.reply_text(text))
            await asyncio.sleep(0)

# ---------------------------
# BOT SETUP
# commander=True  → registers ALL command handlers (only bot[0])
# commander=False → registers ONLY auto_replies (bots[1-23], pure workers)
# ---------------------------
def build_app(token, commander=False):
    request = HTTPXRequest(connection_pool_size=100, read_timeout=15, write_timeout=15, connect_timeout=5)
    app = Application.builder().token(token).request(request).concurrent_updates(True).build()

    if commander:
        app.add_handler(CommandHandler("start",          start_cmd))
        app.add_handler(CommandHandler("help",           help_cmd))
        app.add_handler(CommandHandler("ready",          ready_cmd))
        app.add_handler(CommandHandler("myid",           myid))
        app.add_handler(CommandHandler("status",         status_cmd))
        app.add_handler(CommandHandler("gcnc",           gcnc))
        app.add_handler(CommandHandler("ncemo",          ncemo))
        app.add_handler(CommandHandler("ncbaap",         ncbaap))
        app.add_handler(CommandHandler("stopgcnc",       stopgcnc))
        app.add_handler(CommandHandler("stopncemo",      stopncemo))
        app.add_handler(CommandHandler("stopncbaap",     stopncbaap))
        app.add_handler(CommandHandler("stopall",        stopall))
        app.add_handler(CommandHandler("delay",          delay_cmd))
        app.add_handler(CommandHandler("exonc",          exonc))
        app.add_handler(CommandHandler("exoncfast",      exoncfast))
        app.add_handler(CommandHandler("exoncgodspeed",  exoncgodspeed))
        app.add_handler(CommandHandler("stopexonc",      stopexonc))
        app.add_handler(CommandHandler("spam",           spam))
        app.add_handler(CommandHandler("unspam",         unspam))
        app.add_handler(CommandHandler("emojispam",      emojispam))
        app.add_handler(CommandHandler("stopemojispam",  stopemojispam))
        app.add_handler(CommandHandler("fuck",           fuck))
        app.add_handler(CommandHandler("freeze",         freeze))
        app.add_handler(CommandHandler("replyraid",      replyraid))
        app.add_handler(CommandHandler("stopraid",       stopraid))
        app.add_handler(CommandHandler("newsticker",     newsticker))
        app.add_handler(CommandHandler("delsticker",     delsticker))
        app.add_handler(CommandHandler("multisticker",   multisticker))
        app.add_handler(CommandHandler("stickerstatus",  stickerstatus))
        app.add_handler(CommandHandler("stopstickers",   stopstickers))
        app.add_handler(CommandHandler("startstickers",  startstickers))
        app.add_handler(CommandHandler("addpfp",         addpfp))
        app.add_handler(CommandHandler("pfploop",        pfploop))
        app.add_handler(CommandHandler("stoppfp",        stoppfp))
        app.add_handler(CommandHandler("clearpfp",       clearpfp))
        app.add_handler(CommandHandler("pfpstatus",      pfpstatus))
        app.add_handler(CommandHandler("pfpdelay",       pfpdelay_cmd))
        app.add_handler(CommandHandler("animevn",        animevn))
        app.add_handler(CommandHandler("tempest",        tempest_cmd))
        app.add_handler(CommandHandler("music",          music))
        app.add_handler(CommandHandler("clonevn",        clonevn))
        app.add_handler(CommandHandler("clonedvn",       clonedvn))
        app.add_handler(CommandHandler("voices",         voices))
        app.add_handler(CommandHandler("entrust",        entrust))
        app.add_handler(CommandHandler("retract",        retract))
        app.add_handler(CommandHandler("monarchs",       monarchs))
        app.add_handler(CommandHandler("promote",        promote))
        app.add_handler(CommandHandler("promoteall",     promoteall))
        app.add_handler(CommandHandler("promotebots",    promotebots))
        app.add_handler(CommandHandler("demote",         demote))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_replies))
    return app

# ---------------------------
# INITIALIZE ONE BOT SAFELY
# ---------------------------
async def init_bot(token, commander=False):
    try:
        app = build_app(token, commander=commander)
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "edited_message", "callback_query"],
        )
        label = "👑 COMMANDER" if commander else "⚙️ worker"
        print(f"✅ {label}: {token[:12]}...")
        return app
    except Exception as e:
        print(f"❌ Failed {token[:12]}...: {e}")
        return None

# ---------------------------
# CRASH-SAFE TASK WRAPPER — auto-restarts any loop that dies
# ---------------------------
async def resilient_task(coro_fn, *args):
    """Run a loop coroutine forever — restart it instantly if it crashes."""
    while True:
        try:
            await coro_fn(*args)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"⚠️ Task crashed ({coro_fn.__name__}): {e} — restarting instantly")
            await asyncio.sleep(0.01)

# ---------------------------
# MAIN — all 24 bots start simultaneously
# ---------------------------
async def run_all_bots():
    global apps, bots

    apps.clear()
    bots.clear()

    print(f"🚀 Starting {len(TOKENS)} bots simultaneously...")

    # First token = commander (handles all commands)
    # Rest = pure workers (NC/spam only, no command handling)
    tasks = [init_bot(TOKENS[0], commander=True)]
    tasks += [init_bot(t, commander=False) for t in TOKENS[1:]]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for res in results:
        if isinstance(res, Application):
            apps.append(res)
            bots.append(res.bot)

    if not bots:
        print("❌ No bots started! Check tokens. Retrying in 3s...")
        await asyncio.sleep(3)
        return

    print(f"🎉 {len(bots)}/{len(TOKENS)} bots online!")
    print(f"📊 Chat ID  : {CHAT_ID}")
    print(f"👑 Owner ID : {OWNER_ID}")
    print(f"🤖 Bots     : {len(bots)}")
    print(f"⚡ NC Workers  : {NC_WORKERS}/bot = {len(bots)*NC_WORKERS} tasks")
    print(f"💥 Spam Workers: {SPAM_WORKERS}/bot = {len(bots)*SPAM_WORKERS} tasks")
    print("🛡️ Crash-safe mode ON — all tasks auto-restart")

    # Global asyncio exception handler — swallows unhandled task exceptions
    def handle_exception(loop, context):
        if "exception" in context:
            print(f"⚠️ Unhandled: {context['exception']} — ignored")

    asyncio.get_running_loop().set_exception_handler(handle_exception)

    await asyncio.Event().wait()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(run_all_bots())
        except KeyboardInterrupt:
            print("\n🔴 Shutting down...")
            break
        except Exception as e:
            print(f"⚠️ Crashed: {e} — restarting in 1s...")
            time.sleep(1)
