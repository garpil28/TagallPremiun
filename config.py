import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

HELP_COMMANDS = {}
ACTIVE_LIVECHATS = {}
BROADCAST_STATUS = {}
PENDING_MENTIONS = {}
SHUTDOWN_EVENT = asyncio.Event()
SPAM_CHATS = []

BOT_NAME = os.getenv("BOT_NAME", "Garfield TagAllBot")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

OWNER_NAME = os.getenv("OWNER_NAME", "")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "0").split()]

LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-100"))
DATABASE_URL = os.getenv("DATABASE_URL", "")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

class CBOT:
    API_ID = API_ID
    API_HASH = API_HASH
    BOT_TOKEN = BOT_TOKEN
    BOT_NAME = BOT_NAME
    LOG_GROUP_ID = LOG_GROUP_ID
    DATABASE_URL = DATABASE_URL

class COWNER:
    OWNER_NAME = OWNER_NAME
    OWNER_USERNAME = OWNER_USERNAME
    OWNER_IDS = OWNER_IDS

print(f"[✅] Config loaded for {BOT_NAME}")
print(f"[🧠] Owner: {OWNER_NAME} ({OWNER_USERNAME})")
print(f"[💾] MongoDB connected via {DATABASE_URL[:40]}...")
