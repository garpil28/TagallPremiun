# garfielbot.py — handler partner & user interaksi
import asyncio
import random
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import MONGO_URL, BOT_NAME, STORE_LINK, LOG_CHANNEL

mongo = MongoClient(MONGO_URL)
db = mongo["garfield_system"]
partners = db["partners"]
requests = db["tag_requests"]

# === emoji random buat footer ===
EMOJIS = ["😺", "😼", "😻", "😹", "😽", "🙀", "😾", "😸"]

# === callback utama ===
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


# === MINTA TAGALL ===
async def handle_tagall_request(query, user_id):
    try:
        msg = query.message
        await query.answer("🔍 Memeriksa status kamu...", show_alert=False)

        partner_data = partners.find_one({"user_id": user_id})
        if partner_data:
            limit = 5 * 60  # 5 menit
            await msg.reply_text("✅ Kamu partner aktif. Auto-TagAll aktif 5 menit.")
        else:
            limit = 2 * 60  # 2 menit
            await msg.reply_text("⚡ Mode Non-Partner. Auto-TagAll aktif 2 menit.")

        requests.insert_one({"user_id": user_id, "active": True, "duration": limit})
        await asyncio.sleep(limit)
        requests.update_one({"user_id": user_id}, {"$set": {"active": False}})
        await msg.reply_text("⏰ Waktu Auto-TagAll selesai!")

    except Exception as e:
        await query.message.reply_text(f"❌ Gagal memproses: {e}")


# === AJUKAN PARTNER ===
async def handle_partner_request(query, user_id):
    try:
        partners.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
        await query.answer("🤝 Partner berhasil ditambahkan!", show_alert=True)
        await query.message.reply_text(f"✅ Kamu sekarang terdaftar sebagai Partner di *{BOT_NAME}*.")
    except Exception as e:
        await query.message.reply_text(f"❌ Gagal menambahkan partner: {e}")


# === LEPAS PARTNER ===
async def handle_unpartner_request(query, user_id):
    try:
        partners.delete_one({"user_id": user_id})
        await query.answer("❌ Partner dihapus.", show_alert=True)
        await query.message.reply_text("Kamu telah keluar dari daftar Partner.")
    except Exception as e:
        await query.message.reply_text(f"❌ Gagal menghapus partner: {e}")


# === Fungsi daftar partner (buat owner) ===
async def list_partners_text():
    allp = partners.find()
    if not allp.count():
        return "📭 Belum ada partner terdaftar."

    text = "🤝 Daftar Partner Aktif:\n\n"
    for p in allp:
        text += f"• {p.get('user_id')}\n"
    return text


# === Tambah partner via token (fitur premium / clone bot) ===
async def add_partner_by_token_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Gunakan format:\n/addbot <BOT_TOKEN> [LOG_CHAT_ID]")

    token = args[1]
    log_chat = args[2] if len(args) > 2 else LOG_CHANNEL

    partners.insert_one({"token": token, "log_chat_id": log_chat})
    await message.reply(f"✅ Partner bot baru ditambahkan!\nLog: {log_chat}")


# === Hapus partner ===
async def del_partner_cmd(message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Gunakan format:\n/delbot <LOG_CHAT_ID>")

    log_chat = args[1]
    partners.delete_one({"log_chat_id": log_chat})
    await message.reply("✅ Partner dihapus dari sistem.")


# === Footer TagAll ===
def tagall_footer():
    emoji = random.choice(EMOJIS)
    return f"\n\n{emoji} Powered by [{BOT_NAME}]({STORE_LINK})"


print("✅ garfielbot.py loaded successfully.")
