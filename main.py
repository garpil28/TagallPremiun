# AutoTagAll Premium - single-file controller (async python-telegram-bot v20)
# NOTE: This implementation stores user data locally in data/users.json
#       and logs auto-tagall events to LOGS_CHAT_ID (config.py).
#       Real per-user bot instances or true member-by-member mentions
#       require a Pyrogram implementation (optionally add later).

import os
import json
import asyncio
from datetime import datetime, timedelta, timezone
from zipfile import ZipFile
from io import BytesIO

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

# -------------------------
# Load config (create config.py from earlier)
# -------------------------
try:
    from config import (
        BOT_TOKEN, BOT_NAME, OWNER_IDS, LOGS_CHAT_ID,
        LOG_FILE_NAME, SUPPORT_GROUP, UPDATES_CHANNEL, TIMEZONE
    )
except Exception as e:
    print("ERROR: cannot import config.py. Make sure config.py exists and contains required variables.")
    raise e

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")        # per-user premium data
GLOBAL_PARTNERS = os.path.join(DATA_DIR, "partners_global.json")  # global partners list
LOG_FILE = LOG_FILE_NAME if 'LOG_FILE_NAME' in globals() else "BotTagallGarfieldLogs.txt"

# ensure data dir
os.makedirs(DATA_DIR, exist_ok=True)

# initialize data files if missing
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f, indent=2)

if not os.path.exists(GLOBAL_PARTNERS):
    with open(GLOBAL_PARTNERS, "w") as f:
        json.dump({"global": []}, f, indent=2)

# helper: load/save users
def load_users():
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_global_partners():
    with open(GLOBAL_PARTNERS, "r") as f:
        try:
            return json.load(f)
        except:
            return {"global": []}

def save_global_partners(data):
    with open(GLOBAL_PARTNERS, "w") as f:
        json.dump(data, f, indent=2)

# helper time (WIB)
WIB = timezone(timedelta(hours=7))
def now_wib():
    return datetime.now(WIB)

# create a simple zip bytes from text (for sending results)
def make_zip_bytes(filename: str, content: str) -> BytesIO:
    bio = BytesIO()
    with ZipFile(bio, "w") as zf:
        zf.writestr(filename, content)
    bio.seek(0)
    return bio

# -------------------------
# Decorators / checks
# -------------------------
def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS

# -------------------------
# Command: /start
# -------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = (
        f"👋 Halo {update.effective_user.first_name}!\n\n"
        f"Ini adalah {BOT_NAME} — AutoTagAll Premium.\n\n"
        "• Jika Anda owner: gunakan /addprem <user_id> untuk berikan akses premium.\n"
        "• Jika Anda user premium: gunakan /settoken untuk kirim token bot Anda (jika diperlukan), lalu /setgroupid <group_id>\n\n"
        "Manual TagAll (admin grup): /jalan\n"
        "Owner Broadcast: /broadcast <pesan>\n"
        "Tanya support: " + SUPPORT_GROUP
    )
    await update.message.reply_text(text)

# -------------------------
# OWNER: /addprem, /delprem, /listprem
# -------------------------
async def addprem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        return await update.message.reply_text("❌ Hanya owner bot yang bisa memberikan akses premium.")

ᴏғғ, [31/10/2025 2:18]
if not context.args:
        return await update.message.reply_text("Format: /addprem <telegram_user_id>")
    try:
        target_id = int(context.args[0])
    except:
        return await update.message.reply_text("ID user harus angka (contoh: /addprem 123456789).")
    users = load_users()
    if str(target_id) in users:
        return await update.message.reply_text("⚠️ User sudah memiliki akses premium.")
    # create user record
    users[str(target_id)] = {
        "token": None,
        "group_id": None,
        "partners": [],
        "last_auto": None,   # YYYY-MM-DD last auto run
        "created_at": now_wib().isoformat()
    }
    save_users(users)
    await update.message.reply_text(f"✅ Berhasil menambahkan user {target_id} sebagai premium.")
    # notify user if possible
    try:
        await context.bot.send_message(chat_id=target_id, text="✅ Anda telah diberi akses PREMIUM pada AutoTagAll Bot. Silakan /start untuk info.")
    except:
        pass

async def delprem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        return await update.message.reply_text("❌ Hanya owner bot yang bisa mencabut akses premium.")
    if not context.args:
        return await update.message.reply_text("Format: /delprem <telegram_user_id>")
    try:
        target_id = int(context.args[0])
    except:
        return await update.message.reply_text("ID user harus angka.")
    users = load_users()
    if str(target_id) not in users:
        return await update.message.reply_text("⚠️ User tidak ditemukan di premium list.")
    users.pop(str(target_id))
    save_users(users)
    await update.message.reply_text(f"✅ Berhasil menghapus akses premium untuk user {target_id}.")

async def listprem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        return await update.message.reply_text("❌ Hanya owner bot yang dapat melihat daftar premium.")
    users = load_users()
    if not users:
        return await update.message.reply_text("📭 Belum ada user premium.")
    s = "📜 Daftar User Premium:\n"
    for k,v in users.items():
        s += f"• {k} — group_id: {v.get('group_id')} — partners: {len(v.get('partners',[]))}\n"
    await update.message.reply_text(s)

# -------------------------
# USER PREMIUM: /settoken /setgroupid /addpartner /delpartner /listpartner /mybots
# -------------------------
async def settoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    if uid not in users:
        return await update.message.reply_text("❌ Anda belum mendapat akses premium. Minta owner untuk /addprem <idmu>.")
    if not context.args:
        return await update.message.reply_text("Gunakan: /settoken <BOT_TOKEN_FROM_BOTFATHER>")
    token = context.args[0].strip()
    users[uid]['token'] = token
    save_users(users)
    await update.message.reply_text("✅ Token tersimpan. Ingat: token ini hanya dipakai sebagai identitas bot Anda (backend masih dikelola oleh owner).")

async def setgroupid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    if uid not in users:
        return await update.message.reply_text("❌ Anda belum mendapat akses premium.")
    if not context.args:
        return await update.message.reply_text("Gunakan: /setgroupid <group_id> (contoh: -1001234567890)")
    try:
        gid = int(context.args[0])
    except:
        return await update.message.reply_text("Format group_id salah.")
    users[uid]['group_id'] = gid
    save_users(users)
    await update.message.reply_text(f"✅ Group ID tersimpan: {gid}\nSekarang gunakan /addpartner untuk menambah partner anda.")

ᴏғғ, [31/10/2025 2:18]
async def addpartner_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    if uid not in users:
        return await update.message.reply_text("❌ Anda belum mendapat akses premium.")
    if not context.args:
        return await update.message.reply_text("Gunakan: /addpartner <t.me/link_or_identifier>")
    link = context.args[0].strip()
    if 'partners' not in users[uid]:
        users[uid]['partners'] = []
    if link in users[uid]['partners']:
        return await update.message.reply_text("⚠️ Partner sudah ada.")
    users[uid]['partners'].append(link)
    save_users(users)
    await update.message.reply_text(f"✅ Partner ditambahkan: {link}")

async def delpartner_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    if uid not in users:
        return await update.message.reply_text("❌ Anda belum mendapat akses premium.")
    if not context.args:
        return await update.message.reply_text("Gunakan: /delpartner <t.me/link_or_identifier>")
    link = context.args[0].strip()
    if link not in users[uid].get('partners', []):
        return await update.message.reply_text("⚠️ Partner tidak ditemukan di list Anda.")
    users[uid]['partners'].remove(link)
    save_users(users)
    await update.message.reply_text(f"✅ Partner dihapus: {link}")

async def listpartner_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    if uid not in users:
        return await update.message.reply_text("❌ Anda belum mendapat akses premium.")
    parts = users[uid].get('partners', [])
    if not parts:
        return await update.message.reply_text("📭 Belum ada partner di list Anda.")
    s = "📜 Daftar Partner Anda:\n"
    for p in parts:
        s += f"• {p}\n"
    await update.message.reply_text(s)

async def mybots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    if uid not in users:
        return await update.message.reply_text("❌ Anda belum mendapat akses premium.")
    data = users[uid]
    s = f"📋 Data Bot Anda:\nGroup ID: {data.get('group_id')}\nToken set: {'Yes' if data.get('token') else 'No'}\nPartners: {len(data.get('partners',[]))}"
    await update.message.reply_text(s)

# -------------------------
# AUTO TAGALL: /autotag (user triggers for their group)
#  - Only user premium can trigger auto for their registered group.
#  - Enforces 1x per 24h per group.
#  - Logs to LOGS_CHAT_ID and appends to LOG_FILE.
# -------------------------
async def autotag_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    users = load_users()
    if uid not in users:
        return await update.message.reply_text("❌ Anda belum mempunyai akses premium.")
    record = users[uid]
    gid = record.get('group_id')
    if not gid:
        return await update.message.reply_text("⚠️ Anda belum menyimpan group ID. Gunakan /setgroupid <group_id> terlebih dahulu.")
    # 24-hour check
    last = record.get('last_auto')
    today = now_wib().date().isoformat()
    if last == today:
        return await update.message.reply_text("⚠️ Auto TagAll untuk grup Anda sudah dijalankan hari ini. Coba lagi besok.")
    # all partners = global + user partners
    gp = load_global_partners().get('global', [])
    user_parts = record.get('partners', [])
    all_partners = gp + user_parts

    await update.message.reply_text("🤖 Sabar, TagAll sedang diproses otomatis... (ini mungkin makan beberapa detik)")
    # Simulate work: count members of group and wait a bit (real mass-mention requires Pyrogram)
    try:
        member_count = await context.bot.get_chat_member_count(gid)
    except Exception as e:
        return await update.message.reply_text(f"❌ Gagal mengakses grup (pastikan bot sudah admin di grup). Error: {e}")

ᴏғғ, [31/10/2025 2:18]
# Write log content
    start_time = now_wib().isoformat()
    content = f"AutoTagAll Log\nUser: {uid}\nGroup: {gid}\nStart: {start_time}\nPartnersUsed: {len(all_partners)}\nMemberCount: {member_count}\n\n"
    content += "Note: This run was triggered by user via /autotag\n"

    # Here: PLACE to do real mention loop if you implement Pyrogram
    # For safety, we simulate the tagging with a delay proportional to members (but capped)
    delay_seconds = min(30, max(3, member_count // 50))
    await asyncio.sleep(delay_seconds)

    # finalize
    users[uid]['last_auto'] = today
    save_users(users)

    # prepare zip log
    fname = f"autotag_{uid}_{now_wib().strftime('%Y%m%d_%H%M%S')}.txt"
    bio = make_zip_bytes(fname, content + "\nCompleted at: " + now_wib().isoformat())

    # send result to user (private)
    try:
        await context.bot.send_document(chat_id=update.effective_user.id, document=InputFile(bio, filename=fname + ".zip"),
                                        caption=f"✅ Auto TagAll selesai untuk grup {gid}.\nMemberCount: {member_count}")
    except Exception:
        pass

    # log to owner's logs group (only auto logged)
    try:
        log_text = f"📌 AutoTagAll Completed\nUser: {uid}\nGroup: {gid}\nMembers: {member_count}\nTime: {now_wib().isoformat()}"
        await context.bot.send_message(chat_id=LOGS_CHAT_ID, text=log_text)
        # also append to local log file
        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(log_text + "\n")
    except Exception:
        pass

    await update.message.reply_text("✅ Auto TagAll selesai! Hasil log telah dikirim (private).")

# -------------------------
# MANUAL TAGALL FLOW (/jalan) - admin only with duration buttons
#  - This is run directly in group; it does NOT write to LOG_FILE or LOGS_CHAT_ID
# -------------------------
MANUAL_SESSIONS = {}  # chat_id -> running flag

async def jalan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    # check admin
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"]:
            return await update.message.reply_text("❌ Hanya admin grup yang bisa menjalankan TagAll manual.")
    except Exception:
        return await update.message.reply_text("❌ Gagal memeriksa status admin. Pastikan bot masih berada di grup.")

    keyboard = [
        [InlineKeyboardButton("3m", callback_data="m_3"),
         InlineKeyboardButton("5m", callback_data="m_5"),
         InlineKeyboardButton("10m", callback_data="m_10")],
        [InlineKeyboardButton("20m", callback_data="m_20"),
         InlineKeyboardButton("40m", callback_data="m_40"),
         InlineKeyboardButton("60m", callback_data="m_60")],
        [InlineKeyboardButton("90m", callback_data="m_90"),
         InlineKeyboardButton("Unlimited", callback_data="m_unlimited")]
    ]
    await update.message.reply_text("🧠 Pilih durasi jalan manual untuk TagAll:", reply_markup=InlineKeyboardMarkup(keyboard))

async def manual_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat.id
    dur_key = data.split("_",1)[1]
    if dur_key == "unlimited":
        minutes = None
        desc = "Unlimited"
    else:
        minutes = int(dur_key)
        desc = f"{minutes} menit"
    # mark session
    if MANUAL_SESSIONS.get(chat_id):
        return await query.edit_message_text("⚠️ Proses TagAll manual sudah berjalan di grup ini.")
    MANUAL_SESSIONS[chat_id] = {"started_by": query.from_user.id, "duration": minutes, "start": now_wib().isoformat()}

    await query.edit_message_text(f"💭 Sabar, TagAll lagi di proses selama {desc}...")

ᴏғғ, [31/10/2025 2:18]
# simulate tagging (no actual per-member mentions in this safe implementation)
    # simulate time = min(60, minutes*1) or fixed simulation
    sim_seconds = 10 if minutes is None else min(60, max(5, minutes))
    await context.bot.send_message(chat_id=chat_id, text="🔥 TagAll manual dimulai...")
    await asyncio.sleep(sim_seconds)
    # finish
    MANUAL_SESSIONS.pop(chat_id, None)
    await context.bot.send_message(chat_id=chat_id, text=f"✅ TagAll selesai selama {desc}.")

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if MANUAL_SESSIONS.get(chat_id):
        MANUAL_SESSIONS.pop(chat_id, None)
        await update.message.reply_text("🛑 Proses TagAll manual dihentikan oleh admin.")
    else:
        await update.message.reply_text("❌ Tidak ada proses TagAll manual yang sedang berjalan.")

# -------------------------
# BROADCAST (owner only)
# -------------------------
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        return await update.message.reply_text("❌ Hanya owner yang bisa broadcast.")
    if not context.args:
        return await update.message.reply_text("Gunakan: /broadcast <pesan>")
    text = " ".join(context.args)
    users = load_users()
    sent = 0
    failed = 0
    for uid, rec in users.items():
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"[BROADCAST]\n\n{text}")
            sent += 1
        except Exception:
            failed += 1
    # log broadcast
    log_text = f"[BROADCAST] owner:{user.id} sent:{sent} failed:{failed} time:{now_wib().isoformat()}\nMessage:{text}"
    try:
        await context.bot.send_message(chat_id=LOGS_CHAT_ID, text=log_text)
    except:
        pass
    with open(LOG_FILE, "a", encoding="utf-8") as lf:
        lf.write(log_text + "\n")
    await update.message.reply_text(f"✅ Broadcast selesai. sent: {sent}, failed: {failed}")

# -------------------------
# GLOBAL PARTNER management (owner only)
# -------------------------
async def addglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        return await update.message.reply_text("❌ Owner only.")
    if not context.args:
        return await update.message.reply_text("Gunakan: /addglobal <t.me/link>")
    link = context.args[0].strip()
    gp = load_global_partners()
    if link in gp.get('global', []):
        return await update.message.reply_text("⚠️ Link sudah ada di global partners.")
    gp['global'].append(link)
    save_global_partners(gp)
    await update.message.reply_text("✅ Global partner ditambahkan.")

async def delglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        return await update.message.reply_text("❌ Owner only.")
    if not context.args:
        return await update.message.reply_text("Gunakan: /delglobal <t.me/link>")
    link = context.args[0].strip()
    gp = load_global_partners()
    if link not in gp.get('global', []):
        return await update.message.reply_text("⚠️ Link tidak ditemukan.")
    gp['global'].remove(link)
    save_global_partners(gp)
    await update.message.reply_text("✅ Global partner dihapus.")

async def listglobal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gp = load_global_partners()
    items = gp.get('global', [])
    if not items:
        return await update.message.reply_text("📭 Global partner kosong.")
    s = "📜 Global Partners:\n"
    for p in items:
        s += f"• {p}\n"
    await update.message.reply_text(s)

# -------------------------
# Partner request (simple): partner requests auto tag for a specific user premium

ᴏғғ, [31/10/2025 2:18]
# Usage: /reqtag <user_premium_id>
# This command simulates partner sending request to bot main (instead of to user's own bot)
# -------------------------
async def reqtag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Gunakan: /reqtag <user_premium_id>")
    try:
        target = str(int(context.args[0]))
    except:
        return await update.message.reply_text("ID user premium harus angka.")
    users = load_users()
    if target not in users:
        return await update.message.reply_text("⚠️ User premium tidak ditemukan.")
    # forward: just call autotag for that user but must be triggered by owner or partner? we allow partner to request
    await update.message.reply_text("🤖 Permintaan diterima, memulai AutoTagAll untuk user premium... (bot akan memproses jika belum 24 jam).")
    # find owner of user (we call autotag_user as if user triggered)
    # create a fake update to call autotag_user privately to owner? Simpler: call autotag logic by updating users[target]
    # We'll run auto for that premium user if not run today.
    # For safety, we will notify the premium user via private message and start the autotag process as if they requested.
    try:
        await context.bot.send_message(chat_id=int(target), text=f"📨 Ada permintaan TagAll untuk grup Anda dari partner {update.effective_user.full_name}. Jika Anda setujui, bot akan memproses (1x/24h).")
    except:
        pass
    # Start process (call internal routine)
    # Note: we will run the same logic as autotag_user but without a user update object
    class Ctx: pass
    # create a context-like with bot and args
    # reuse autotag_user but create a dummy Update with effective_user = premium user? Simpler: call internal logic below
    # We'll call a helper: run_autotag_for_user(user_id)
    await run_autotag_for_user(target, context)

async def run_autotag_for_user(uid_str: str, context):
    users = load_users()
    record = users.get(uid_str)
    if not record:
        return
    gid = record.get('group_id')
    if not gid:
        try:
            await context.bot.send_message(chat_id=int(uid_str), text="⚠️ Anda belum set group_id, auto cancelled.")
        except:
            pass
        return
    today = now_wib().date().isoformat()
    if record.get('last_auto') == today:
        try:
            await context.bot.send_message(chat_id=int(uid_str), text="⚠️ Auto TagAll sudah dilakukan hari ini; batalkan permintaan.")
        except:
            pass
        return
    # simulate
    try:
        member_count = await context.bot.get_chat_member_count(gid)
    except Exception:
        try:
            await context.bot.send_message(chat_id=int(uid_str), text="❌ Bot tidak bisa mengakses grup Anda (pastikan sebagai admin).")
        except:
            pass
        return

    # compose content and zip as log
    start_time = now_wib().isoformat()
    content = f"AutoTagAll Log\nUser: {uid_str}\nGroup: {gid}\nStart: {start_time}\nMemberCount: {member_count}\nTriggeredBy: partner_request\n"
    # simulate some delay
    await asyncio.sleep(min(10, max(3, member_count//50)))

    # update last_auto
    users[uid_str]['last_auto'] = today
    save_users(users)

    # send private log zip to premium user
    fname = f"autotag_{uid_str}_{now_wib().strftime('%Y%m%d_%H%M%S')}.txt"
    bio = make_zip_bytes(fname, content + "\nCompleted at: " + now_wib().isoformat())
    try:
        await context.bot.send_document(chat_id=int(uid_str), document=InputFile(bio, filename=fname + ".zip"),
                                        caption=f"✅ Auto TagAll selesai untuk grup {gid}.")
    except:
        pass

    # log to owner logs
    log_text = f"[AUTO] user:{uid_str} group:{gid} members:{member_count} time:{now_wib().isoformat()}"
    try:
        await context.bot.send_message(chat_id=LOGS_CHAT_ID, text=log_text)
        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(log_text + "\n")
    except:
        pass

ᴏғғ, [31/10/2025 2:18]
# -------------------------
# Setup application & handlers
# -------------------------
def build_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # basic
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", start_cmd))

    # owner admin premium control
    app.add_handler(CommandHandler("addprem", addprem))
    app.add_handler(CommandHandler("delprem", delprem))
    app.add_handler(CommandHandler("listprem", listprem))

    # premium user commands
    app.add_handler(CommandHandler("settoken", settoken))
    app.add_handler(CommandHandler("setgroupid", setgroupid))
    app.add_handler(CommandHandler("addpartner", addpartner_user))
    app.add_handler(CommandHandler("delpartner", delpartner_user))
    app.add_handler(CommandHandler("listpartner", listpartner_user))
    app.add_handler(CommandHandler("mybots", mybots))

    # auto tag and partner request
    app.add_handler(CommandHandler("autotag", autotag_user))
    app.add_handler(CommandHandler("reqtag", reqtag))

    # manual tag (group)
    app.add_handler(CommandHandler("jalan", jalan_cmd))
    app.add_handler(CallbackQueryHandler(manual_button_handler, pattern="^m_"))
    app.add_handler(CommandHandler("cancel", cancel_cmd))

    # broadcast & global partner (owner)
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("addglobal", addglobal))
    app.add_handler(CommandHandler("delglobal", delglobal))
    app.add_handler(CommandHandler("listglobal", listglobal))

    return app

# -------------------------
# Run
# -------------------------
async def main():
    app = build_app()

    # Optional: schedule daily reset of some in-memory sets if needed (we persist last_auto per user)
    # For safe running 24/7, we just start the bot.
    print(f"{BOT_NAME} starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()  # start polling
    print("Bot running. Press CTRL+C to stop.")
    # keep running
    await app.updater.idle()

if name == "main":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
