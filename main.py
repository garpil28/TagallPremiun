import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient
from config import *

app = Client(
    "GarfieldTagAllBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

mongo = MongoClient(DATABASE_URL)
db = mongo["garfield_tagall"]
premium_users = db["premium_users"]

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

@app.on_message(filters.command(["start", "help"]))
async def start_help(_, message):
    text = (
        "🤖 Garfield TagAllBot\n"
        "Bot ini bisa melakukan TagAll secara manual atau otomatis.\n\n"
        "📌 Perintah Admin:\n"
        "/tagall <durasi> — Tagall manual.\n"
        "Durasi: 3, 5, 10, 20, 30, 60, 90, 120, unlimited\n\n"
        "👑 Owner Commands:\n"
        "/addprem <user_id> — Tambah user premium.\n"
        "/delprem <user_id> — Hapus user premium.\n\n"
        "💎 Premium Users:\n"
        "Kirim pesan ke grup, bot akan otomatis menandai semua member selama 5 menit."
    )
    await message.reply_text(text)

@app.on_message(filters.command("tagall") & filters.group)
async def manual_tagall(_, message):
    if not message.from_user:
        return
    user = message.from_user
    admins = [a.user.id async for a in app.get_chat_members(message.chat.id, filter="administrators")]
    if user.id not in admins and user.id not in OWNER_IDS:
        return await message.reply("❌ Hanya admin atau owner yang bisa menjalankan TagAll manual.")

    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Gunakan format:\n/tagall <durasi>\nContoh: /tagall 5")

    durasi = args[1]
    if durasi not in DURASI:
        return await message.reply("Durasi tidak valid. Pilih: 3, 5, 10, 20, 30, 60, 90, 120, unlimited.")

    waktu = DURASI[durasi]
    await message.reply(f"✅ Manual TagAll dimulai ({durasi} menit)...")

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
        await message.reply("✅ Durasi TagAll selesai.")
    else:
        await message.reply("♾️ TagAll unlimited aktif sampai bot dihentikan manual.")

@app.on_message(filters.text & filters.group & ~filters.command(["tagall", "addprem", "delprem", "start", "help"]))
async def auto_tagall(client, message):
    uid = message.from_user.id
    if not premium_users.find_one({"_id": uid}):
        return
    text = message.text
    await message.reply("🔁 Auto TagAll aktif selama 5 menit...")

    members = [m async for m in client.get_chat_members(message.chat.id)]
    count = 0
    for m in members:
        if not m.user or m.user.is_bot:
            continue
        try:
            await message.reply_text(f"{text} [{m.user.first_name}](tg://user?id={m.user.id})",
                                     disable_web_page_preview=True)
            count += 1
            await asyncio.sleep(2)
        except:
            continue

    await message.reply(f"✅ TagAll selesai ({count} anggota).")

@app.on_message(filters.command("addprem") & filters.user(OWNER_IDS))
async def add_premium(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan: /addprem <user_id>")
    uid = int(message.command[1])
    premium_users.update_one({"_id": uid}, {"$set": {"active": True}}, upsert=True)
    await message.reply_text(f"✅ User {uid} ditambahkan ke premium list.")

@app.on_message(filters.command("delprem") & filters.user(OWNER_IDS))

ᴏғғ, [31/10/2025 23:35]
async def del_premium(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan: /delprem <user_id>")
    uid = int(message.command[1])
    premium_users.delete_one({"_id": uid})
    await message.reply_text(f"❌ User {uid} dihapus dari premium list.")

print("🚀 Garfield TagAllBot siap dijalankan!")
app.run()
