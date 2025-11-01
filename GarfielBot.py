import asyncio
import random
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from config import CBOT, COWNER
from emoji_list import EMOJIS

# ────────────────────────────────
# Inisialisasi Client
# ────────────────────────────────
app = Client(
    "GarfieldBot",
    api_id=CBOT.API_ID,
    api_hash=CBOT.API_HASH,
    bot_token=CBOT.BOT_TOKEN,
)

# ────────────────────────────────
# Variabel global
# ────────────────────────────────
ACTIVE = False
PARTNERS = set()
OWNER_GROUP = CBOT.LOG_GROUP_ID
SPAM_DELAY = 5  # detik antar tag
TAG_BATCH = 5   # jumlah user per batch

# ────────────────────────────────
# Banner Startup
# ────────────────────────────────
async def banner_startup():
    banner = f"""
<blockquote>
🦊 <b>{CBOT.BOT_NAME}</b> Telah Aktif!

👑 Owner  : {COWNER.OWNER_NAME}
🌐 Grup   : <a href="https://t.me/officialhyperion">Official Hyperion</a>
🧠 Status : Auto TagAll 24 Jam Aktif
</blockquote>
"""
    await app.send_message(OWNER_GROUP, banner)

# ────────────────────────────────
# Fungsi Auto TagAll
# ────────────────────────────────
async def auto_tagall():
    global ACTIVE
    while ACTIVE:
        try:
            text = random.choice([
                "🐾 Halo semuanya, Garfield hadir mengingatkan!",
                "🌟 Semangat terus hari ini!",
                "🍀 Jangan lupa bahagia!",
                "☕ Waktunya istirahat sebentar, teman-teman!",
            ])
            user_list = []
            async for m in app.get_chat_members(OWNER_GROUP):
                if m.user.is_bot or m.user.is_deleted:
                    continue
                emoji = random.choice(EMOJIS)
                mention = f"[{emoji}](tg://user?id={m.user.id})"
                user_list.append(mention)

                if len(user_list) == TAG_BATCH:
                    msg = f"<blockquote>{text}</blockquote>\n\n{''.join(user_list)}"
                    await app.send_message(
                        OWNER_GROUP,
                        msg,
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(SPAM_DELAY)
                    user_list.clear()
            await asyncio.sleep(300)  # jeda antar sesi 5 menit
        except Exception as e:
            await app.send_message(OWNER_GROUP, f"❌ Error auto tagall: {e}")
            await asyncio.sleep(10)

# ────────────────────────────────
# Start Command
# ────────────────────────────────
@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    user_id = message.from_user.id
    btns = [
        [InlineKeyboardButton("🧩 Minta Partner", callback_data="partner:add")],
        [InlineKeyboardButton("❌ Copot Partner", callback_data="partner:remove")],
        [InlineKeyboardButton("📊 Cek Status", callback_data="partner:status")],
        [InlineKeyboardButton("⚙️ Menu Bantuan", callback_data="partner:help")],
    ]
    greet = f"""
<blockquote>
Halo <b>{message.from_user.first_name}</b> 👋  
Saya <b>{CBOT.BOT_NAME}</b>, asisten auto tagall 24 jam!

Gunakan tombol di bawah untuk mengelola partner atau melihat bantuan.
</blockquote>
"""
    await message.reply(greet, reply_markup=InlineKeyboardMarkup(btns))

    # Auto aktif jika di grup owner
    if message.chat.id == OWNER_GROUP:
        global ACTIVE
        if not ACTIVE:
            ACTIVE = True
            await message.reply("<blockquote>🟢 Auto TagAll dimulai di grup Owner.</blockquote>")
            asyncio.create_task(auto_tagall())

# ────────────────────────────────
# Callback Partner System
# ────────────────────────────────
@app.on_callback_query(filters.regex("^partner:"))
async def partner_callback(_, cq: CallbackQuery):
    action = cq.data.split(":")[1]
    user_id = cq.from_user.id

    if action == "add":
        PARTNERS.add(user_id)
        await cq.answer("✅ Kamu telah menjadi partner Garfield!", show_alert=True)
    elif action == "remove":
        if user_id in PARTNERS:
            PARTNERS.remove(user_id)
            await cq.answer("❌ Kamu telah dilepas dari partner Garfield.", show_alert=True)
        else:
            await cq.answer("⚠️ Kamu belum terdaftar sebagai partner.", show_alert=True)
    elif action == "status":
        status = "Terdaftar ✅" if user_id in PARTNERS else "Belum Terdaftar ❌"
        await cq.answer(f"📊 Status Partner Kamu: {status}", show_alert=True)
    elif action == "help":
        msg = """
<blockquote>
<b>🧩 Panduan Garfield Bot</b>

- /start → buka menu
- /ping → cek respon bot
- tombol 'Minta Partner' → daftar partner resmi
- tombol 'Copot Partner' → lepas partner
- tombol 'Cek Status' → lihat status kamu

Partner bisa meminta fitur tagall manual melalui bot.
</blockquote>
"""
        await cq.message.reply(msg)

# ────────────────────────────────
# Command Ping
# ────────────────────────────────
@app.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    start = datetime.now()
    msg = await message.reply_text("🏓 Pong...")
    end = datetime.now()
    ping = (end - start).microseconds / 1000
    await msg.edit_text(f"🏓 Pong! `{ping}ms`")

# ────────────────────────────────
# Run
# ────────────────────────────────
async def main():
    await app.start()
    await banner_startup()
    print(f"[✅] {CBOT.BOT_NAME} aktif dan siap 24 jam.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
