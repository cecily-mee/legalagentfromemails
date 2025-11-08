##for creating database structure
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["email_automation"]
emails_collection = db["emails"]
