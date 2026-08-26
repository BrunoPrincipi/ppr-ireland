-- ============================================
-- PPR IRELAND - CORE ANALYTICAL QUERIES
-- ============================================
-- All queries use vw_individual_sales to exclude
-- bulk purchases and non-market transactions
-- ============================================


-- QUERY 1: Total sales and median price by year
-- Shows the overall market trend from 2010 to 2026
SELECT
    sale_year,
    COUNT(*)                                                    AS total_sales,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price))  AS median_price,
    ROUND(AVG(price))                                          AS avg_price
FROM vw_individual_sales
GROUP BY sale_year
ORDER BY sale_year;


-- QUERY 2: Median price by county (all time)
-- Shows which counties are most and least affordable
SELECT
    county,
    COUNT(*)                                                    AS total_sales,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price))  AS median_price
FROM vw_individual_sales
GROUP BY county
ORDER BY median_price DESC;


-- QUERY 3: New vs second-hand split by year
-- Shows how the new build market has changed over time
SELECT
    sale_year,
    property_type,
    COUNT(*)                                                    AS total_sales,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price))  AS median_price
FROM vw_individual_sales
GROUP BY sale_year, property_type
ORDER BY sale_year, property_type;


-- QUERY 4: Most affordable counties in last 3 years
-- Useful insight for first time buyers
SELECT
    county,
    COUNT(*)                                                    AS total_sales,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price))  AS median_price
FROM vw_individual_sales
WHERE sale_year >= 2023
GROUP BY county
ORDER BY median_price ASC;