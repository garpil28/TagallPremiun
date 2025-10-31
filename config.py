# config.py — Garfield AutoTagAll (env-based)
import os
from dotenv import load_dotenv

load_dotenv()

# ----- BOT / API -----
BOT_NAME = os.getenv("BOT_NAME", "Garfield Bot Tagall")
API_ID = int(os.getenv("API_ID", "0"))            # GANTI: API_ID dari my.telegram.org
API_HASH = os.getenv("API_HASH", "")              # GANTI: API_HASH dari my.telegram.org
BOT_TOKEN = os.getenv("BOT_TOKEN", "")            # GANTI: token dari @BotFather

# ----- OWNER -----
OWNER_NAME = os.getenv("OWNER_NAME", "kopi567")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "kopi567")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "6954401932 5727852338").split()]

# ----- LOG / SUPPORT -----
LOGS_CHAT_ID = int(os.getenv("LOGS_CHAT_ID", "-1003282574590"))
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "BotTagallGarfieldLogs.txt")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/garfieldoffc")
UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL", "storegarf")
BANNER_IMG_URL = os.getenv("BANNER_IMG_URL", "https://files.catbox.moe/vcdo1g.jpg")

# ----- MONGO -----
DATABASE_URL = os.getenv("DATABASE_URL", "")     # GANTI: MongoDB Atlas URI
DATABASE_NAME = os.getenv("DATABASE_NAME", "garfield_tagall")

# ----- TIME/ZONES -----
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

# ----- EFFECTS (optional) -----
EFFECT_IDS = {
    "THUMB": 5107584321108051014,
    "NOOB": 5104858069142078462,
    "LOVE": 5159385139981059251,
    "FIRE": 5104841245755180586,
    "PARTY": 5046509860389126442,
    "POOP": 5046589136895476101,
}
