import socket
import psycopg2
from supabase import create_client

PROJECT_REF = "opdhrdjfuyqiqoqzselc"
SUPABASE_URL = f"https://{PROJECT_REF}.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9wZGhyZGpmdXlxaXFvcXpzZWxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc3MTU0NzMsImV4cCI6MjA4MzI5MTQ3M30.TkE3agxEZDEXVeyaDEAwUqVULVPAVY2GpnPlLAg2aDg"

print(f"--- DIAGNOSTIC FOR {PROJECT_REF} ---\n")

# 1. DNS Resolution
domains_to_check = [
    f"db.{PROJECT_REF}.supabase.co",
    f"{PROJECT_REF}.supabase.co",
    "aws-0-ap-south-1.pooler.supabase.com",
    "aws-0-ap-southeast-1.pooler.supabase.com",
    "aws-1-ap-southeast-1.pooler.supabase.com"
]

print("1. DNS RESOLUTION CHECK:")
for domain in domains_to_check:
    try:
        ip = socket.gethostbyname(domain)
        print(f"   ✅ {domain} -> {ip}")
    except socket.gaierror:
        print(f"   ❌ {domain} -> FAILED TO RESOLVE")

# 2. API Status Check
print("\n2. SUPABASE API CHECK:")
try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Just checking if we can talk to the server
    health = client.table("test").select("*").limit(0).execute() 
    print("   ✅ API is reachable (Project is Active)")
except Exception as e:
    print(f"   ⚠️ API Check Failed: {e}")

# 3. Port Check (Connectivity)
print("\n3. PORT REACHABILITY CHECK (Timeout 3s):")
hosts_to_check = [
     ("aws-1-ap-southeast-1.pooler.supabase.com", 6543),
     ("aws-0-ap-south-1.pooler.supabase.com", 6543),
     (f"db.{PROJECT_REF}.supabase.co", 5432)
]

for host, port in hosts_to_check:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        if result == 0:
             print(f"   ✅ {host}:{port} -> OPEN")
        else:
             print(f"   ❌ {host}:{port} -> CLOSED/BLOCKED (Err: {result})")
        sock.close()
    except Exception as e:
        print(f"   ❌ {host}:{port} -> ERROR ({e})")
