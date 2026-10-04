# Changelog

**Naming convention:** `part<N>_<topic>_v<version>.<ext>`: every notebook and every generated
file starts with the task part (`part1_`, `part2_`, ...) and ends with its version (`_v1.1`).
Each notebook creates an output folder with **the same name as the notebook** (`part1_eda_v1.2.ipynb` → `part1_eda_v1.2/`) when run (only the folder takes the notebook's name; the files inside keep their own versioned names); output folders are git-ignored.
Previous versions are never overwritten or deleted: a new version is a new notebook,
and the older notebooks stay in the repo alongside it as history.

| Part | Version | Notebook | Generates (when run) | Notes |
|---|---|---|---|---|
| 1 – Data engineering (EDA) | v1.1 | `part1_eda_v1.1.ipynb` | `part1_eda_v1.1/v1_eda_results_v1.1.xlsx`, `figures/*_v1.1.png` | Read-only EDA of the raw `Sample_Data.xlsx`; all results in one Excel workbook |
| 1 – Data engineering (EDA) | v1.2 | `part1_eda_v1.2.ipynb` | `part1_eda_v1.2/v1_eda_results_v1.2.xlsx`, `figures/*_v1.2.png` | Adds a `Summary` sheet (25-row EDA summary with severity and proposed ETL treatment) |
| 1 – Data engineering (ETL) | v1.0 | `part1_etl_pipeline_v1.0.ipynb` | `part1_etl_pipeline_v1.0/armani_trade_v1.0.db`, `schema_v1.0.sql`, `etl_results_v1.0.xlsx`, `etl_run_v1.0.log`, `figures/*_v1.0.png` | Extract, validate/quarantine, de-duplicate, recover sales, flag anomalies, recompute KPIs, synthetic calendar, SQLite star schema, validation + exception tests, quality scorecard |
| 1 – Data engineering (ETL) | v1.1 | `part1_etl_pipeline_v1.1.ipynb` | `part1_etl_pipeline_v1.1/armani_trade_v1.1.db`, `schema_v1.1.sql`, `etl_results_v1.1.xlsx`, `etl_run_v1.1.log`, `figures/*_v1.1.png` | Inventory timing fix: sales never exceed the previous row's inventory -> `stock_available_for_sales`, stock-out / stock-limited flags (replace "inventory inconsistent"), turnover on available stock, new evidence sheet + figure |
| 2 – Forecasting (preprocessing) | v1.0 | `part2_preprocessing_v1.0.ipynb` | `part2_preprocessing_v1.0/forecast_dataset_v1.0.db`, `preprocessing_results_v1.0.xlsx`, `figures/*_v1.0.png` | Stock-censoring classification, legacy-forecast validation, demand reconstruction (CV-tuned seasonal model + blend), calendar-effect tests, product patterns / stock regimes, forecasting dataset |
