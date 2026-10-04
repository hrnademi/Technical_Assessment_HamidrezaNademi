# Changelog

**Naming convention:** `part<N>_<topic>_v<version>.<ext>`: every notebook and every generated
file starts with the task part (`part1_`, `part2_`, ...) and ends with its version (`_v1.1`).
Each notebook creates its own output folder (`part<N>_<topic>/`) when run; output folders are git-ignored.
Previous versions are never overwritten or deleted: a new version is a new notebook,
and the older notebooks stay in the repo alongside it as history.

| Part | Version | Notebook | Generates (when run) | Notes |
|---|---|---|---|---|
| 1 – Data engineering (EDA) | v1.1 | `part1_eda_v1.1.ipynb` | `v1_eda/` (old folder name) | Read-only EDA of the raw `Sample_Data.xlsx`; all results in one Excel workbook |
| 1 – Data engineering (EDA) | v1.2 | `part1_eda_v1.2.ipynb` | `v1_eda/` (old folder name) | Adds a `Summary` sheet (25-row EDA summary with severity and proposed ETL treatment) |
| 1 – Data engineering (ETL) | v1.0 | `part1_etl_pipeline_v1.0.ipynb` | `part1_etl_pipeline/part1_armani_trade_v1.0.db`, `part1_schema_v1.0.sql`, `part1_etl_results_v1.0.xlsx`, `part1_etl_run_v1.0.log`, `figures/part1_*_v1.0.png` | Extract, validate/quarantine, de-duplicate, recover sales, flag anomalies, recompute KPIs, synthetic calendar, SQLite star schema, validation + exception tests, quality scorecard |
