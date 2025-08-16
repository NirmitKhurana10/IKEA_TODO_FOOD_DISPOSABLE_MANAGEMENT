from supabase import create_client
from dotenv import load_dotenv
import os
import time

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

time.sleep(60)
try:
    supabase.rpc("refresh_disposable_daily_usage_view").execute()
    print("✅ Procedure Executed Successfully")
except Exception as e:
    print(f"Error occured while executing refresh_daily_disposable_usage_view.py: {e}")
    
