# main.py — GarfieldBot Maxx Full System (Auto Restart + Error Report)
import asyncio
import time
import traceback
from pyrogram import Client
from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    LOG_CHANNEL,
    BOT_NAME,
    OWNER_ID,
    AUTO_RESTART_HOUR,
    AUTO_RESTART_MINUTE,
)
from datetime import datetime, timedelta
import os

# Waktu restart otomatis
RESTART_INTERVAL = timedelta(hours=AUTO_RESTART_HOUR, minutes=AUTO_RESTART_MINUTE)

async def start_bot():
    """Menjalankan GarfieldBot dan menjaga uptime."""
    from __init__ import GarfieldBot

    start_time = datetime.now()
    await GarfieldBot.start()
    await GarfieldBot.send_message(
        LOG_CHANNEL,
        f"✅ **{BOT_NAME} aktif!**\n🕐 {datetime.now().strftime('%H:%M:%S %d-%m-%Y')}\n👑 Owner ID: `{OWNER_ID}`",
    )
    print(f"🦊 {BOT_NAME} aktif dan berjalan...")

    try:
        while True:
            await asyncio.sleep(60)
            elapsed = datetime.now() - start_time
            if elapsed >= RESTART_INTERVAL:
                await GarfieldBot.send_message(
                    LOG_CHANNEL,
                    f"♻️ **{BOT_NAME} Restart Otomatis** setelah {elapsed.seconds//3600} jam.",
                )
                await GarfieldBot.stop()
                os.execv(sys.executable, ['python3'] + sys.argv)
    except Exception as e:
        err = traceback.format_exc()
        await GarfieldBot.send_message(
            LOG_CHANNEL,
            f"❌ **{BOT_NAME} Error!**\n\n`{e}`\n\n```{err}```",
        )
        print(f"[ERROR] {e}")
        await GarfieldBot.stop()
        time.sleep(5)
        os.execv(sys.executable, ['python3'] + sys.argv)

if __name__ == "__main__":
    asyncio.run(start_bot())
