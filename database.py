from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Read Atlas URL from .env (must include your DB name)
MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise ValueError("❌ MONGO_URL not found in .env. Please add your Atlas connection string.")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URL)

# Database name should match the one in the URL or be consistent
db = client.get_database()

# Collections
users_collection = db["users"]
chats_collection = db["chats"]
