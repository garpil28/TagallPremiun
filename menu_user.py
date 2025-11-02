# menu_user.py — GarfieldBot Partner System
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import MONGO_URL, LOG_CHANNEL, STORE_LINK, BOT_NAME, OWNER_ID
from auto_tagall import trigger_auto_tagall

# === koneksi database ===
mongo = MongoClient(MONGO_URL)
db = mongo["garfield_system"]
partners = db["partners"]

# === helper time WIB ===
def wib_now():
    return datetime.utcnow() + timedelta(hours=7)

# === menu utama ===
@Client.on_message(filters.command(["start", "help"]) & filters.private)
async def menu_help(app: Client, message: Message):
    user_id = message.from_user.id
    partner = partners.find_one({"user_id": user_id})

    # tombol umum
    buttons = [
        [InlineKeyboardButton("🚀 Ajukan Partner", callback_data="req_partner")],
        [InlineKeyboardButton("❌ Lepas Partner", callback_data="del_partner")],
        [InlineKeyboardButton("🧠 Tentang Bot", callback_data="about_bot")],
        [
            InlineKeyboardButton("🏪 STORE", url=STORE_LINK),
            InlineKeyboardButton("👑 Pemilik Bot", url="https://t.me/kopi567"),
        ],
        [
            InlineKeyboardButton("💬 Support Grup", url="https://t.me/garfieldgrup"),
            InlineKeyboardButton("📢 Channel Info", url="https://t.me/garfieldchannel"),
        ],
    ]

    # jika partner aktif → tambah tombol tagall
    if partner:
        buttons.insert(0, [InlineKeyboardButton("🔥 Mulai Auto TagAll", callback_data="start_tagall")])

    text = (
        f"👋 Hai [{message.from_user.first_name}](tg://user?id={user_id})!\n\n"
        f"Aku **{BOT_NAME}**, bot auto tagall 24 jam dengan sistem partner eksklusif.\n\n"
        f"💡 Klik tombol di bawah untuk mulai."
    )

    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
    )

# === tombol callback ===
@Client.on_callback_query()
async def callback_handler(app: Client, cq):
    user_id = cq.from_user.id
    data = cq.data
    partner = partners.find_one({"user_id": user_id})

    if data == "req_partner":
        if partner:
            await cq.message.edit_text("✅ Kamu sudah menjadi **Partner Aktif!** 😎\n\nLangsung saja pakai tombol ‘🔥 Mulai Auto TagAll’.")
            return

        partners.insert_one({
            "user_id": user_id,
            "since": wib_now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_used": None
        })
        await cq.message.edit_text(
            "🎉 Permintaan partner kamu sudah dikirim!\n"
            "Kamu kini terdaftar sebagai **Partner GarfieldBot**.\n\n"
            "Gunakan tombol `🔥 Mulai Auto TagAll` untuk menjalankan bot."
        )
        await app.send_message(LOG_CHANNEL, f"👤 Partner baru: [{user_id}](tg://user?id={user_id}) ditambahkan pada {wib_now().strftime('%H:%M %d/%m/%Y')} WIB")

    elif data == "del_partner":
        if not partner:
            await cq.message.edit_text("⚠️ Kamu belum terdaftar sebagai partner.")
            return
        partners.delete_one({"user_id": user_id})
        await cq.message.edit_text("❌ Status partner kamu sudah dihapus.")
        await app.send_message(LOG_CHANNEL, f"🗑 Partner [{user_id}](tg://user?id={user_id}) dihapus dari sistem.")

    elif data == "about_bot":
        await cq.message.edit_text(
            f"🤖 **Tentang {BOT_NAME}**\n\n"
            "Bot auto tagall otomatis tanpa command, aktif 24 jam penuh.\n"
            "Partner bisa menjalankan tagall sekali per hari (5 menit tiap sesi).\n\n"
            f"🔗 Powered by [Garfield Store]({STORE_LINK})",
            disable_web_page_preview=True
        )

    elif data == "start_tagall":
        if not partner:
            await cq.message.edit_text("⚠️ Kamu belum partner, ajukan dulu ya!")
            return

        # cek limit harian
        last_used = partner.get("last_used")
        if last_used:
            last_time = datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S")
            if wib_now().date() == last_time.date():
                await cq.message.edit_text("⏰ Kamu sudah pakai TagAll hari ini!\nCoba lagi besok ya 🦊")
                return

        # update waktu pakai
        partners.update_one({"user_id": user_id}, {"$set": {"last_used": wib_now().strftime("%Y-%m-%d %H:%M:%S")}})

        await cq.message.edit_text("🚀 Menjalankan Auto TagAll...\nBot akan aktif 5 menit (durasi partner).")
        await trigger_auto_tagall(app, cq.message)
        await app.send_message(LOG_CHANNEL, f"📢 Partner [{user_id}](tg://user?id={user_id}) menjalankan AutoTagAll jam {wib_now().strftime('%H:%M')} WIB")
