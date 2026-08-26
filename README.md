#  Irish Property Price Register — Analytics & ML Pipeline

A full end-to-end data project analysing 750,000+ residential property 
transactions in Ireland from 2010 to 2026, built as a portfolio project 
targeting data analyst and ML engineer roles in Dublin.

---

## Live Dashboard

https://datastudio.google.com/reporting/07f0908e-1a22-4887-87fc-955354058b8a

---

## Project Overview

This project covers the complete data pipeline from raw government data 
to a deployed machine learning API:

- **Data ingestion** — 17 CSV files from the official Property Price 
  Register (PSRA), combined and cleaned using Python
- **SQL analysis** — PostgreSQL database with analytical views, 
  window functions, and CTEs
- **Dashboard** — Interactive Looker Studio report with 4 pages
- **ML model** — XGBoost price prediction model trained on 747,000 rows
- **API** — FastAPI REST endpoint serving predictions
- **MLOps** — Dockerised container for reproducible deployment

---

##  Project Structure

Project Structure

| File/Folder | Description |
|---|---|
| `scripts/load_ppr.py` | Data cleaning and PostgreSQL ingestion |
| `scripts/train_model.py` | XGBoost model training and evaluation |
| `sql/01_views.sql` | Analytical views — individual vs bulk sales |
| `sql/02_analysis.sql` | Core analytical queries |
| `sql/03_window_functions.sql` | LAG, RANK, rolling averages |
| `api/main.py` | FastAPI app with /health /counties /predict |
| `Dockerfile` | Container definition |
| `requirements.txt` | Python dependencies |

---

##  Database Schema

**Table:** `ppr_sales` — 792,749 rows

| Column | Type | Description |
|--------|------|-------------|
| sale_date | DATE | Date of property sale |
| address | TEXT | Full property address |
| county | VARCHAR(50) | One of 26 Irish counties |
| eircode | VARCHAR(10) | Irish postal code |
| price | NUMERIC(12,2) | Sale price in euros |
| not_full_market_price | VARCHAR(10) | Flags non-market sales |
| vat_exclusive | VARCHAR(10) | VAT status for new builds |
| property_type | VARCHAR(100) | Property category |
| sale_year | SMALLINT | Extracted year |
| sale_month | SMALLINT | Extracted month |

**Views:**
- `vw_individual_sales` — 751,454 rows, excludes bulk purchases >€5M 
  and non-market transfers
- `vw_bulk_sales` — 1,019 rows, institutional block purchases

---

## Key SQL Highlights

**Window function — year on year price growth by county:**
```sql
WITH yearly_prices AS (
    SELECT county, sale_year,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP 
        (ORDER BY price)::NUMERIC) AS median_price
    FROM vw_individual_sales
    GROUP BY county, sale_year
)
SELECT county, sale_year, median_price,
    LAG(median_price) OVER (PARTITION BY county 
    ORDER BY sale_year) AS prev_year_price,
    ROUND((median_price - LAG(median_price) OVER 
    (PARTITION BY county ORDER BY sale_year))
    / LAG(median_price) OVER (PARTITION BY county 
    ORDER BY sale_year) * 100, 1) AS yoy_growth_pct
FROM yearly_prices
ORDER BY county, sale_year;
```

---

## Key Insights

- **Dublin median price** grew from €270,000 in 2010 to €477,000 
  in 2026 — a 76% increase
- **Market crash** — prices fell 13.5% in Dublin in 2012, bottoming 
  out at €212,000
- **Most affordable county** — Longford at €107,000 median 
  vs Dublin at €360,000
- **Institutional purchases** — 1,019 bulk transactions averaging 
  €18.9M each, representing investment funds buying entire 
  apartment blocks
- **New builds** consistently price at a premium over second-hand 
  — €396k vs €355k in 2026

---

##  ML Model

**Algorithm:** XGBoost Regressor  
**Training data:** 747,060 transactions (2010-2026)  
**Features:** County, sale year, sale month, property category, 
VAT status  
**Target:** Property price (log-transformed)

**Results:**
- RMSE: €184,651
- R²: 0.288

**Note on model performance:** The R² of 0.29 reflects the inherent 
limitations of the PPR dataset rather than the algorithm. The register 
does not include bedrooms, floor area, BER rating, or exact location 
within a county — the most important price determinants. Three paths 
to improvement are documented:
1. Eircode-level feature engineering from existing data
2. CSO county economic indicators (unemployment, income)
3. Property characteristics from Daft.ie (estimated R² >0.75)

---

##  API Endpoints

**Run locally:**
```bash
uvicorn api.main:app --reload
```

**Run with Docker:**
```bash
docker build -t ppr-price-predictor .
docker run -p 8000:8000 ppr-price-predictor
```

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | API status check |
| GET | /counties | List of valid county names |
| POST | /predict | Predict property price |

**Example prediction request:**
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"county": "Dublin", "sale_year": 2024, 
       "sale_month": 6, "is_new": 0, "vat_exclusive": 0}'
```

**Example response:**
```json
{
  "predicted_price": 464799.41,
  "county": "Dublin",
  "sale_year": 2024,
  "model_note": "Prediction based on county, year and property 
  type only. Actual prices vary significantly based on property 
  size, condition and exact location."
}
```

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Database | PostgreSQL 16 |
| Data processing | Python, Pandas, SQLAlchemy |
| ML | XGBoost, Scikit-learn |
| API | FastAPI, Uvicorn |
| Containerisation | Docker |
| Dashboard | Google Looker Studio |
| Version control | Git, GitHub |

---

## Data Source

**Irish Property Price Register (PPR)**  
Published by the Property Services Regulatory Authority (PSRA)  
Source: propertypriceregister.ie  
Licence: PSI Open Licence  
Coverage: All residential property sales in Ireland, 
January 2010 — present

---

## 👤 Author

Bruno Principi  
MSc Artificial Intelligence — University of Limerick  
Industry co-supervision: Viotas Ireland 