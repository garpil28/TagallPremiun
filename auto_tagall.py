import asyncio
import random
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMembersFilter

from emoji_list import EMOJIS

# ───────────────────────────────
# Cache per chat (auto process)
# ───────────────────────────────
AUTO_TASKS = {}

# ───────────────────────────────
# Helper: cek admin
# ───────────────────────────────
async def is_admin(client, chat_id, user_id):
    try:
        async for admin in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if admin.user.id == user_id:
                return True
    except Exception:
        pass
    return False

# ───────────────────────────────
# Trigger utama (dipanggil otomatis dari app.py)
# ───────────────────────────────
async def trigger_auto_tagall(client: Client, message):
    """
    Dijalankan otomatis bila ada link t.me di group.
    Admin / partner bisa pakai, otomatis berhenti setelah durasi tertentu.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id in AUTO_TASKS:
        # udah jalan auto tagall
        return

    # pastikan hanya admin/partner yang bisa trigger
    if not await is_admin(client, chat_id, user_id):
        return

    text = f"<b>🔗 Deteksi tautan otomatis!</b>\n\n{message.text or ''}"

    durasi = 300  # 5 menit default
    AUTO_TASKS[chat_id] = asyncio.create_task(run_auto_tagall(client, chat_id, text, durasi, message))

# ───────────────────────────────
# Proses utama auto tagall
# ───────────────────────────────
async def run_auto_tagall(client, chat_id, text, duration, trigger_msg):
    start_time = asyncio.get_event_loop().time()
    mention_buffer = []
    count = 0

    try:
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🛑 Stop AutoTag", callback_data=f"autotag:cancel:{chat_id}")]]
        )
        msg = await trigger_msg.reply_text(
            f"<b>▶️ Auto TagAll aktif selama {duration//60} menit...</b>",
            reply_markup=btn,
        )

        async for member in client.get_chat_members(chat_id):
            if asyncio.get_event_loop().time() - start_time > duration:
                break
            if chat_id not in AUTO_TASKS:
                break
            if member.user.is_bot or member.user.is_deleted:
                continue

            count += 1
            emoji = random.choice(EMOJIS)
            mention_buffer.append(f"[{emoji}](tg://user?id={member.user.id})")

            if len(mention_buffer) == 5:
                teks = (
                    f"<blockquote>{text}</blockquote>\n\n"
                    f"{' '.join(mention_buffer)}\n\n"
                    f"<blockquote><i>@storegarf</i></blockquote>"
                )
                try:
                    await client.send_message(
                        chat_id,
                        teks,
                        disable_web_page_preview=True,
                        reply_markup=btn,
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                await asyncio.sleep(2)
                mention_buffer.clear()

        if mention_buffer:
            teks = (
                f"<blockquote>{text}</blockquote>\n\n"
                f"{' '.join(mention_buffer)}\n\n"
                f"<blockquote><i>@storegarf</i></blockquote>"
            )
            await client.send_message(
                chat_id,
                teks,
                disable_web_page_preview=True,
                reply_markup=btn,
            )

        await client.send_message(
            chat_id,
            f"<blockquote>✅ Auto TagAll selesai! Total {count} member ditag.</blockquote>",
        )

    except Exception as e:
        await client.send_message(chat_id, f"❌ Gagal auto tagall: {e}")
    finally:
        AUTO_TASKS.pop(chat_id, None)
        try:
            await msg.edit_reply_markup(None)
        except:
            pass
