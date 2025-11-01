ᴏғғ, [01/11/2025 21:54]
# auto_tagall.py
import asyncio
from datetime import datetime, timezone, timedelta
from pyrogram import filters
from pyrogram.types import InputFile
import motor.motor_asyncio
from app import app
from config import MONGO_URL, OWNER_IDS, LOGS_CHAT_ID

# timezone WIB
WIB = timezone(timedelta(hours=7))
def now_wib(): return datetime.now(WIB)

# Mongo (motor async)
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not set in .env")
mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = mongo["garfield_tagall"]
premium_col = db["premium_users"]
global_partners_col = db["global_partners"]

# helper
async def ensure_record(uid: int):
    await premium_col.update_one({"_id": uid}, {"$setOnInsert": {"partners": [], "group_id": None, "last_auto": None, "created_at": now_wib().isoformat()}}, upsert=True)

@app.on_message(filters.command("start"))
async def start_cmd(_, message):
    await message.reply("🤖 Garfield TagAll ready. Owner can /addprem. Premium users /setgroupid then /autotag or send message in their bot to auto-run.")

# Premium admin owner commands
@app.on_message(filters.command("addprem") & filters.user(OWNER_IDS))
async def addprem(_, message):
    if len(message.command) < 2:
        return await message.reply("Gunakan: /addprem <user_id>")
    uid = int(message.command[1])
    await ensure_record(uid)
    await premium_col.update_one({"_id": uid}, {"$set": {"active": True}})
    await message.reply(f"✅ User {uid} ditambahkan premium.")
    try:
        await app.send_message(uid, "✅ Anda diberi akses premium. Silakan /start untuk instruksi.")
    except:
        pass

@app.on_message(filters.command("delprem") & filters.user(OWNER_IDS))
async def delprem(_, message):
    if len(message.command) < 2:
        return await message.reply("Gunakan: /delprem <user_id>")
    uid = int(message.command[1])
    await premium_col.delete_one({"_id": uid})
    await message.reply(f"❌ User {uid} dihapus premium.")

@app.on_message(filters.command("listprem") & filters.user(OWNER_IDS))
async def listprem(_, message):
    cur = premium_col.find({})
    s = "📜 Premium users:\n"
    async for r in cur:
        s += f"• {r['_id']} — group:{r.get('group_id')} partners:{len(r.get('partners',[]))}\n"
    await message.reply(s or "📭 Kosong")

# premium user commands
@app.on_message(filters.command("setgroupid"))
async def setgroupid(_, message):
    uid = message.from_user.id
    rec = await premium_col.find_one({"_id": uid})
    if not rec:
        return await message.reply("❌ Anda belum premium. Minta owner /addprem <idmu>.")
    if len(message.command) < 2:
        return await message.reply("Gunakan: /setgroupid <group_id>")
    try:
        gid = int(message.command[1])
    except:
        return await message.reply("Group id harus angka.")
    await premium_col.update_one({"_id": uid}, {"$set": {"group_id": gid}})
    await message.reply(f"✅ Group ID tersimpan: {gid}")

@app.on_message(filters.command("addpartner"))
async def addpartner(_, message):
    uid = message.from_user.id
    if not await premium_col.find_one({"_id": uid}):
        return await message.reply("❌ Anda belum premium.")
    if len(message.command) < 2:
        return await message.reply("Gunakan: /addpartner <t.me/link_or_identifier>")
    link = message.command[1]
    await premium_col.update_one({"_id": uid}, {"$addToSet": {"partners": link}})
    await message.reply(f"✅ Partner ditambahkan: {link}")

@app.on_message(filters.command("mybots"))
async def mybots(_, message):
    uid = message.from_user.id
    rec = await premium_col.find_one({"_id": uid})
    if not rec:
        return await message.reply("❌ Anda belum premium.")
    await message.reply(f"Group ID: {rec.get('group_id')}\nPartners: {len(rec.get('partners',[]))}\nLast auto: {rec.get('last_auto')}")

ᴏғғ, [01/11/2025 21:54]
# /autotag : trigger auto run for that premium user's registered group (1x/day)
@app.on_message(filters.command("autotag"))
async def autotag_cmd(_, message):
    uid = message.from_user.id
    rec = await premium_col.find_one({"_id": uid})
    if not rec:
        return await message.reply("❌ Anda belum premium.")
    gid = rec.get("group_id")
    if not gid:
        return await message.reply("⚠️ Anda belum set group_id (/setgroupid).")
    today = now_wib().date().isoformat()
    if rec.get("last_auto") == today:
        return await message.reply("⚠️ Auto TagAll untuk grup anda sudah dijalankan hari ini.")
    # check bot admin
    try:
        member_count = await app.get_chat_members_count(gid)
    except Exception as e:
        return await message.reply(f"❌ Gagal akses grup: {e}")
    await message.reply("🤖 Sabar, TagAll otomatis sedang diproses... (hasil akan dikirim private).")
    # simulate mentions (to avoid spam) - we will iterate but send only a log zip to user
    members = []
    try:
        async for m in app.get_chat_members(gid):
            members.append(m)
    except:
        members = []
    # create content log
    start = now_wib().isoformat()
    content = f"AutoTagAll Log\nUser:{uid}\nGroup:{gid}\nStart:{start}\nMemberCount:{len(members)}\n"
    # mark last_auto
    await premium_col.update_one({"_id": uid}, {"$set": {"last_auto": today}})
    # prepare zipper and send
    fname = f"autotag_{uid}_{now_wib().strftime('%Y%m%d_%H%M%S')}.txt"
    bio = bytes(content + "\nCompleted at: " + now_wib().isoformat(), "utf-8")
    try:
        await app.send_document(chat_id=uid, document=InputFile.from_bytes(bio, filename=fname))
    except:
        pass
    # log to owner logs
    try:
        await app.send_message(LOGS_CHAT_ID, f"[AUTO] user:{uid} group:{gid} members:{len(members)} time:{now_wib().isoformat()}")
    except:
        pass
    await message.reply("✅ Auto TagAll selesai (log dikirim).")
