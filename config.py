import os
import asyncio
from dotenv import load_dotenv

# ==== Load dari file .env ====
load_dotenv()

# ==== Variabel umum ====
HELP_COMMANDS = {}
ACTIVE_LIVECHATS = {}
BROADCAST_STATUS = {}
PENDING_MENTIONS = {}
SHUTDOWN_EVENT = asyncio.Event()
SPAM_CHATS = []

# ==== Efek Mention (biarkan saja, untuk variasi animasi tagall) ====
EFFECT_IDS = {
    "THUMB": 5107584321108051014,
    "NOOB": 5104858069142078462,
    "LOVE": 5159385139981059251,
    "FIRE": 5104841245755180586,
    "PARTY": 5046509860389126442,
    "POOP": 5046589136895476101,
}

# ==== Konfigurasi dari .env ====
BOT_NAME = os.getenv("BOT_NAME", "Garfield Protect")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
APP_VERSION = os.getenv("APP_VERSION", "v1.0")

OWNER_NAME = os.getenv("OWNER_NAME", "kopi567")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "kopi567")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "0").split()]

LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "BotTagallGarfieldLogs.txt")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1003282574590"))

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "")
UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL", "")
BANNER_IMG_URL = os.getenv("BANNER_IMG_URL", "")

DATABASE_URL = os.getenv("DATABASE_URL", "")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

GEMINI_API = os.getenv("GEMINI_API", "")

# ==== Kelas Pendukung ====
class CBOT:
    API_ID = API_ID
    API_HASH = API_HASH
    BOT_TOKEN = BOT_TOKEN
    BOT_NAME = BOT_NAME
    LOG_FILE_NAME = LOG_FILE_NAME
    LOG_GROUP_ID = LOG_GROUP_ID
    BANNER_IMG_URL = BANNER_IMG_URL
    GEMINI_API = GEMINI_API
    SUPPORT_GROUP = SUPPORT_GROUP
    UPDATES_CHANNEL = UPDATES_CHANNEL


class COWNER:
    OWNER_NAME = OWNER_NAME
    OWNER_USERNAME = OWNER_USERNAME
    OWNER_IDS = OWNER_IDS


class CDATABASE:
    DATABASE_URL = DATABASE_URL


# ==== Print konfirmasi ke log ====
print(f"[✅] Config loaded successfully for bot: {BOT_NAME}")
print(f"[🧠] Owner: {OWNER_NAME} ({OWNER_USERNAME})")
print(f"[💾] MongoDB: Connected via {DATABASE_URL[:40]}...")
