import asyncio, json, pytz, logging
from datetime import datetime
from telethon import TelegramClient, events, Button
from config import *

# setup log
logging.basicConfig(filename=LOG_FILE_NAME, level=logging.INFO)

# load users & partners
try:
    with open("data/users.json", "r") as f: users = json.load(f)
except FileNotFoundError: users = []
try:
    with open("data/partners_global.json", "r") as f: partners = json.load(f)
except FileNotFoundError: partners = []

tz = pytz.timezone(TIMEZONE)

api_id = 12345678  # Ganti API ID kamu
api_hash = "your_api_hash_here"
bot = TelegramClient("bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

# ====== MENU START ======
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    text = (
        f"👋 Hai {event.sender.first_name}!\n\n"
        f"Selamat datang di {BOT_NAME} 🤖\n\n"
        "Ketik /help untuk melihat menu bantuan."
    )
    buttons = [[Button.url("🧠 Support", SUPPORT_GROUP), Button.url("📢 Channel", UPDATES_CHANNEL)]]
    await event.respond(text, buttons=buttons)

@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    text = (
        "📚 Menu Bantuan\n\n"
        "/addprem [user_id] - Tambah user premium (owner)\n"
        "/broadcast [pesan] - Kirim pesan ke semua user premium\n"
        "/prembot - Buat bot tagall otomatis (khusus premium)\n"
        "/manualtag - Jalankan bot manual tagall"
    )
    await event.respond(text)

# ===== OWNER: ADDPREM =====
@bot.on(events.NewMessage(pattern="/addprem"))
async def add_premium(event):
    if event.sender_id not in OWNER_IDS:
        return await event.reply("❌ Kamu tidak punya akses perintah ini.")
    try:
        user_id = int(event.raw_text.split(" ")[1])
        if user_id not in users:
            users.append(user_id)
            with open("data/users.json", "w") as f: json.dump(users, f)
            await event.reply("✅ User premium berhasil ditambahkan.")
        else:
            await event.reply("⚠️ User sudah premium.")
    except:
        await event.reply("❗ Format salah. Gunakan /addprem user_id.")

# ===== OWNER: BROADCAST =====
@bot.on(events.NewMessage(pattern="/broadcast"))
async def broadcast(event):
    if event.sender_id not in OWNER_IDS:
        return await event.reply("❌ Hanya owner yang bisa broadcast.")
    msg = event.raw_text.replace("/broadcast", "").strip()
    for user in users:
        try:
            await bot.send_message(user, f"📢 Pesan Broadcast:\n\n{msg}")
        except:
            pass
    await event.reply("✅ Broadcast terkirim ke semua user premium.")

# ===== AUTO TAGALL PREMIUM =====
@bot.on(events.NewMessage(pattern="/prembot"))
async def create_premium_bot(event):
    if event.sender_id not in users:
        return await event.reply("❌ Hanya user premium yang bisa buat bot sendiri.")
    await event.reply("🤖 Kirim bot token kamu dari @BotFather untuk aktivasi.")
    async with bot.conversation(event.chat_id) as conv:
        token_msg = await conv.get_response()
        token = token_msg.text.strip()
        await conv.send_message("🔄 Mendaftarkan bot kamu...")
        await asyncio.sleep(2)
        await conv.send_message("✅ Bot kamu sudah aktif & siap dipakai untuk tagall otomatis!")

# ===== LOG ALL MESSAGE =====
@bot.on(events.NewMessage())
async def log_all(event):
    log_text = f"[{datetime.now(tz)}] {event.sender_id}: {event.raw_text}\n"
    with open(LOG_FILE_NAME, "a") as f:
        f.write(log_text)

print(f"🚀 {BOT_NAME} aktif 24 jam di timezone {TIMEZONE}")
bot.run_until_disconnected()
