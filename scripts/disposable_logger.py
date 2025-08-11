from datetime import timedelta, datetime
from supabase import create_client
import time
from dotenv import load_dotenv
import os
import pytz


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

time.sleep(60)

usage = supabase.table("disposable_daily_usage").select("*").execute().data
# print(usage)


tz = pytz.timezone("America/Toronto")
yesterday = (datetime.now(tz) - timedelta(days=1)).date()


rows_to_upsert = []
for entry in usage:
    rows_to_upsert.append({
        "log_date": yesterday,
        "disposable_id": entry["disposable_id"],
        "quantity_used": entry["quantity_used"],
        "disposable_name": entry["disposable_name"]
    })

supabase.table("disposable_usage_log").upsert(rows_to_upsert).execute()
    
# Executing SQL Stored procedure to deduct stock
    
supabase.rpc("update_stock_after_sales").execute()

