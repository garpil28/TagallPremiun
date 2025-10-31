from pymongo import MongoClient
from config import DATABASE_URL, DATABASE_NAME

client = MongoClient(DATABASE_URL)
db = client[DATABASE_NAME]

# Collections for auto-tagall (owner / premium)
premium_users_col = db["premium_users"]     # documents: { "_id": user_id, "group_id": ..., "last_auto": "YYYY-MM-DD", ... }
partners_col = db["global_partners"]       # documents: { "_id": link_or_identifier, "meta": {...} }
auto_logs_col = db["auto_logs"]            # run logs
