from supabase import create_client
from dotenv import load_dotenv
import os
import time

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

time.sleep(60)
supabase.rpc("refresh_daily_order_disposable").execute()