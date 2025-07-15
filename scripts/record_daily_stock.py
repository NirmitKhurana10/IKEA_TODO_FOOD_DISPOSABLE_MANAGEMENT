from datetime import timedelta, date
from supabase import create_client, Client
from dotenv import load_dotenv
import os


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

usage = supabase.table("disposable_daily_usage").select("*").execute().data
print(usage)

yesterday = date.today() - timedelta(days=1)

for entry in usage:
    disp_id = entry["disposable_id"]
    used_qty = entry["quantity_used"]
    disp_name = entry["disposable_name"]

    supabase.table("disposable_usage_log").insert({
    "disposable_name":disp_name,
    "disposable_id": disp_id,
    "quantity_used": used_qty,
    "log_date": str(yesterday)
        }).execute()
    
    
# Executing SQL Stored procedure to deduct stock
    
supabase.rpc("update_stock_after_sales").execute()