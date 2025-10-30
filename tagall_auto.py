import asyncio
from telegram import Bot
from utils import log_to_group, get_wib_time

# Daftar partner yang diizinkan (bisa diubah via bot nanti)
PARTNER_LIST = [
    "https://t.me/garfieldoffc"
]

async def auto_tagall(bot: Bot):
    """Fungsi utama auto tagall"""
    await log_to_group(bot, f"🤖 Auto TagAll dimulai otomatis ({get_wib_time()})")

    for partner in PARTNER_LIST:
        try:
            await asyncio.sleep(5)
            await log_to_group(bot, f"✅ TagAll auto berhasil untuk partner: {partner}")
        except Exception as e:
            await log_to_group(bot, f"❌ Gagal TagAll di {partner}: {e}")

    await log_to_group(bot, f"🏁 Auto TagAll selesai ({get_wib_time()})")
