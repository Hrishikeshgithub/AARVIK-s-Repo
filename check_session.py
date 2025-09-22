# Save as check_session.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME")]
session = db.sessions.find_one({"session_id": "aeb31dc0-e117-4227-859b-995b0fe9f893"})
print(session)
client.close()