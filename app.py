from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, LOGS_CHAT_ID

app = Client(
    "GarfieldTagallSession",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# import modul AFTER app created so modules can import app
import manual_tagall   # Handlers manual tagall (buttons, cancel)
import auto_tagall     # Auto/premium logic (autotag, setgroupid, partners, db)

if name == "main":
    print(f"[🚀] Starting {BOT_NAME} ...")
    app.start()
    print("[✅] Bot running. Press CTRL+C to stop.")
    idle()
    print("[🛑] Bot stopped.")
