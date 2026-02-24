import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables
load_dotenv()

# Fetch URI
uri = os.getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

print(f"Connecting to MongoDB Atlas...")

try:
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # List databases to confirm info access
    dbs = client.list_database_names()
    print(f"Databases found: {dbs}")

except Exception as e:
    print(e)
