# auto_tagall.py — auto tagall sistem pro
import asyncio
import random
from datetime import datetime
from pyrogram import Client, enums
from pyrogram.types import Message
from pymongo import MongoClient
from config import MONGO_URL, STORE_LINK, LOG_CHANNEL, BOT_NAME, OWNER_ID
from emoji_list import EMOJIS

# === koneksi mongo ===
mongo = MongoClient(MONGO_URL)
db = mongo["garfield_system"]
partners = db["partners"]

# === Variabel Global ===
AUTO_SESSIONS = {}
TAG_BATCH = 10     # jumlah user per batch tag
SPAM_DELAY = 5     # delay antar kirim pesan

async def auto_tagall_start(app: Client, chat_id: int, user_id: int, duration: int = 300):
    """Mulai auto tagall di grup."""
    if chat_id in AUTO_SESSIONS:
        await app.send_message(chat_id, "⚠️ TagAll sudah aktif di grup ini.")
        return

    AUTO_SESSIONS[chat_id] = True
    start_msg = await app.send_message(
        chat_id,
        f"<blockquote>🦊 {BOT_NAME} Auto TagAll Aktif!\n"
        f"🔹 Diminta oleh: [{user_id}](tg://user?id={user_id})\n"
        f"🔹 Durasi: {duration//60} menit\n"
        f"💡 Powered by [Garfield Store]({STORE_LINK})</blockquote>",
        disable_web_page_preview=True
    )

    try:
        members = []
        async for m in app.get_chat_members(chat_id):
            if m.user.is_bot or m.user.is_deleted:
                continue
            members.append(m.user.id)

        total = len(members)
        print(f"[INFO] Mulai AutoTagAll di {chat_id}, total member: {total}")

        count = 0
        while AUTO_SESSIONS.get(chat_id):
            random.shuffle(members)
            text = random.choice([
                "🐾 Hai semuanya, semangat ya!",
                "🌟 Garfield hadir buat nyapa kamu semua!",
                "🍀 Jangan lupa senyum hari ini 😎",
                "☕ Yuk istirahat sebentar bareng Garfield!"
            ])
            batch = []
            for uid in members:
                emoji = random.choice(EMOJIS)
                batch.append(f"{emoji}[‌](tg://user?id={uid})")  # spasi zero-width biar rapi

                if len(batch) >= TAG_BATCH:
                    count += len(batch)
                    footer = f"\n\n💬 {text}\n\n🔗 [STORE]({STORE_LINK})"
                    await app.send_message(chat_id, "".join(batch) + footer)
                    await asyncio.sleep(SPAM_DELAY)
                    batch.clear()

            await asyncio.sleep(duration)
            break

        await app.send_message(
            chat_id,
            f"🟡 Auto TagAll selesai.\nTotal mention: {count}\n"
            f"💡 Powered by [Garfield Store]({STORE_LINK})",
            disable_web_page_preview=True
        )

    except Exception as e:
        await app.send_message(chat_id, f"❌ Error auto tagall: {e}")
    finally:
        AUTO_SESSIONS.pop(chat_id, None)
        await app.send_message(LOG_CHANNEL, f"✅ Sesi auto tagall di {chat_id} selesai.")

async def stop_auto_tagall(app: Client, chat_id: int):
    """Hentikan auto tagall manual"""
    if chat_id not in AUTO_SESSIONS:
        return await app.send_message(chat_id, "⚠️ Tidak ada sesi Auto TagAll aktif.")
    AUTO_SESSIONS.pop(chat_id, None)
    await app.send_message(chat_id, "🛑 Auto TagAll dihentikan.")

# === event helper ===
async def trigger_auto_tagall(app: Client, message: Message):
    """trigger dipanggil dari callback partner"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # cek partner di Mongo
    partner = partners.find_one({"user_id": user_id})
    if partner:
        duration = 300  # 5 menit
    else:
        duration = 120  # non partner cuma 2 menit

    await auto_tagall_start(app, chat_id, user_id, duration)

print("✅ auto_tagall.py loaded successfully.")
