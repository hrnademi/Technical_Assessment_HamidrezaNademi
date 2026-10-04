"""v1_eda: read-only exploratory analysis of the raw Sample_Data.xlsx.

Nothing is cleaned or modified here; the goal is to document the raw state.
All outputs are written to ./outputs (tables as CSV, plots in ./outputs/figures,
and a text log in ./outputs/eda_log.txt).
"""
from pathlib import Path
import io
import contextlib

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "outputs"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(HERE / "Sample_Data.xlsx")
NUM = [c for c in df.columns if c not in ("Week", "Product")]
buf = io.StringIO()


def section(title):
    print(f"\n{'=' * 80}\n{title}\n{'=' * 80}")


def save(t, name):
    t.to_csv(OUT / name)


with contextlib.redirect_stdout(buf):
    section("1. SHAPE / DTYPES")
    print(df.shape, "| expected 30 products x 260 weeks =", 30 * 260)
    print(df.dtypes.to_string())

    section("2. MISSING VALUES")
    miss = pd.DataFrame({"n_missing": df.isna().sum(), "pct": (df.isna().mean() * 100).round(2)})
    print(miss.to_string()); save(miss, "missing_values.csv")
    print("rows with >=1 missing:", df.isna().any(axis=1).sum())

    section("3. PRODUCT NAMES")
    pc = df["Product"].value_counts(dropna=False).sort_index()
    print(pc.to_string()); save(pc.to_frame("rows"), "rows_per_product.csv")
    print("n unique raw names:", df["Product"].nunique(dropna=False))
    norm = df["Product"].astype(str).str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
    print("n unique after trim/lower/whitespace-collapse:", norm.nunique())
    print("names with leading/trailing/double whitespace:",
          int((df["Product"].astype(str) != df["Product"].astype(str).str.strip()).sum()))
    print("names with inconsistent case vs. normalised form:")
    grp = df.assign(n=norm).groupby("n")["Product"].unique()
    print(grp[grp.apply(len) > 1].to_string())

    section("4. DUPLICATES")
    print("exact duplicate rows:", df.duplicated().sum())
    print("duplicate (Week, Product) keys:", df.duplicated(["Week", "Product"]).sum())
    dk = df[df.duplicated(["Week", "Product"], keep=False)].sort_values(["Product", "Week"])
    print("rows involved in key duplication:", len(dk))
    print("key-duplicates that are NOT exact copies:",
          len(dk) - len(dk.drop_duplicates()) * 0 - dk.duplicated(keep="first").sum() - dk.drop_duplicates().groupby(["Week","Product"]).ngroups)
    dk.to_csv(OUT / "duplicate_rows.csv", index=False)
    print(dk.head(12).to_string())

    section("5. WEEK COVERAGE")
    print("Week min/max:", df["Week"].min(), df["Week"].max(), "| n unique:", df["Week"].nunique())
    cov = df.drop_duplicates(["Week", "Product"]).groupby("Product")["Week"].agg(["count", "min", "max"])
    cov["missing_weeks"] = 260 - cov["count"]
    print(cov.to_string()); save(cov, "week_coverage.csv")
    gaps = {p: sorted(set(range(1, 261)) - set(g["Week"])) for p, g in df.groupby("Product")}
    gaps = {p: v for p, v in gaps.items() if v}
    print("products with missing weeks:", {p: v[:10] for p, v in gaps.items()})

    section("6. DESCRIPTIVE STATS (raw)")
    desc = df[NUM].describe(percentiles=[.01, .05, .5, .95, .99]).T
    print(desc.round(3).to_string()); save(desc, "describe.csv")

    section("7. IMPOSSIBLE / SUSPICIOUS VALUES")
    for c in ["Sales_Units", "Cost_of_Goods_Sold_COGS", "Inventory_Level", "Price_Per_Unit", "Revenue", "Demand_Forecast"]:
        print(f"{c:28s} <0: {(df[c] < 0).sum():4d} | ==0: {(df[c] == 0).sum():4d}")
    print("Price < COGS rows (negative unit margin):", (df.Price_Per_Unit < df.Cost_of_Goods_Sold_COGS).sum())
    print("Sales_Units > Inventory_Level:", (df.Sales_Units > df.Inventory_Level).sum())
    print("Sales_Units non-integer:", int(((df.Sales_Units.dropna() % 1) != 0).sum()))
    print("Operating_Profit > Gross_Profit:", (df.Operating_Profit > df.Gross_Profit).sum())

    section("8. OUTLIERS (per-product robust z-score, |z|>4 using median/MAD; plus global IQR 3x)")
    rows = []
    for c in ["Sales_Units", "Cost_of_Goods_Sold_COGS", "Inventory_Level", "Demand_Forecast", "Price_Per_Unit"]:
        med = df.groupby("Product")[c].transform("median")
        mad = df.assign(d=(df[c] - med).abs()).groupby("Product")["d"].transform("median")
        z = 0.6745 * (df[c] - med) / mad.replace(0, np.nan)
        q1, q3 = df[c].quantile([.25, .75]); iqr = q3 - q1
        glob = ((df[c] < q1 - 3 * iqr) | (df[c] > q3 + 3 * iqr)).sum()
        rows.append({"column": c, "robust_z>4": int((z.abs() > 4).sum()), "global_IQR3x": int(glob)})
        df[f"{c}__rz"] = z
    out = pd.DataFrame(rows).set_index("column"); print(out.to_string()); save(out, "outlier_counts.csv")
    top = df.loc[df[[f"{c}__rz" for c in ["Sales_Units", "Cost_of_Goods_Sold_COGS", "Inventory_Level", "Demand_Forecast", "Price_Per_Unit"]]].abs().max(axis=1).nlargest(15).index,
                 ["Week", "Product", "Sales_Units", "Cost_of_Goods_Sold_COGS", "Inventory_Level", "Demand_Forecast", "Price_Per_Unit"]]
    print("\nmost extreme rows:\n", top.to_string()); top.to_csv(OUT / "top_outliers.csv")
    df = df.drop(columns=[c for c in df.columns if c.endswith("__rz")])

    section("9. DERIVED-COLUMN CONSISTENCY (are given formulas reproducible?)")
    d = df.dropna(subset=["Sales_Units"]).copy()
    d["rev_calc"] = d.Sales_Units * d.Price_Per_Unit
    d["gp_calc"] = d.Revenue - d.Sales_Units * d.Cost_of_Goods_Sold_COGS
    d["gpm_calc"] = d.Gross_Profit / d.Revenue
    d["it_a"] = d.Sales_Units / d.Inventory_Level
    d["it_b"] = d.Sales_Units * d.Cost_of_Goods_Sold_COGS / d.Inventory_Level
    d = d.sort_values(["Product", "Week"])
    d["rg_calc"] = d.groupby("Product")["Revenue"].pct_change().fillna(0)
    tests = {
        "Revenue = Sales*Price": (d.Revenue, d.rev_calc),
        "Gross_Profit = Revenue - Sales*COGS": (d.Gross_Profit, d.gp_calc),
        "GPM = GP/Revenue": (d.Gross_Profit_Margin, d.gpm_calc),
        "Turnover = Sales/Inventory": (d.Inventory_Turnover_Ratio, d.it_a),
        "Turnover = Sales*COGS/Inventory": (d.Inventory_Turnover_Ratio, d.it_b),
        "Rev_Growth = pct_change(Revenue)": (d.Revenue_Growth, d.rg_calc),
    }
    res = []
    for k, (a, b) in tests.items():
        m = a.notna() & b.notna()
        err = (a[m] - b[m]).abs()
        res.append({"test": k, "n": int(m.sum()), "median_abs_err": err.median(), "p99_abs_err": err.quantile(.99),
                    "pct_within_1%_rel": round(100 * (err <= 0.01 * b[m].abs().clip(lower=1e-9)).mean(), 1)})
    res = pd.DataFrame(res).set_index("test"); print(res.round(4).to_string()); save(res, "formula_checks.csv")
    print("\nCorr Demand_Forecast vs Sales_Units:", round(d.Demand_Forecast.corr(d.Sales_Units), 3))
    fe = (d.Demand_Forecast - d.Sales_Units).abs() / d.Sales_Units
    print("Baseline forecast MAPE on raw data (%):", round(100 * fe.mean(), 2), "| median:", round(100 * fe.median(), 2))

    section("10. PER-PRODUCT SUMMARY")
    ps = df.groupby("Product").agg(rows=("Week", "size"), units_mean=("Sales_Units", "mean"), units_cv=("Sales_Units", lambda s: s.std() / s.mean()),
                                    cogs_mean=("Cost_of_Goods_Sold_COGS", "mean"), price_mean=("Price_Per_Unit", "mean"),
                                    inv_mean=("Inventory_Level", "mean"), rev_total=("Revenue", "sum"))
    print(ps.round(2).to_string()); save(ps, "product_summary.csv")

    section("11. SEASONALITY SIGNAL (mean Sales_Units index by week-of-year, 52-wk cycle, all products)")
    t = df.dropna(subset=["Sales_Units"]).copy()
    t["idx"] = t.Sales_Units / t.groupby("Product")["Sales_Units"].transform("mean")
    wk = t.assign(woy=((t.Week - 1) % 52) + 1).groupby("woy")["idx"].mean()
    print("seasonal index range:", round(wk.min(), 3), "-", round(wk.max(), 3))
    yr = t.assign(y=(t.Week - 1) // 52 + 1).groupby("y")["idx"].mean()
    print("yearly mean index (trend):", yr.round(3).to_dict())

(OUT / "eda_log.txt").write_text(buf.getvalue())
print(buf.getvalue())

# ---------- figures ----------
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(8, 4))
miss["n_missing"][miss["n_missing"] > 0].sort_values().plot.barh(ax=ax, color="#c0392b")
ax.set_title("Missing values per column (raw)"); fig.tight_layout(); fig.savefig(FIG / "missing_values.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 7))
pc.sort_values().plot.barh(ax=ax, color="#2c7fb8"); ax.axvline(260, color="k", ls="--", lw=1)
ax.set_title("Rows per product (dashed = 260 expected)"); fig.tight_layout(); fig.savefig(FIG / "rows_per_product.png"); plt.close(fig)

fig, axes = plt.subplots(2, 3, figsize=(14, 7))
for ax, c in zip(axes.ravel(), ["Sales_Units", "Cost_of_Goods_Sold_COGS", "Inventory_Level", "Demand_Forecast", "Price_Per_Unit", "Revenue"]):
    ax.hist(df[c].dropna(), bins=60, color="#2c7fb8"); ax.set_title(c)
fig.tight_layout(); fig.savefig(FIG / "distributions.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(12, 5))
df.dropna(subset=["Sales_Units"]).assign(z=lambda x: x.Sales_Units / x.groupby("Product")["Sales_Units"].transform("mean")).boxplot(column="z", by="Product", ax=ax, rot=90, grid=False)
ax.set_title("Sales_Units / product mean (outlier view)"); plt.suptitle(""); fig.tight_layout(); fig.savefig(FIG / "sales_boxplot.png"); plt.close(fig)

first6 = df.Product.drop_duplicates().head(6)
fig, axes = plt.subplots(3, 2, figsize=(14, 9), sharex=True)
for ax, p in zip(axes.ravel(), first6):
    g = df[df.Product == p].sort_values("Week")
    ax.plot(g.Week, g.Sales_Units, lw=.8, label="Sales_Units"); ax.plot(g.Week, g.Demand_Forecast, lw=.8, alpha=.7, label="Demand_Forecast")
    ax.set_title(p, fontsize=9)
axes[0, 0].legend(); fig.tight_layout(); fig.savefig(FIG / "sales_vs_forecast_sample.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 6))
cm = df[NUM].corr(); im = ax.imshow(cm, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(NUM))); ax.set_xticklabels(NUM, rotation=90, fontsize=7); ax.set_yticks(range(len(NUM))); ax.set_yticklabels(NUM, fontsize=7)
fig.colorbar(im); ax.set_title("Correlation (raw)"); fig.tight_layout(); fig.savefig(FIG / "correlation.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4))
wk.plot(ax=ax, color="#2c7fb8"); ax.set_title("Mean normalised Sales_Units by week-of-year (all products)"); fig.tight_layout(); fig.savefig(FIG / "seasonality.png"); plt.close(fig)

# ---------- deep-dive on anomalies found in first pass ----------
buf2 = io.StringIO()
with contextlib.redirect_stdout(buf2):
    section("12. ZERO-SALES / CAPS / INF DEEP-DIVE")
    z = df[df.Sales_Units == 0]
    print("zero-sales rows:", len(z), "| of which Inventory_Level==0:", (z.Inventory_Level == 0).sum(),
          "| Revenue==0:", (z.Revenue == 0).sum(), "| Gross_Profit==0:", (z.Gross_Profit == 0).sum())
    print("Inventory_Level==0 rows with Sales_Units>0:", ((df.Inventory_Level == 0) & (df.Sales_Units > 0)).sum())
    print("zero-sales share by product (top 8):\n", (df.assign(z=df.Sales_Units == 0).groupby("Product")["z"].mean().sort_values(ascending=False).head(8)).round(3).to_string())
    run = df.sort_values(["Product", "Week"]).assign(z=lambda x: (x.Sales_Units == 0).astype(int))
    run["grp"] = (run.z != run.groupby("Product")["z"].shift()).cumsum()
    lens = run[run.z == 1].groupby("grp").size()
    print("zero-sales run lengths: n_runs=%d, median=%d, max=%d" % (len(lens), lens.median(), lens.max()))
    print("Sales_Units == 2500 (cap?):", (df.Sales_Units == 2500).sum(), "| Inventory_Level == 2500:", (df.Inventory_Level == 2500).sum(),
          "| Turnover == 1.0:", (df.Inventory_Turnover_Ratio == 1).sum(), "| Sales_Units==1500:", (df.Sales_Units == 1500).sum(), "| Inventory==1500:", (df.Inventory_Level == 1500).sum())
    print("Inventory value counts (top 6):\n", df.Inventory_Level.value_counts().head(6).to_string())
    print("Revenue_Growth: inf rows =", np.isinf(df.Revenue_Growth).sum(), "| ==-1:", (df.Revenue_Growth == -1).sum())
    print("Revenue_Growth abs>2 (excluding inf):", ((df.Revenue_Growth.abs() > 2) & np.isfinite(df.Revenue_Growth)).sum())
    print("Sales_Units NaN rows - Revenue/GP values:\n", df[df.Sales_Units.isna()][["Week", "Product", "Revenue", "Gross_Profit", "Inventory_Level"]].head(8).to_string())
    print("Demand_Forecast missing share by year:\n", df.assign(y=(df.Week - 1) // 52 + 1).groupby("y")["Demand_Forecast"].apply(lambda s: s.isna().mean()).round(3).to_string())
    print("Products with huge inventory (mean>5000) -> weeks of cover:")
    big = ps[ps.inv_mean > 5000]; print((big.inv_mean / big.units_mean).round(1).to_string())
    print("Operating_Profit/Gross_Profit ratio describe:\n", (df.Operating_Profit / df.Gross_Profit.replace(0, np.nan)).describe().round(3).to_string())
    print("Price vs COGS markup ratio describe:\n", (df.Price_Per_Unit / df.Cost_of_Goods_Sold_COGS).describe().round(3).to_string())
    print("Sales_Units upper clip? top values:", df.Sales_Units.nlargest(5).tolist())
(OUT / "eda_log.txt").write_text(buf.getvalue() + buf2.getvalue())
print(buf2.getvalue())
