import asyncio
from telethon import TelegramClient, events
from config import *

api_id = 12345678   # Ganti dgn API ID kamu
api_hash = "your_api_hash_here"
bot = TelegramClient("manual_tag_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/manualtag"))
async def manualtag(event):
    if not event.is_group:
        return await event.reply("❌ Gunakan di grup.")
    try:
        args = event.raw_text.split()
        if len(args) < 3:
            return await event.reply("⚠️ Format salah.\nGunakan: /manualtag [durasi_menit/unlimited] Pesan")
        durasi = args[1].lower()
        pesan = " ".join(args[2:])
        members = await bot.get_participants(event.chat_id)
        taglist = " ".join([f"[{m.first_name}](tg://user?id={m.id})" for m in members])

        await event.respond(f"🚀 Tagall dimulai.\nDurasi: {durasi} menit.\nPesan:\n{pesan}")
        await event.respond(taglist)

        if durasi != "unlimited":
            waktu = int(durasi)
            await asyncio.sleep(waktu * 60)
            await event.respond("✅ Tagall selesai otomatis.")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")

print("✅ Manual TagAll aktif (24 jam)")
bot.run_until_disconnected()
