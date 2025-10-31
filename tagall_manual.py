# manual_tagall.py — manual tagall handler (durasi pilihan)
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from database.manual_db import manual_sessions_col, manual_logs_col

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manual_tagall")

app = Client(
    "manual_tagall",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="."
)

DUR_MAP = {
    "3m": 3,
    "5m": 5,
    "10m": 10,
    "20m": 20,
    "30m": 30,
    "60m": 60,
    "90m": 90,
    "120m": 120,
    "unlimited": None
}

async def now_wib():
    return datetime.now(timezone.utc) + timedelta(hours=7)

@app.on_message(filters.command("jalan") & filters.group)
async def jalan_cmd(client: Client, message: Message):
    # check admin
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ("administrator", "creator"):
            return await message.reply_text("❌ Hanya admin grup yang bisa menjalankan TagAll manual.")
    except Exception:
        return await message.reply_text("❌ Gagal memeriksa status admin.")

    # show keyboard-like instructions (users click by sending command)
    choices = "Pilih durasi: /durasi 3m | /durasi 5m | /durasi 10m | /durasi 20m | /durasi 30m | /durasi 60m | /durasi 90m | /durasi 120m | /durasi unlimited"
    await message.reply_text("🧠 Pilih durasi jalan manual untuk TagAll:\n\n" + choices)

@app.on_message(filters.command("durasi") & filters.group)
async def durasi_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan: /durasi <3m/5m/.../unlimited>")
    key = message.command[1].lower()
    if key not in DUR_MAP:
        return await message.reply_text("Pilihan durasi tidak valid.")
    minutes = DUR_MAP[key]
    desc = "Unlimited" if minutes is None else f"{minutes} menit"

    cid = message.chat.id
    # check if session running
    if manual_sessions_col.find_one({"chat_id": cid, "status": "running"}):
        return await message.reply_text("⚠️ Proses TagAll manual sudah berjalan di grup ini.")

    # create session
    session = {
        "chat_id": cid,
        "started_by": message.from_user.id,
        "duration_minutes": minutes,
        "status": "running",
        "start_time": (await now_wib()).isoformat()
    }
    manual_sessions_col.insert_one(session)
    await message.reply_text(f"💭 Sabar, TagAll lagi di proses selama {desc}...")

    # simulate tagging process
    # WARNING: real per-member mention requires rate limit handling
    try:
        members = []
        async for m in client.get_chat_members(cid):
            # skip bots + deleted
            if m.user.is_bot or getattr(m.user, "is_deleted", False):
                continue
            members.append(m.user)
    except Exception as e:
        manual_sessions_col.update_one({"chat_id": cid}, {"$set": {"status": "error", "error": str(e)}})
        return await message.reply_text(f"❌ Gagal mengambil daftar member: {e}")

    # send starting message
    await client.send_message(cid, f"🔥 TagAll manual dimulai... ({desc})")

    # For safety we do batch mention by username or mention link (Pyrogram allows mention via tg://user?id=)
    batch = []
    batch_size = 5
    delay_s = 3
    mentioned = 0
    for u in members:
        mention = f"[{u.first_name}](tg://user?id={u.id})"
        batch.append(mention)
        if len(batch) >= batch_size:
            text = "\n".join(batch)
            try:
                await client.send_message(cid, text, disable_web_page_preview=True)
                mentioned += len(batch)
            except Exception:
                pass

batch = []
            await asyncio.sleep(delay_s)
        # check if unlimited or time limit exceeded
    if batch:
        try:
            await client.send_message(cid, "\n".join(batch), disable_web_page_preview=True)
            mentioned += len(batch)
        except Exception:
            pass

    # Wait duration (simulate ongoing process)
    if minutes is not None:
        await asyncio.sleep(minutes * 60)

    # finish
    manual_sessions_col.update_one({"chat_id": cid}, {"$set": {"status": "finished", "end_time": (await now_wib()).isoformat(), "mentioned": mentioned}})
    manual_logs_col.insert_one({"chat_id": cid, "mentioned": mentioned, "duration": desc, "time": (await now_wib()).isoformat()})
    await client.send_message(cid, f"✅ TagAll selesai selama {desc}. Mentioned: {mentioned} members.")

@app.on_message(filters.command("batal") & filters.group)
async def batal_cmd(client: Client, message: Message):
    cid = message.chat.id
    sess = manual_sessions_col.find_one({"chat_id": cid, "status": "running"})
    if not sess:
        return await message.reply_text("❌ Tidak ada proses TagAll manual yang sedang berjalan.")
    manual_sessions_col.update_one({"chat_id": cid}, {"$set": {"status": "cancelled", "cancelled_by": message.from_user.id}})
    await message.reply_text("🛑 Proses TagAll manual dihentikan oleh admin.")

if name == "main":
    logger.info("Manual TagAll bot starting...")
    app.run()
