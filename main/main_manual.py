import asyncio
from pyrogram import Client, filters
from config import CBOT, COWNER

bot = Client(
    "GarfieldManual",
    api_id=CBOT.API_ID,
    api_hash=CBOT.API_HASH,
    bot_token=CBOT.BOT_TOKEN,
)

DURATIONS = {
    "3m": 180,
    "5m": 300,
    "10m": 600,
    "20m": 1200,
    "30m": 1800,
    "60m": 3600,
    "90m": 5400,
    "120m": 7200,
    "unlimited": None,
}

@bot.on_message(filters.command("manual") & filters.user(COWNER.OWNER_IDS))
async def manual_tagall(client, message):
    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            return await message.reply_text(
                "Gunakan format:\n/manual <durasi> <pesan>\n\nContoh: /manual 10m Halo semua!"
            )
        duration_key = parts[1].lower()
        text = parts[2]

        if duration_key not in DURATIONS:
            return await message.reply_text("Durasi tidak valid!")

        members = [m async for m in client.get_chat_members(message.chat.id)]
        delay = DURATIONS[duration_key]

        await message.reply_text(f"🔔 Mulai menandai {len(members)} anggota selama {duration_key}...")

        count = 0
        for m in members:
            if not m.user or m.user.is_bot:
                continue
            try:
                await message.reply_text(f"{text} [{m.user.first_name}](tg://user?id={m.user.id})", disable_web_page_preview=True)
                count += 1
                await asyncio.sleep(2)
            except Exception:
                continue

            if delay and count * 2 >= delay:
                break

        await message.reply_text(f"✅ TagAll selesai! Total {count} anggota ditandai.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

bot.run()
