-- ============================================
-- PPR IRELAND - WINDOW FUNCTIONS
-- ============================================


-- QUERY 1: Year-on-year median price change by county
WITH yearly_prices AS (
    SELECT
        county,
        sale_year,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)::NUMERIC) AS median_price
    FROM vw_individual_sales
    GROUP BY county, sale_year
)
SELECT
    county,
    sale_year,
    median_price,
    LAG(median_price) OVER (PARTITION BY county ORDER BY sale_year) AS prev_year_price,
    ROUND(
        (median_price - LAG(median_price) OVER (PARTITION BY county ORDER BY sale_year))
        / LAG(median_price) OVER (PARTITION BY county ORDER BY sale_year) * 100, 1
    ) AS yoy_growth_pct
FROM yearly_prices
ORDER BY county, sale_year;


-- QUERY 2: County price rank per year
WITH yearly_prices AS (
    SELECT
        county,
        sale_year,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)::NUMERIC) AS median_price
    FROM vw_individual_sales
    GROUP BY county, sale_year
)
SELECT
    county,
    sale_year,
    median_price,
    RANK() OVER (PARTITION BY sale_year ORDER BY median_price DESC) AS price_rank
FROM yearly_prices
ORDER BY sale_year, price_rank;


-- QUERY 3: 3-year rolling average price by county
WITH yearly_prices AS (
    SELECT
        county,
        sale_year,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)::NUMERIC) AS median_price
    FROM vw_individual_sales
    GROUP BY county, sale_year
)
SELECT
    county,
    sale_year,
    median_price,
    ROUND(AVG(median_price) OVER (
        PARTITION BY county
        ORDER BY sale_year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )) AS rolling_3yr_avg
FROM yearly_prices
ORDER BY county, sale_year;