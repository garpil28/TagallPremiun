# __init__.py — GarfieldBot Full Loader
# Pastikan semua modul berada di folder yang sama (auto_tagall.py, menu_user.py, config.py, emoji_list.py)

import logging
from pyrogram import Client
from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    BOT_NAME,
    LOG_CHANNEL,
)

# === setup logging ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === inisialisasi bot utama ===
GarfieldBot = Client(
    "GarfieldBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")  # folder plugins (auto_tagall.py, menu_user.py, dll)
)

if __name__ == "__main__":
    print(f"🦊 {BOT_NAME} sedang memulai...")
    GarfieldBot.run()
