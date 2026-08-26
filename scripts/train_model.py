# ============================================
# PPR IRELAND - PRICE PREDICTION MODEL
# ============================================
# Trains an XGBoost model to predict property
# prices from county, year, and property type
# ============================================

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import joblib
import os

# --- STEP 1: CONNECT AND QUERY DATABASE ---
print("Connecting to database...")
DB_URL = "postgresql://brunoprincipi@localhost:5432/ppr_ireland"
engine = create_engine(DB_URL)

query = """
    SELECT
        county,
        sale_year,
        sale_month,
        property_category,
        vat_exclusive,
        price
    FROM vw_individual_sales
    WHERE price > 10000
      AND price < 2000000
"""

df = pd.read_sql(query, engine)
print(f"Loaded {len(df):,} rows from database")

# --- STEP 2: FEATURE ENGINEERING ---
print("Engineering features...")

# Convert vat_exclusive from Yes/No to 1/0
df['vat_exclusive'] = (df['vat_exclusive'] == 'Yes').astype(int)

# Convert property_category from New/Second-Hand to 1/0
df['is_new'] = (df['property_category'] == 'New').astype(int)

# Encode county as a number
# LabelEncoder converts Dublin -> 4, Cork -> 2 etc
le_county = LabelEncoder()
df['county_encoded'] = le_county.fit_transform(df['county'])

# Use log of price as target
# Log transformation makes price distribution more normal
# which helps XGBoost learn better
df['log_price'] = np.log(df['price'])

# Define features (X) and target (y)
features = [
    'county_encoded',
    'sale_year',
    'sale_month',
    'is_new',
    'vat_exclusive'
]

X = df[features]
y = df['log_price']

print(f"Features: {features}")
print(f"Training on {len(X):,} properties")

# --- STEP 3: TRAIN THE MODEL ---
print("\nSplitting data into train and test sets...")

# 80% training, 20% testing
# random_state=42 means the split is reproducible
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set: {len(X_train):,} rows")
print(f"Test set: {len(X_test):,} rows")

print("\nTraining XGBoost model...")
model = xgb.XGBRegressor(
    n_estimators=100,      # number of trees
    max_depth=6,           # how deep each tree can grow
    learning_rate=0.1,     # how much each tree contributes
    random_state=42
)

model.fit(X_train, y_train)
print("Training complete")

# --- STEP 4: EVALUATE THE MODEL ---
print("\nEvaluating model...")

# Predict on test set
y_pred_log = model.predict(X_test)

# Convert log predictions back to actual prices
y_pred = np.exp(y_pred_log)
y_actual = np.exp(y_test)

# RMSE - average error in euros
rmse = np.sqrt(mean_squared_error(y_actual, y_pred))

# R2 - percentage of variation explained (1.0 is perfect)
r2 = r2_score(y_actual, y_pred)

print(f"RMSE: €{rmse:,.0f}")
print(f"R²: {r2:.3f}")
print(f"\nOn average the model predicts within €{rmse:,.0f} of the actual price")

# Feature importance - which features matter most
print("\nFeature importance:")
importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print(importance.to_string(index=False))

# --- STEP 5: SAVE THE MODEL ---
print("\nSaving model...")
os.makedirs('api', exist_ok=True)

joblib.dump(model, 'api/model.pkl')
joblib.dump(le_county, 'api/county_encoder.pkl')

# Save county list for the API to use
county_list = sorted(df['county'].unique().tolist())
joblib.dump(county_list, 'api/county_list.pkl')

print("Model saved to api/model.pkl")
print("County encoder saved to api/county_encoder.pkl")
print("County list saved to api/county_list.pkl")
