import asyncio
from pyrogram import Client, filters
from config import CBOT, COWNER
from pymongo import MongoClient

bot = Client(
    "GarfieldAuto",
    api_id=CBOT.API_ID,
    api_hash=CBOT.API_HASH,
    bot_token=CBOT.BOT_TOKEN,
)

mongo = MongoClient(CBOT.DATABASE_URL)
db = mongo["garfield_bot"]
premium_users = db["premium_users"]
partners = db["partners"]

# Tambah premium user
@bot.on_message(filters.command("addprem") & filters.user(COWNER.OWNER_IDS))
async def add_premium(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan: /addprem <user_id>")
    uid = int(message.command[1])
    premium_users.update_one({"_id": uid}, {"$set": {"active": True}}, upsert=True)
    await message.reply_text(f"✅ User {uid} sekarang premium!")

# Hapus premium user
@bot.on_message(filters.command("delprem") & filters.user(COWNER.OWNER_IDS))
async def del_premium(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan: /delprem <user_id>")
    uid = int(message.command[1])
    premium_users.delete_one({"_id": uid})
    await message.reply_text(f"❌ User {uid} sudah dihapus dari premium.")

# Start handler untuk semua user
@bot.on_message(filters.command("start"))
async def start_handler(_, message):
    uid = message.from_user.id
    is_premium = premium_users.find_one({"_id": uid})
    if not is_premium:
        return await message.reply_text("👋 Halo! Kamu belum premium.\nHubungi owner untuk akses TagAll Premium.")
    await message.reply_text(
        "🤖 Selamat datang di Auto TagAll!\n"
        "Kirim kata-kata yang ingin kamu tagall ke grup kamu.\n"
        "Bot akan berjalan selama 5 menit dan menandai semua anggota!"
    )

# Terima pesan dari partner dan mulai tagall
@bot.on_message(filters.text & ~filters.command(["start", "addprem", "delprem"]))
async def tagall_handler(client, message):
    uid = message.from_user.id
    is_premium = premium_users.find_one({"_id": uid})
    if not is_premium:
        return
    text = message.text
    await message.reply_text("🔄 Proses TagAll sedang berjalan selama 5 menit...")

    members = [m async for m in client.get_chat_members(message.chat.id)]
    count = 0
    for m in members:
        if not m.user or m.user.is_bot:
            continue
        try:
            await message.reply_text(f"{text} [{m.user.first_name}](tg://user?id={m.user.id})", disable_web_page_preview=True)
            count += 1
            await asyncio.sleep(2)
        except:
            continue

    await message.reply_text(f"✅ TagAll selesai ({count} anggota).")
    await message.reply_document(docume
    main()
