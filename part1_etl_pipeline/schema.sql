
PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS vw_product_summary;
DROP VIEW  IF EXISTS vw_monthly_product_sales;
DROP VIEW  IF EXISTS vw_sales_enriched;
DROP TABLE IF EXISTS fact_weekly_sales;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS data_quality_log;
DROP TABLE IF EXISTS quarantine_rows;
DROP TABLE IF EXISTS etl_run_log;

CREATE TABLE dim_product (
    product_id         INTEGER PRIMARY KEY,
    product_name       TEXT    NOT NULL UNIQUE,
    product_category   TEXT    NOT NULL,
    product_variant    TEXT,
    inventory_profile  TEXT    NOT NULL CHECK (inventory_profile IN ('normal', 'high_stock'))
);

CREATE TABLE dim_date (
    week_id          INTEGER PRIMARY KEY CHECK (week_id BETWEEN 1 AND 260),
    week_start_date  TEXT    NOT NULL,   -- synthetic calendar (assumption)
    week_end_date    TEXT    NOT NULL,
    year             INTEGER NOT NULL,
    quarter          INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month            INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name       TEXT    NOT NULL,
    week_of_year     INTEGER NOT NULL CHECK (week_of_year BETWEEN 1 AND 52),
    season           TEXT    NOT NULL,
    year_index       INTEGER NOT NULL    -- 1..5 = data year (52-week blocks)
);

CREATE TABLE fact_weekly_sales (
    sales_id                     INTEGER PRIMARY KEY,
    product_id                   INTEGER NOT NULL REFERENCES dim_product (product_id),
    week_id                      INTEGER NOT NULL REFERENCES dim_date (week_id),
    sales_units                  INTEGER NOT NULL CHECK (sales_units >= 0),
    sales_units_winsorized       REAL    NOT NULL CHECK (sales_units_winsorized >= 0),
    unit_price                   REAL    NOT NULL CHECK (unit_price > 0),
    unit_cogs                    REAL    NOT NULL CHECK (unit_cogs > 0),
    inventory_level              INTEGER NOT NULL CHECK (inventory_level >= 0),
    stock_available_for_sales    INTEGER CHECK (stock_available_for_sales >= 0),  -- previous row's inventory (see note)
    demand_forecast_legacy       REAL,
    revenue                      REAL    NOT NULL CHECK (revenue >= 0),
    gross_profit                 REAL    NOT NULL,
    operating_profit             REAL,
    implied_opex                 REAL,
    gross_profit_margin          REAL,
    inventory_turnover           REAL,
    revenue_growth               REAL,
    inventory_turnover_src       REAL,
    revenue_growth_src           REAL,
    flag_sales_imputed           INTEGER NOT NULL DEFAULT 0 CHECK (flag_sales_imputed IN (0, 1)),
    flag_zero_sales              INTEGER NOT NULL DEFAULT 0 CHECK (flag_zero_sales IN (0, 1)),
    flag_sales_pileup            INTEGER NOT NULL DEFAULT 0 CHECK (flag_sales_pileup IN (0, 1)),
    flag_inventory_pileup        INTEGER NOT NULL DEFAULT 0 CHECK (flag_inventory_pileup IN (0, 1)),
    flag_stockout_week           INTEGER NOT NULL DEFAULT 0 CHECK (flag_stockout_week IN (0, 1)),
    flag_stock_limited           INTEGER NOT NULL DEFAULT 0 CHECK (flag_stock_limited IN (0, 1)),
    flag_stock_unknown           INTEGER NOT NULL DEFAULT 0 CHECK (flag_stock_unknown IN (0, 1)),
    flag_sales_outlier           INTEGER NOT NULL DEFAULT 0 CHECK (flag_sales_outlier IN (0, 1)),
    flag_forecast_missing        INTEGER NOT NULL DEFAULT 0 CHECK (flag_forecast_missing IN (0, 1)),
    source_row_id                INTEGER NOT NULL,   -- row number in stg_sales_raw (lineage)
    UNIQUE (product_id, week_id)
);
CREATE INDEX idx_fact_week ON fact_weekly_sales (week_id);

CREATE TABLE data_quality_log (
    dq_id          INTEGER PRIMARY KEY,
    run_id         TEXT NOT NULL,
    source_row_id  INTEGER,
    product_name   TEXT,
    week_id        INTEGER,
    issue_type     TEXT NOT NULL,
    column_name    TEXT,
    action         TEXT NOT NULL,
    detail         TEXT
);
CREATE INDEX idx_dq_issue ON data_quality_log (issue_type);

CREATE TABLE quarantine_rows (
    quarantine_id    INTEGER PRIMARY KEY,
    run_id           TEXT NOT NULL,
    source_row_id    INTEGER,
    reason           TEXT NOT NULL,
    raw_record_json  TEXT
);

CREATE TABLE etl_run_log (
    step_id       INTEGER PRIMARY KEY,
    run_id        TEXT NOT NULL,
    step          TEXT NOT NULL,
    status        TEXT NOT NULL,
    rows_in       INTEGER,
    rows_out      INTEGER,
    duration_s    REAL,
    note          TEXT,
    started_utc   TEXT
);

CREATE VIEW vw_sales_enriched AS
SELECT f.sales_id, p.product_id, p.product_name, p.product_category, p.inventory_profile,
       d.week_id, d.week_start_date, d.year, d.quarter, d.month, d.week_of_year, d.season,
       f.sales_units, f.sales_units_winsorized, f.unit_price, f.unit_cogs, f.inventory_level, f.stock_available_for_sales,
       f.demand_forecast_legacy, f.revenue, f.gross_profit, f.operating_profit, f.implied_opex,
       f.gross_profit_margin, f.inventory_turnover, f.revenue_growth,
       f.flag_sales_imputed, f.flag_zero_sales, f.flag_sales_pileup, f.flag_inventory_pileup,
       f.flag_stockout_week, f.flag_stock_limited, f.flag_stock_unknown, f.flag_sales_outlier, f.flag_forecast_missing
FROM fact_weekly_sales f
JOIN dim_product p ON p.product_id = f.product_id
JOIN dim_date    d ON d.week_id    = f.week_id;

CREATE VIEW vw_monthly_product_sales AS
SELECT p.product_name, p.product_category, d.year, d.month,
       SUM(f.sales_units)       AS units,
       SUM(f.revenue)           AS revenue,
       SUM(f.gross_profit)      AS gross_profit,
       SUM(f.operating_profit)  AS operating_profit,
       ROUND(1.0 * SUM(f.gross_profit) / NULLIF(SUM(f.revenue), 0), 4) AS gross_profit_margin,
       AVG(f.inventory_level)   AS avg_inventory
FROM fact_weekly_sales f
JOIN dim_product p ON p.product_id = f.product_id
JOIN dim_date    d ON d.week_id    = f.week_id
GROUP BY p.product_name, p.product_category, d.year, d.month;

CREATE VIEW vw_product_summary AS
SELECT p.product_name, p.product_category, p.inventory_profile,
       COUNT(*)                     AS weeks,
       SUM(f.sales_units)           AS total_units,
       ROUND(SUM(f.revenue), 2)     AS total_revenue,
       ROUND(SUM(f.gross_profit), 2) AS total_gross_profit,
       ROUND(1.0 * SUM(f.gross_profit) / NULLIF(SUM(f.revenue), 0), 4) AS gross_profit_margin,
       ROUND(AVG(f.inventory_level), 1) AS avg_inventory,
       ROUND(1.0 * AVG(f.inventory_level) / NULLIF(AVG(f.sales_units), 0), 1) AS avg_weeks_of_cover,
       SUM(f.flag_zero_sales)       AS zero_sales_weeks,
       SUM(f.flag_stockout_week)    AS stockout_weeks,
       SUM(f.flag_stock_limited)    AS stock_limited_weeks
FROM fact_weekly_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.product_id;
