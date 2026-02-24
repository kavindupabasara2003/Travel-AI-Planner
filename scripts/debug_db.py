import psycopg2
import sys
import os
from supabase import create_client, Client

# Load env variables directly for test
PROJECT_REF = "opdhrdjfuyqiqoqzselc"
PASSWORD = "kavindupabasara"
SUPABASE_URL = f"https://{PROJECT_REF}.supabase.co"
# The anon key provided in .env (truncated in thought, but assuming it's loaded or I use the user's latest if provided)
# Using the values from the previously read .env file for the keys
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9wZGhyZGpmdXlxaXFvcXpzZWxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc3MTU0NzMsImV4cCI6MjA4MzI5MTQ3M30.TkE3agxEZDEXVeyaDEAwUqVULVPAVY2GpnPlLAg2aDg"

def test_api():
    print(f"\n--- Testing Supabase API ({SUPABASE_URL}) ---")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Try a simple select. Even if table doesn't exist, it should return a response, not a connection error.
        response = supabase.table("destinations").select("*").limit(1).execute()
        print("✅ API SUCCESS! Connected to Supabase API.")
        print(f"Data sample: {response.data}")
        return True
    except Exception as e:
        print(f"❌ API FAILED: {e}")
        return False

def test_sql():
    regions = [
        "ap-south-1",      # Mumbai
        "ap-southeast-1",  # Singapore
        "us-east-1",       # N. Virginia
        "eu-central-1",    # Frankfurt
        "eu-west-1",       # Ireland
        "us-west-1",       # N. California
        "sa-east-1",       # Sao Paulo
        "ap-northeast-1",  # Tokyo
        "ap-northeast-2",  # Seoul
        "ca-central-1",    # Canada
        "eu-west-2",       # London
        "eu-west-3",       # Paris
    ]

    print(f"\n--- Testing SQL Connections (Project: {PROJECT_REF}) ---")
    
    # 1. Test "Direct" (Just in case DNS flaked)
    print(f"\n[Test 1] Direct Connection (db.{PROJECT_REF}.supabase.co)")
    try:
        conn = psycopg2.connect(
            host=f"db.{PROJECT_REF}.supabase.co",
            port=5432,
            user="postgres",
            password=PASSWORD,
            dbname="postgres",
            connect_timeout=3
        )
        print("✅ DIRECT SQL SUCCESS! (This is best)")
        conn.close()
        return
    except Exception as e:
        print(f"❌ Direct Failed: {str(e).strip()}")

    # 2. Scan Poolers
    print(f"\n[Test 2] Scanning Pooler Regions...")
    for region in regions:
        host = f"aws-0-{region}.pooler.supabase.com"
        user = f"postgres.{PROJECT_REF}"
        
        # We try to connect. 
        # If we get "Tenant not found", region is wrong.
        # If we get "Password auth failed", REGION IS RIGHT (but pass is wrong).
        # If we get Connected, Everything is right.
        
        sys.stdout.write(f"Testing {region: <15} ")
        try:
            conn = psycopg2.connect(
                host=host,
                port=6543,
                user=user,
                password=PASSWORD,
                dbname="postgres",
                connect_timeout=3
            )
            print("✅ SUCCESS!!!")
            url = f"postgresql://{user}:{PASSWORD}@{host}:6543/postgres"
            print(f"\n >>> FOUND MATCHING REGION: {region}")
            print(f" >>> RECOMMENDED URL: {url}")
            return
        except psycopg2.OperationalError as e:
            msg = str(e).strip()
            if "password authentication failed" in msg:
                 print(f"⚠️  FOUND REGION ({region}) BUT PASSWORD FAILED!")
                 print("   -> The Project is definitely in this region.")
                 print("   -> Please check your database password.")
                 return
            elif "Tenant or user not found" in msg:
                print("❌ Tenant Not Found")
            else:
                print(f"❌ Error: {msg}")
        except Exception as e:
             print(f"❌ Error: {str(e).strip()}")

if __name__ == "__main__":
    if test_api():
        test_sql()
    else:
        print("\n⚠️ API Connection failed. The project might be paused or URL/Key is invalid.")
