import pandas as pd
import glob
from sqlalchemy import create_engine

# --- CONFIG ---
DB_URL = "postgresql://brunoprincipi@localhost:5432/ppr_ireland"
DATA_FOLDER = "data/*.csv"

# --- STEP 1: Read and combine all 17 CSV files ---
dfs = []
for path in sorted(glob.glob(DATA_FOLDER)):
    print(f"Reading: {path}")
    df = pd.read_csv(path, encoding='windows-1252')
    dfs.append(df)

combined = pd.concat(dfs, ignore_index=True)
print(f"\nTotal raw rows: {len(combined)}")

# --- STEP 2: Rename columns ---
combined.columns = [
    'sale_date',
    'address',
    'county',
    'eircode',
    'price',
    'not_full_market_price',
    'vat_exclusive',
    'property_type',
    'property_size'
]

# --- STEP 3: Clean each column ---
combined['sale_date'] = pd.to_datetime(
    combined['sale_date'], format='%d/%m/%Y', errors='coerce'
)

combined['price'] = (
    combined['price']
    .str.replace(r'[^\d.]', '', regex=True)
    .str.strip()
    .astype(float)
)

combined['sale_year']  = combined['sale_date'].dt.year
combined['sale_month'] = combined['sale_date'].dt.month
combined['county']     = combined['county'].str.strip().str.title()
combined['eircode']    = combined['eircode'].str.strip().str.upper()

# --- STEP 4: Drop rows with missing date or price ---
before = len(combined)
combined = combined.dropna(subset=['sale_date', 'price'])
print(f"Dropped {before - len(combined)} rows with nulls")
print(f"Clean rows ready to load: {len(combined)}")

# --- STEP 5: Sanity check before loading ---
print("\nSample of clean data:")
print(combined[['sale_date', 'county', 'price', 'property_type']].head(3))
print(f"\nPrice range: €{combined['price'].min():,.0f} — €{combined['price'].max():,.0f}")
print(f"Years: {combined['sale_year'].min()} — {combined['sale_year'].max()}")
print(f"Counties: {combined['county'].nunique()}")

# --- STEP 6: Load into PostgreSQL ---
print("\nConnecting to database...")
engine = create_engine(DB_URL)

print("Loading data — this takes 1-2 minutes...")
combined.to_sql(
    name='ppr_sales',
    con=engine,
    if_exists='append',
    index=False,
    chunksize=1000
)

print("\nDone. Verifying row count...")
result = pd.read_sql("SELECT COUNT(*) as total FROM ppr_sales", engine)
print(result)