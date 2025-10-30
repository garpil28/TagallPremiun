import logging
from datetime import datetime, timezone, timedelta
from telegram import Bot
from config import LOGS_CHAT_ID, LOG_FILE_NAME, TIMEZONE

# Konfigurasi logging ke file
logging.basicConfig(
    filename=LOG_FILE_NAME,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def get_wib_time():
    """Ambil waktu lokal WIB (UTC+7)."""
    wib = timezone(timedelta(hours=7))
    return datetime.now(wib).strftime("%Y-%m-%d %H:%M:%S")

async def log_to_group(bot: Bot, text: str):
    """Kirim log ke grup LOGS_CHAT_ID dan tulis di file."""
    try:
        logging.info(text)
        await bot.send_message(chat_id=LOGS_CHAT_ID, text=f"🪵 [LOGS]\n{text}")
    except Exception as e:
        print(f"Gagal kirim log: {e}")
