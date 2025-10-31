import os
from dotenv import load_dotenv

load_dotenv()

# ===== BOT CONFIG =====
BOT_NAME = "AutoTagAll Premium"
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== OWNER CONFIG =====
OWNER_NAME = "kopi567"
OWNER_USERNAME = "kopi567"
OWNER_IDS = [6954401932, 5727852338]

# ===== LOG CONFIG =====
LOGS_CHAT_ID = -1003282574590
LOG_FILE_NAME = "BotTagallGarfieldLogs.txt"

# ===== SUPPORT & CHANNEL =====
SUPPORT_GROUP = "https://t.me/garfieldoffc"
UPDATES_CHANNEL = "storegarf"
BANNER_IMG_URL = "https://files.catbox.moe/vcdo1g.jpg"

# ===== TIMEZONE CONFIG =====
TIMEZONE = "Asia/Jakarta"  # WIB (GMT+7)

# ===== DATABASE CONFIG =====
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
)

# ===== API CONFIG =====
API_ID = int(os.getenv("API_ID", "20186947"))
API_HASH = os.getenv("API_HASH", "033defc8a75d858d76870f65f947d130")

# ===== EFFECTS ID (jangan ubah kecuali mau ubah efek stiker) =====
EFFECT_IDS = {
    "THUMB": 5107584321108051014,
    "NOOB": 5104858069142078462,
    "LOVE": 5159385139981059251,
    "FIRE": 5104841245755180586,
    "PARTY": 5046509860389126442,
    "POOP": 5046589136895476101,
}
