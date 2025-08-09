import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
from io import BytesIO


load_dotenv()  # loading variables from .env


# ========== CONFIG ==========
# DATA_FOLDER = "data"
# CLEAN_DATA_FOLDER = "clean_data"
# FILE_DATE = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
# INPUT_FILE = f"../{DATA_FOLDER}/{FILE_DATE}.xlsx"
# CLEANED_FILE = f"../{CLEAN_DATA_FOLDER}/{FILE_DATE}_cleaned.csv"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

download_bucket = "daily-sales"
upload_bucket = "clean-food-sales"

FILE_DATE = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

INPUT_FILE_NAME = f"{FILE_DATE}.xlsx"
OUTPUT_FILE_NAME = f"{FILE_DATE}_cleaned.csv"

raw_file = supabase.storage.from_(download_bucket).download(INPUT_FILE_NAME)

# ========== STEP 1: CLEAN DATA ==========

df = pd.read_excel(raw_file).dropna().drop_duplicates()
df[['batch_code', 'item_name']] = df['Item'].str.split(' - ', n=1, expand=True)

df = df[['batch_code', 'item_name', 'Quantity']]
df[['batch_code', 'Quantity']] = df[['batch_code', 'Quantity']].astype(int)
df.rename(columns={'Quantity': 'quantity_sold'}, inplace=True)

df['date'] = FILE_DATE  # Add prev date

df.to_csv(OUTPUT_FILE_NAME, index=False)

print("✅ Data cleaned. - insert_food_sales.py:46")

# ========== STEP 2: LOAD FOOD ITEM IDS ==========
food_items = supabase.table("food_items").select("id, batch_code").execute().data
food_items_df = pd.DataFrame(food_items)
food_items_df["batch_code"] = food_items_df["batch_code"].astype(int)

print("✅ Data loaded from Database - insert_food_sales.py:53")


# ========== STEP 3: MERGE & INSERT TO Supabase ==========
sales_df = pd.read_csv(OUTPUT_FILE_NAME)
merged_df = sales_df.merge(food_items_df, on="batch_code", how="inner")

upload_df = merged_df[["id", "quantity_sold", "date"]].rename(columns={"id": "food_item_id"})

records = upload_df.to_dict("records")  # For inserting to Supabase

# Prepares the clean, transformed, and correctly mapped data so it can be inserted row-by-row into the food_sales table in Supabase.

# [
#     {"food_item_id": 12, "quantity_sold": 500, "date": "2025-07-14"},
#     {"food_item_id": 15, "quantity_sold": 300, "date": "2025-07-14"},
#     ...
# ]

supabase.table("food_sales").insert(records).execute()

print("✅ Data cleaned, matched, and uploaded successfully. - insert_food_sales.py:74")


# Step 4: Upload cleaned CSV to Storage
csv_buffer = BytesIO()
upload_df.to_csv(csv_buffer, index=False)
csv_buffer.seek(0)

supabase.storage.from_(upload_bucket).upload(
    OUTPUT_FILE_NAME,
    csv_buffer.read(),
    file_options={"content-type": "text/csv"}
)

print("✅ Clean CSV uploaded to Supabase Storage - insert_food_sales.py:88")