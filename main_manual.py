import asyncio
from pyrogram import Client, filters
from config import *

app = Client("autotagall_manual", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DURASI = {
    "3": 180,
    "5": 300,
    "10": 600,
    "20": 1200,
    "30": 1800,
    "60": 3600,
    "90": 5400,
    "120": 7200,
    "unlimited": None
}

@app.on_message(filters.command("tagall") & filters.group)
async def manual_tagall(_, message):
    if not message.from_user:
        return
    member = message.from_user
    if not (member.id in OWNER_IDS or member.status in ["creator", "administrator"]):
        return await message.reply("❌ Hanya admin yang bisa menjalankan manual tagall.")

    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Gunakan format:\n/tagall <durasi>\nContoh: /tagall 5 untuk 5 menit.")

    durasi = args[1]
    if durasi not in DURASI:
        return await message.reply("Durasi tidak valid. Pilih antara 3, 5, 10, 20, 30, 60, 90, 120, atau unlimited.")

    waktu = DURASI[durasi]
    await message.reply(f"✅ Manual Tagall dimulai ({durasi} menit)...")

    members = []
    async for m in app.get_chat_members(message.chat.id):
        if not m.user.is_bot:
            members.append(m.user.mention)

    text = " ".join(members)
    chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]
    for chunk in chunks:
        await message.reply(chunk)
        await asyncio.sleep(5)

    if waktu:
        await asyncio.sleep(waktu)
        await message.reply("✅ Durasi tagall selesai.")
    else:
        await message.reply("♾️ Tagall unlimited aktif sampai bot dihentikan manual.")

print("🚀 Manual TagAll siap dijalankan...")
app.run()
