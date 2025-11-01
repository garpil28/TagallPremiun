import os
from dotenv import load_dotenv

# load .env biar semua data penting diambil otomatis
load_dotenv()

# 🔰 Data dasar bot
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_NAME = os.getenv("BOT_NAME", "GarfieldTagall")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "").split()] if os.getenv("OWNER_IDS") else []
OWNER_NAME = os.getenv("OWNER_NAME", "kopi567")

# 🔰 Log & identitas
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", 0))
STORE_LINK = os.getenv("TAG_FOOTER_LINK", "https://t.me/storegarf")

# 🔰 Database
MONGO_URL = os.getenv("MONGO_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")

# 🔰 Broadcast
BROADCAST_DELAY = int(os.getenv("BROADCAST_DELAY", 2))
BROADCAST_CHUNK = int(os.getenv("BROADCAST_CHUNK", 50))

# 🔰 TagAll config
TAG_BATCH_SIZE = int(os.getenv("TAG_BATCH_SIZE", 5))
TAG_DELAY = int(os.getenv("TAG_DELAY", 5))
TAG_INTERVAL = int(os.getenv("TAG_INTERVAL", 300))

# 🔰 Fitur AI & Auto Reply
ENABLE_AUTOREPLY = os.getenv("ENABLE_AUTOREPLY", "True").lower() == "true"

# 🔰 Fitur SangMata (deteksi ganti nama user)
ENABLE_SANGMATA = os.getenv("ENABLE_SANGMATA", "True").lower() == "true"
SANGMATA_LOG_ID = int(os.getenv("SANGMATA_LOG_ID", 0))

# 🔰 Durasi Tagall (biar ga spam)
MAX_PARTNER_DURATION = int(os.getenv("MAX_PARTNER_DURATION", 300))
MAX_NONPARTNER_DURATION = int(os.getenv("MAX_NONPARTNER_DURATION", 120))

# 🔰 Info versi
VERSION = "GarfieldBot PRO MAX+"
DEVELOPER = "kopi567"
