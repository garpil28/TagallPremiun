# auto_tagall.py — GarfieldBot Auto TagAll System (Partner Only)
import asyncio
import random
from datetime import datetime, timedelta
from pyrogram import Client
from pymongo import MongoClient
from pyrogram.types import Message
from config import MONGO_URL, STORE_LINK, LOG_CHANNEL, BOT_NAME, OWNER_ID
from emoji_list import EMOJIS

# === Koneksi Mongo ===
mongo = MongoClient(MONGO_URL)
db = mongo["garfield_system"]
partners = db["partners"]
tag_history = db["tag_history"]

# === Variabel Global ===
AUTO_SESSIONS = {}
TAG_BATCH = 10      # jumlah mention per batch
SPAM_DELAY = 5      # delay antar batch (detik)
DURATION = 300      # durasi auto tag (5 menit)

# === Pesan Random Garfield ===
RANDOM_MSGS = [
    "🐾 Hai semuanya, semangat ya!",
    "🌟 Garfield hadir buat nyapa kamu semua!",
    "🍀 Jangan lupa senyum hari ini 😎",
    "☕ Yuk istirahat sebentar bareng Garfield!",
    "💫 Garfield nyapa biar grup makin rame!",
    "🧡 Hari ini luar biasa, yuk happy bareng Garfield!",
    "😼 Garfield datang buat ngingetin kamu tetap positif!"
]

# === Fungsi utama ===
async def auto_tagall_start(app: Client, chat_id: int, user_id: int, custom_text: str = None):
    """Mulai auto tagall untuk partner"""
    if chat_id in AUTO_SESSIONS:
        await app.send_message(chat_id, "⚠️ Auto TagAll sedang berjalan di grup ini.")
        return

    # cek apakah user partner
    partner = partners.find_one({"user_id": user_id})
    if not partner:
        await app.send_message(chat_id, "❌ Kamu bukan partner. Ajukan di menu help untuk jadi partner.")
        return

    # cek limit harian
    today = datetime.utcnow().date()
    last_use = tag_history.find_one({"user_id": user_id, "date": str(today)})
    if last_use:
        await app.send_message(chat_id, "⚠️ Limit harian kamu sudah digunakan. Coba lagi besok.")
        return

    AUTO_SESSIONS[chat_id] = True
    tag_history.insert_one({"user_id": user_id, "date": str(today), "chat_id": chat_id})

    start_msg = await app.send_message(
        chat_id,
        f"🦊 **{BOT_NAME} Auto TagAll Aktif!**\n"
        f"🔹 Diminta oleh: [{user_id}](tg://user?id={user_id})\n"
        f"🔹 Durasi: 5 menit\n"
        f"💡 Powered by [Garfield Store]({STORE_LINK})",
        disable_web_page_preview=True
    )

    try:
        members = []
        async for m in app.get_chat_members(chat_id):
            if m.user.is_bot or m.user.is_deleted:
                continue
            members.append(m.user.id)

        total = len(members)
        count = 0
        await app.send_message(LOG_CHANNEL, f"🚀 Mulai AutoTagAll di grup {chat_id} oleh {user_id} (Total member: {total})")

        random.shuffle(members)
        end_time = datetime.utcnow() + timedelta(seconds=DURATION)

        while datetime.utcnow() < end_time and AUTO_SESSIONS.get(chat_id):
            text = custom_text or random.choice(RANDOM_MSGS)
            batch = []
            for uid in members:
                emoji = random.choice(EMOJIS)
                batch.append(f"{emoji}[‌](tg://user?id={uid})")

                if len(batch) >= TAG_BATCH:
                    footer = f"\n\n💬 {text}\n\n🏪 [STORE]({STORE_LINK})"
                    await app.send_message(chat_id, "".join(batch) + footer)
                    await asyncio.sleep(SPAM_DELAY)
                    count += len(batch)
                    batch.clear()

            await asyncio.sleep(10)

        await app.send_message(
            chat_id,
            f"🟡 **Auto TagAll selesai!**\nTotal mention: {count}\n💡 Powered by [Garfield Store]({STORE_LINK})",
            disable_web_page_preview=True
        )
        await app.send_message(LOG_CHANNEL, f"✅ AutoTagAll selesai di grup {chat_id} oleh {user_id}, total {count} mention.")

    except Exception as e:
        await app.send_message(chat_id, f"❌ Error auto tagall: {e}")
        await app.send_message(LOG_CHANNEL, f"⚠️ Error AutoTagAll di {chat_id}: {e}")
    finally:
        AUTO_SESSIONS.pop(chat_id, None)


async def stop_auto_tagall(app: Client, chat_id: int):
    """Hentikan auto tagall manual"""
    if chat_id not in AUTO_SESSIONS:
        return await app.send_message(chat_id, "⚠️ Tidak ada sesi Auto TagAll aktif.")
    AUTO_SESSIONS.pop(chat_id, None)
    await app.send_message(chat_id, "🛑 Auto TagAll dihentikan.")
    await app.send_message(LOG_CHANNEL, f"🛑 AutoTagAll dihentikan di {chat_id} oleh owner.")


async def trigger_auto_tagall(app: Client, message: Message):
    """Trigger dari pesan user partner"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip()

    # cek partner
    partner = partners.find_one({"user_id": user_id})
    if not partner:
        return await message.reply("❌ Kamu bukan partner. Ajukan partner lewat menu Help.")

    await auto_tagall_start(app, chat_id, user_id, custom_text=text)

print("✅ auto_tagall.py loaded successfully.")
