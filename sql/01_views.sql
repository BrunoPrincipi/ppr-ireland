-- ============================================
-- PPR IRELAND - ANALYTICAL VIEWS
-- ============================================
-- Purpose: Separate individual sales from bulk
-- institutional purchases for clean analysis
-- ============================================


-- VIEW 1: Individual sales (under €5 million)
-- This is the main view for all price analysis
CREATE OR REPLACE VIEW vw_individual_sales AS
SELECT
    id,
    sale_date,
    address,
    county,
    eircode,
    price,
    vat_exclusive,
    property_type,
    CASE
        WHEN property_type ILIKE '%New%'
          OR property_type ILIKE '%Nua%'
        THEN 'New'
        ELSE 'Second-Hand'
    END AS property_category,
    property_size,
    sale_year,
    sale_month
FROM ppr_sales
WHERE price <= 5000000
  AND not_full_market_price = 'No';


-- VIEW 2: Bulk/institutional purchases (over €5 million)
-- Apartment blocks bought by investment funds
CREATE OR REPLACE VIEW vw_bulk_sales AS
SELECT
    id,
    sale_date,
    address,
    county,
    price,
    property_type,
    sale_year
FROM ppr_sales
WHERE price > 5000000;