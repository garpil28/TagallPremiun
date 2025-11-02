# config.py — GarfieldBot PRO MAX+
import os
from dotenv import load_dotenv

# 🧩 Load .env agar semua data penting otomatis diambil
load_dotenv()

# === 🔰 DATA DASAR BOT ===
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_NAME = os.getenv("BOT_NAME", "GarfieldTagall")
OWNER_IDS = [int(x) for x in os.getenv("OWNER_IDS", "").split()] if os.getenv("OWNER_IDS") else []
OWNER_NAME = os.getenv("OWNER_NAME", "kopi567")

# === 🔰 LOG & IDENTITAS ===
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", 0))

# === 🔰 DATABASE ===
MONGO_URL = os.getenv("MONGO_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")

# === 🔰 BROADCAST ===
BROADCAST_DELAY = int(os.getenv("BROADCAST_DELAY", 2))
BROADCAST_CHUNK = int(os.getenv("BROADCAST_CHUNK", 50))

# === 🔰 TAGALL CONFIG ===
TAG_BATCH_SIZE = int(os.getenv("TAG_BATCH_SIZE", 5))  # jumlah user per batch
TAG_DELAY = int(os.getenv("TAG_DELAY", 5))  # jeda antar batch
TAG_INTERVAL = int(os.getenv("TAG_INTERVAL", 300))  # delay antar tag otomatis

# === 🔰 FITUR AI & AUTO REPLY ===
ENABLE_AUTOREPLY = os.getenv("ENABLE_AUTOREPLY", "True").lower() == "true"

# === 🔰 FITUR SANGMATA ===
ENABLE_SANGMATA = os.getenv("ENABLE_SANGMATA", "True").lower() == "true"
SANGMATA_LOG_ID = int(os.getenv("SANGMATA_LOG_ID", 0))

# === 🔰 DURASI TAGALL (BIAR GA SPAM) ===
MAX_PARTNER_DURATION = int(os.getenv("MAX_PARTNER_DURATION", 300))  # partner = 5 menit
MAX_NONPARTNER_DURATION = int(os.getenv("MAX_NONPARTNER_DURATION", 120))  # non partner = 2 menit

# === 🔰 INFO VERSI ===
VERSION = "GarfieldBot PRO MAX+"
DEVELOPER = "kopi567"

# === 🔰 REPO INFO ===
REPO_URL = "https://github.com/garpil28/TagallPremiun"

# === 🔰 AUTO RESTART SETTING ===
AUTO_RESTART_HOUR = int(os.getenv("AUTO_RESTART_HOUR", "24"))  # restart tiap 24 jam
AUTO_RESTART_MINUTE = int(os.getenv("AUTO_RESTART_MINUTE", "0"))

# === 🔰 VARIABEL OPSIONAL ===
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ["true", "1", "yes"]

# === 🔰 CHANNEL & GROUP SUPPORT ===
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/garfieldoffc")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/galeriorng41")
STORE_LINK = os.getenv("STORE_LINK", "https://t.me/storegarf")

# === 🔰 PRINT INFO KE CONSOLE ===
print(f"[✅] Config loaded successfully for {BOT_NAME} (Owner: {OWNER_NAME}) — Version {VERSION}")
