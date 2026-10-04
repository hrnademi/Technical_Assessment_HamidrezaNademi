# v1_eda: raw data profile (no changes made to data)

Reproduce: run `v1_eda/v1_eda.ipynb` (top to bottom) → `outputs/` (CSV tables, `figures/*.png`)

| Area | Finding |
|---|---|
| Size | 7,839 rows × 13 cols; expected 30 × 260 = 7,800 |
| Duplicates | 39 exact duplicate rows (same Week+Product, identical values) → after removal 260 weeks per product, no gaps |
| Product names | 30 clean names, no spelling/whitespace/case variants |
| Missing | `Demand_Forecast` 609 (7.8%, uniform across years); `Sales_Units` 16 (0.2%) |
| Recoverable | The 16 missing `Sales_Units` rows still have `Revenue` → `Sales_Units = Revenue / Price_Per_Unit` |
| Zero sales | 1,333 rows (17%) with Sales=0, Revenue=0, GP=0; runs are short (median 1 week, max 6); only 431 coincide with Inventory=0 |
| Inventory | Heavily clipped: 0 (1,341 rows), 1,500 (1,421), 2,500 (1,399) are spikes; 905 rows have Inventory=0 yet Sales>0 (logically impossible) |
| Caps | Sales_Units = 2,500 in 732 rows and 1,500 in 1,384 rows; Turnover_Ratio = 1.0 in 2,842 rows (clipped) |
| Inventory outliers | 7 products carry 6–185 weeks of cover (Spices-Turmeric, Wheat-Hard Red, Sunflower Oil, Milk Powder-Whole, Chickpeas, Rice-Basmati, Flour) with mean inventory 8k–105k vs ~1.5k for the rest |
| Derived columns | `Revenue = Sales×Price` and `Gross_Profit = Revenue − Sales×COGS` hold 100%; `GPM = GP/Revenue` holds 100% (where Revenue>0) |
| Revenue_Growth | 897 `inf` values (growth after a zero-revenue week); 87% match week-over-week pct_change; 165 finite values with \|growth\|>2 |
| Inventory_Turnover | Does not match Sales/Inventory or Sales×COGS/Inventory → definition unknown (clipped to [0,1]) |
| Operating_Profit | Always ≤ Gross_Profit; ratio OP/GP 0.25–0.71 (opex not given, cannot be recomputed) |
| Pricing | Price/COGS markup is uniform 1.20–1.35 for all products → little real pricing signal |
| Baseline forecast | `Demand_Forecast` vs `Sales_Units`: corr 0.21, median abs % error 17.5% (inflated by zeros) |
| Seasonality | Weak yearly pattern (seasonal index 0.87–1.23); flat trend yrs 1–4, +4% in yr 5 |
| Price/COGS | No negatives; no price < COGS |
