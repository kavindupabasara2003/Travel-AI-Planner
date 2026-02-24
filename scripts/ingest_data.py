import os
import pandas as pd
import json
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Clients
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    print("Error: Missing environment variables. Please check .env file.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

DATA_FILE = "data/SriLanka_Travel_Dataset_Final.csv"

def get_embedding(text):
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def ingest_data():
    if not os.path.exists(DATA_FILE):
        print(f"Error: Data file {DATA_FILE} not found.")
        return

    print(f"Loading data from {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    
    # Ensure columns exist
    required_cols = ['Location_Name', 'Located_City', 'Location', 'Location_Type', 'Avg_Rating', 'AI_Context']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Missing columns. Required: {required_cols}")
        return

    print(f"Found {len(df)} records. Starting ingestion...")
    
    success_count = 0
    error_count = 0

    for index, row in df.iterrows():
        try:
            # Generate Embedding
            ai_context = row['AI_Context']
            if pd.isna(ai_context) or str(ai_context).strip() == "":
                print(f"Skipping row {index}: Empty Context")
                continue
                
            embedding = get_embedding(str(ai_context))
            
            # Prepare Payload
            # Note: Ensure table 'destinations' exists in Supabase with 'embedding' column (vector)
            data = {
                "location_name": row['Location_Name'],
                "located_city": row['Located_City'],
                "location_address": row['Location'],
                "location_type": row['Location_Type'],
                "avg_rating": row['Avg_Rating'] if pd.notnull(row['Avg_Rating']) else None,
                "ai_context": ai_context,
                "embedding": embedding
                # Latitude/Longitude would go here if we had them
            }
            
            # Insert into Supabase
            response = supabase.table("destinations").insert(data).execute()
            if response.data:
                success_count += 1
                if success_count % 10 == 0:
                    print(f"Ingested {success_count} records...")
            else:
                 print(f"Failed to insert row {index}: No data returned")
                 error_count += 1

        except Exception as e:
            print(f"Error processing row {index} ({row.get('Location_Name')}): {e}")
            error_count += 1

    print(f"--- Ingestion Complete ---")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    ingest_data()
