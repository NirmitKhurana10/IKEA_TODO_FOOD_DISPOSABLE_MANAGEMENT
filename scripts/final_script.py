import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

load_dotenv()  # loading variables from .env


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# ========== CONFIG ==========
DATA_FOLDER = "data"
CLEAN_DATA_FOLDER = "clean_data"
FILE_DATE = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
INPUT_FILE = f"../{DATA_FOLDER}/{FILE_DATE}.xlsx"
CLEANED_FILE = f"../{CLEAN_DATA_FOLDER}/{FILE_DATE}_cleaned.csv"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== STEP 1: CLEAN DATA ==========
df = pd.read_excel(INPUT_FILE).dropna().drop_duplicates()
df[['batch_code', 'item_name']] = df['Item'].str.split(' - ', n=1, expand=True)

df = df[['batch_code', 'item_name', 'Quantity']]
df[['batch_code', 'Quantity']] = df[['batch_code', 'Quantity']].astype(int)
df.rename(columns={'Quantity': 'quantity_sold'}, inplace=True)

df['date'] = FILE_DATE  # Add prev date

df.to_csv(CLEANED_FILE, index=False)

print("✅ Data cleaned.")

# ========== STEP 2: LOAD FOOD ITEM IDS ==========
food_items = supabase.table("food_items").select("id, batch_code").execute().data
food_items_df = pd.DataFrame(food_items)
food_items_df["batch_code"] = food_items_df["batch_code"].astype(int)

print("✅ Data loaded from Database")


# ========== STEP 3: MERGE & INSERT TO Supabase ==========
sales_df = pd.read_csv(CLEANED_FILE)
merged_df = sales_df.merge(food_items_df, on="batch_code", how="inner")

records = merged_df[["id", "quantity_sold","date"]].rename(columns={"id": "food_item_id"}).to_dict("records")


for row in records:
    supabase.table("food_sales").insert(row).execute()

print("✅ Data cleaned, matched, and uploaded successfully.")