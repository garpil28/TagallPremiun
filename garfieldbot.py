# garfieldbot.py — versi partner-only clean
import asyncio
import random
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import MONGO_URL, BOT_NAME, STORE_LINK, LOG_CHANNEL

# koneksi ke database Mongo
mongo = MongoClient(MONGO_URL)
db = mongo["garfield_system"]
partners = db["partners"]
requests = db["tag_requests"]

# daftar emoji untuk footer
EMOJIS = ["😺", "😼", "😻", "😹", "😽", "🙀", "😾", "😸"]


# === fungsi utama callback ===
async def handle_callback(query):
    data = query.data
    user_id = query.from_user.id

    if data == "req_tagall":
        await handle_tagall_request(query, user_id)
    elif data == "req_partner":
        await handle_partner_request(query, user_id)
    elif data == "req_unpartner":
        await handle_unpartner_request(query, user_id)
    else:
        await query.answer("❌ Perintah tidak dikenal.", show_alert=True)


# === fitur utama: MINTA TAGALL (hanya partner) ===
async def handle_tagall_request(query, user_id):
    try:
        msg = query.message
        await query.answer("🔍 Memeriksa status kamu...", show_alert=False)

        partner_data = partners.find_one({"user_id": user_id})
        if not partner_data:
            return await query.answer(
                "❌ Fitur ini hanya untuk partner resmi GarfieldBot.",
                show_alert=True,
            )

        # aktifkan tagall 5 menit (auto stop)
        limit = 5 * 60
        await msg.reply_text(
            f"✅ Partner aktif terdeteksi!\nAuto-TagAll diaktifkan selama 5 menit ⏱️."
        )

        # simpan status request
        requests.insert_one({"user_id": user_id, "active": True, "duration": limit})
        await asyncio.sleep(limit)

        # setelah 5 menit, auto nonaktif
        requests.update_one({"user_id": user_id}, {"$set": {"active": False}})
        await msg.reply_text("⏰ Waktu Auto-TagAll kamu sudah selesai!")

    except Exception as e:
        await query.message.reply_text(f"❌ Gagal memproses: {e}")


# === AJUKAN PARTNER (register) ===
async def handle_partner_request(query, user_id):
    try:
        partners.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
        await query.answer("🤝 Partner berhasil ditambahkan!", show_alert=True)
        await query.message.reply_text(
            f"✅ Kamu sekarang terdaftar sebagai Partner resmi di *{BOT_NAME}*.\n"
            f"📦 Dukung kami di: {STORE_LINK}"
        )
    except Exception as e:
        await query.message.reply_text(f"❌ Gagal menambahkan partner: {e}")


# === LEPAS PARTNER ===
async def handle_unpartner_request(query, user_id):
    try:
        partners.delete_one({"user_id": user_id})
        await query.answer("❌ Partner dihapus.", show_alert=True)
        await query.message.reply_text("🚪 Kamu telah keluar dari daftar Partner.")
    except Exception as e:
        await query.message.reply_text(f"❌ Gagal menghapus partner: {e}")


# === DAFTAR PARTNER (buat owner) ===
async def list_partners_text():
    allp = partners.find()
    total = partners.count_documents({})
    if total == 0:
        return "📭 Belum ada partner terdaftar."

    text = f"🤝 Daftar Partner Aktif ({total}):\n\n"
    for p in allp:
        text += f"• [{p.get('user_id')}](tg://user?id={p.get('user_id')})\n"
    return text


# === TAMBAH PARTNER VIA TOKEN (khusus owner) ===
async def add_partner_by_token_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Gunakan format:\n/addbot <BOT_TOKEN> [LOG_CHAT_ID]")

    token = args[1]
    log_chat = args[2] if len(args) > 2 else LOG_CHANNEL

    partners.insert_one({"token": token, "log_chat_id": log_chat})
    await message.reply(
        f"✅ Partner bot baru ditambahkan!\n📡 Log Channel: {log_chat}"
    )


# === HAPUS PARTNER VIA CMD (owner) ===
async def del_partner_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Gunakan format:\n/delbot <LOG_CHAT_ID>")

    log_chat = args[1]
    partners.delete_one({"log_chat_id": log_chat})
    await message.reply("✅ Partner dihapus dari sistem.")


# === FOOTER OTOMATIS ===
def tagall_footer():
    emoji = random.choice(EMOJIS)
    return f"\n\n{emoji} Powered by [{BOT_NAME}]({STORE_LINK})"


print("✅ garfieldbot.py partner-only loaded successfully.")
