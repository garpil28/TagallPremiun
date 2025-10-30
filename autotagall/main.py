# autotagall/main.py
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import os

# Ambil token dari variabel lingkungan (environment variable)
TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", 123456))  # ganti kalau mau
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")

# Buat client bot
app = Client(
    "autotagall_bot",
    bot_token=TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# --- FITUR 1: Command start ---
@app.on_message(filters.command("start"))
async def start_cmd(_, msg: Message):
    await msg.reply_text(
        "👋 Halo! Saya bot TagAll otomatis.\n"
        "Ketik /tagall untuk menandai semua anggota grup."
    )

# --- FITUR 2: Manual TagAll ---
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, msg: Message):
    chat = msg.chat
    members = []
    async for member in client.get_chat_members(chat.id):
        if not member.user.is_bot:
            members.append(member.user.mention)

    text = "🔥 TagAll diminta oleh " + msg.from_user.mention + " 🔥\n\n"
    text += " ".join(members)

    # Bagi pesan jadi beberapa bagian biar ga terlalu panjang
    for part in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        await msg.reply_text(part)
        await asyncio.sleep(1)

# --- Jalankan bot ---
print("✅ Bot autotagall sedang berjalan...")
app.run()
