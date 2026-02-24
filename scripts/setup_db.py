import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA_FILE = "backend/supabase_schema.sql"

def setup_database():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env")
        return

    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: Schema file {SCHEMA_FILE} not found.")
        return

    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print(f"Reading schema from {SCHEMA_FILE}...")
        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()
            
        print("Executing schema...")
        cur.execute(schema_sql)
        conn.commit()
        
        print("--- SUCCESS: Database tables created ---")
        
        # Verify
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        print("Current tables:", [t[0] for t in tables])
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    setup_database()
