from pymongo import MongoClient
import os
from django.conf import settings

class MongoDBClient:
    _instance = None

    @classmethod
    def get_db(cls):
        if cls._instance is None:
            mongo_uri = os.environ.get('MONGO_URI')
            if not mongo_uri:
                raise ValueError("MONGO_URI not found in environment variables")
            
            client = MongoClient(mongo_uri)
            # Verify connection
            try:
                client.admin.command('ping')
                print("✅ Connected to MongoDB Atlas")
            except Exception as e:
                print(f"❌ Failed to connect to MongoDB: {e}")
                raise e
            
            db_name = os.environ.get('DB_NAME', 'travel_ai_db')
            cls._instance = client[db_name]
        
        return cls._instance

# usage: db = MongoDBClient.get_db()
# users_collection = db['users']
