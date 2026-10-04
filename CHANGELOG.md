# Changelog

Every generated file carries its version at the end of the name (e.g. `*_v1.1.xlsx`).
Only the notebooks are committed. Each notebook creates its own output folder when run
(git-ignored). Previous versions are never overwritten or deleted: a new version is a new
notebook, and the older notebooks stay in the repo alongside it as history.

| Version | Notebook | Generates (when run) | Notes |
|---|---|---|---|
| v1.1 | `v1_eda_v1.1.ipynb` | `v1_eda/v1_eda_results_v1.1.xlsx`, `v1_eda/figures/*_v1.1.png` | Read-only EDA of the raw `Sample_Data.xlsx`; all results in one Excel workbook |
| v1.2 | `v1_eda_v1.2.ipynb` | `v1_eda/v1_eda_results_v1.2.xlsx`, `v1_eda/figures/*_v1.2.png` | Adds a `Summary` sheet (first sheet): 25-row EDA summary of the raw data with result, rows affected, severity and proposed ETL treatment; replaces the shorter `Findings` sheet |
