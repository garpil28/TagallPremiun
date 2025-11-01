import asyncio
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)
from main import app

# Grup Owner & Grup Log
OWNER_ID = 6954401932
OWNER_GROUP_ID = --1002430300514  # grup auto tagall aktif
LOG_GROUP_ID = -1003282574590    # grup log juga

# ─── Tombol Menu Utama ─────────────────────────────
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤝 Minta Partner", callback_data="partner:add"),
            InlineKeyboardButton("❌ Copot Partner", callback_data="partner:remove")
        ],
        [
            InlineKeyboardButton("📢 Minta TagAll", callback_data="partner:tagall")
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="menu:help"),
            InlineKeyboardButton("🏓 Cek Ping", callback_data="menu:ping")
        ]
    ])

# ─── /start ─────────────────────────────────────────
@app.on_message(filters.command("start"))
async def start_bot(_, message: Message):
    user = message.from_user.first_name
    banner = "banner.jpg"  # pastikan file ini ada
    caption = (
        f"👋 Halo {user}!\n\n"
        "Saya Garfield Auto TagAll Bot 🐾\n"
        "• Auto tagall aktif 24 jam di grup owner.\n"
        "• Manual tagall hanya bisa dilakukan oleh admin grup.\n\n"
        "Silakan pilih menu di bawah ini 👇"
    )
    try:
        await message.reply_photo(photo=banner, caption=caption, reply_markup=main_menu())
    except Exception:
        await message.reply_text(caption, reply_markup=main_menu())

    await app.send_message(LOG_GROUP_ID, f"🟢 {user} baru menekan /start.")

# ─── Callback Tombol Menu ──────────────────────────
@app.on_callback_query(filters.regex("^menu:"))
async def menu_callback(_, cq):
    data = cq.data.split(":")[1]
    if data == "help":
        text = (
            "📚 Panduan GarfieldBot\n\n"
            "🔹 /tagall [pesan] — Tag semua member (admin only)\n"
            "🔹 AutoTagAll aktif 24 jam di grup owner.\n"
            "🔹 /cancel — Hentikan proses tagall manual.\n"
            "🔹 /ping — Tes respon bot.\n"
            "🔹 /partner — Setel / cabut partner grup."
        )
        await cq.message.edit_text(text, reply_markup=main_menu())
    elif data == "ping":
        start = asyncio.get_event_loop().time()
        m = await cq.message.reply("🏓 Pong!")
        end = asyncio.get_event_loop().time()
        await m.edit_text(f"🏓 Pong! {(end - start)*1000:.0f} ms")
    await cq.answer()

# ─── Partner System ────────────────────────────────
@app.on_callback_query(filters.regex("^partner:"))
async def partner_callback(_, cq):
    data = cq.data.split(":")[1]
    user = cq.from_user
    if data == "add":
        await cq.message.edit_text(
            f"🤝 Hai {user.mention},\n"
            "Permintaan partner kamu sudah dikirim ke Owner GarfieldBot.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="menu:help")]])
        )
        await app.send_message(
            LOG_GROUP_ID,
            f"📩 Partner Request dari {user.mention} (ID: {user.id})"
        )

    elif data == "remove":
        await cq.message.edit_text(
            f"❌ {user.mention}, partner kamu telah dicabut.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="menu:help")]])
        )
        await app.send_message(LOG_GROUP_ID, f"❌ Partner {user.mention} dicabut.")

    elif data == "tagall":
        await cq.message.edit_text(
            f"📢 {user.mention}, permintaan tagall kamu dikirim ke Owner GarfieldBot.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="menu:help")]])
        )
        await app.send_message(LOG_GROUP_ID, f"📢 {user.mention} meminta TagAll otomatis.")
    await cq.answer()

# ─── Command /ping ────────────────────────────────
@app.on_message(filters.command("ping"))
async def ping(_, message: Message):
    start = asyncio.get_event_loop().time()
    m = await message.reply("🏓 Pong!")
    end = asyncio.get_event_loop().time()
    await m.edit_text(f"🏓 Pong! {(end - start)*1000:.0f} ms")

# ─── Log Aktivitas ────────────────────────────────
@app.on_message(filters.command(["help", "menu"]))
async def help_menu(_, message: Message):
    await start_bot(_, message)
