# GarfieldBot.py — modul utama admin panel & broadcast
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client
from pymongo import MongoClient
from config import MONGO_URL, OWNER_IDS, LOG_GROUP_ID, BOT_NAME

# === koneksi mongo ===
mongo = MongoClient(MONGO_URL)
db = mongo["garfield_system"]
partners = db["partners"]
premiums = db["premium_users"]

# === handler tombol owner ===
async def handle_owner_panel(client: Client, query):
    uid = query.from_user.id
    if uid not in OWNER_IDS:
        return await query.answer("❌ Kamu bukan owner!", show_alert=True)

    data = query.data
    if data == "list_prem":
        all_prem = [str(x["user_id"]) for x in premiums.find()]
        text = "**👑 Premium Users:**\n" + ("\n".join(all_prem) if all_prem else "_Belum ada user premium._")
        await query.message.edit_text(text, reply_markup=owner_menu())
    elif data == "add_prem":
        await query.message.edit_text("Kirim ID user untuk ditambahkan ke Premium:")
        db["pending_action"].update_one({"owner": uid}, {"$set": {"mode": "add"}}, upsert=True)
    elif data == "del_prem":
        await query.message.edit_text("Kirim ID user untuk dihapus dari Premium:")
        db["pending_action"].update_one({"owner": uid}, {"$set": {"mode": "del"}}, upsert=True)
    elif data == "broadcast":
        await query.message.edit_text("Kirim pesan broadcast untuk semua partner bot:")
        db["pending_action"].update_one({"owner": uid}, {"$set": {"mode": "broadcast"}}, upsert=True)
    else:
        await query.answer("Menu tidak dikenal!", show_alert=True)


# === proses pesan teks owner ===
async def process_owner_message(client: Client, message):
    uid = message.from_user.id
    if uid not in OWNER_IDS:
        return

    act = db["pending_action"].find_one({"owner": uid})
    if not act:
        return

    mode = act.get("mode")
    text = message.text.strip()

    if mode == "add":
        try:
            uid_target = int(text)
            premiums.update_one({"user_id": uid_target}, {"$set": {"user_id": uid_target}}, upsert=True)
            await message.reply(f"✅ User `{uid_target}` ditambahkan ke premium.")
        except Exception as e:
            await message.reply(f"❌ Gagal menambahkan: {e}")

    elif mode == "del":
        try:
            uid_target = int(text)
            premiums.delete_one({"user_id": uid_target})
            await message.reply(f"✅ User `{uid_target}` dihapus dari premium.")
        except Exception as e:
            await message.reply(f"❌ Gagal menghapus: {e}")

    elif mode == "broadcast":
        await message.reply("📢 Mengirim broadcast ke semua partner...")
        await broadcast_to_partners(client, text)

    db["pending_action"].delete_one({"owner": uid})


# === broadcast ke partner bot ===
async def broadcast_to_partners(client: Client, text: str):
    success, fail = 0, 0
    all_partners = partners.find()

    for p in all_partners:
        token = p.get("token")
        chat_id = p.get("log_chat_id", LOG_GROUP_ID)
        if not token:
            continue

        try:
            sub = Client(f"broadcast_{chat_id}", api_id=client.api_id, api_hash=client.api_hash, bot_token=token)
            await sub.start()
            await sub.send_message(chat_id, f"📢 **Broadcast dari {BOT_NAME}**\n\n{text}")
            await sub.stop()
            success += 1
        except Exception as e:
            print(f"[⚠️] Broadcast gagal ke {chat_id}: {e}")
            fail += 1

    await client.send_message(LOG_GROUP_ID, f"📊 Broadcast selesai.\n✅ Sukses: {success}\n❌ Gagal: {fail}")


# === tombol owner panel ===
def owner_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📜 List Premium", callback_data="list_prem")],
            [
                InlineKeyboardButton("➕ Add Premium", callback_data="add_prem"),
                InlineKeyboardButton("➖ Remove Premium", callback_data="del_prem")
            ],
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
            [InlineKeyboardButton("🏪 STORE", url="https://t.me/storegarf")],
        ]
    )

print("✅ GarfieldBot.py loaded successfully.")
