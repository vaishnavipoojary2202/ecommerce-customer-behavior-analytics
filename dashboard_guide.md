# Dashboard Guide

A practical, owner-facing guide to the Streamlit dashboard in **`main.py`**
(repository root). It explains what the dashboard is, how to run it, how to
connect it to the real notebook outputs, and what to do when something looks off.

> If you only read one section, read **3. Quick start** and **5. Connecting real data**.

---

## 1. What this dashboard is

`main.py` is the **frontend** for the E-Commerce Customer Behavior Analytics project.
It visualises the results of notebooks `01 → 06`.

It has two modes:

| Mode | When it is used | Where the numbers come from |
|---|---|---|
| 🧪 **Demo** | The real output files are **not found** | Embedded sample data inside `main.py`, built from the notebook summaries in `context.md` |
| ✅ **Real** | The real output files **are found** at the expected paths | The Parquet/CSV files produced by your notebooks |

**The demo mode is intentional.** It means the dashboard always renders, even on a
fresh clone where the (gitignored) data files don't exist yet. You are *not* seeing
real data until the sidebar says otherwise — see section 4.

The dashboard does **not** overwrite or replace `dashboard/app.py`; it is a separate,
more complete app.

---

## 2. Prerequisites

- Python 3.9+
- The packages in `requirements.txt` **plus** `pyarrow` (needed to read `.parquet`
  files with pandas). If `pandas.read_parquet` fails, install it:

  ```bash
  pip install pyarrow
  ```

---

## 3. Quick start

From the **repository root**:

```bash
# 1) install dependencies (once)
pip install -r requirements.txt
pip install pyarrow

# 2) launch the dashboard
streamlit run main.py
```

Streamlit opens a browser tab (usually http://localhost:8501). You can stop the
server with `Ctrl + C` in the terminal.

> The first run will very likely be in **demo mode** (🧪). That is expected — the
> real files are only created after you run the notebooks and export the outputs
> (section 5).

---

## 4. Is it showing REAL or DEMO data?

Open the sidebar and look at **🔌 Data source status**. Each expected file is listed
with an icon:

- ✅ — the file was found and is being used (real data)
- 🧪 demo — the file is missing, so the embedded sample data is used instead

If **any** customer file is missing, the *customer* pages use demo data, and a yellow
warning appears in the sidebar. The same applies per-section for product / category /
brand / sales tables.

The demo numbers are loosely based on notebook results (e.g. 347,118 customers,
₹229.96M revenue), so the dashboard looks realistic — but it is **not** your analysis
until the icons turn to ✅.

---

## 5. Connecting real data  ← the main thing you need to do

The dashboard looks for files at the exact paths listed at the top of `main.py`
(the `DATA SOURCE PATHS` block). If a file exists there with the **right column
names**, it is used automatically — **no code change needed**.

### 5.1 File & column contract

The dashboard reads specific column names. If your notebook output uses different
names, either rename them in the notebook's export cell, or edit the constants in
`main.py`.

**A. Customer-level data (drives Overview, RFM & Segments, Segment Profiles)**

| File | Produced by | Columns the dashboard needs |
|---|---|---|
| `data/clustered_customers_oct.parquet` | notebook 05 | `cluster`, `user_id`, `recency_days`, `purchase_events`, `total_spend`, `avg_txn_value`, `events_per_session`, and optionally `spend_band` |
| `data/customer_analytics_oct.parquet` | notebook 03 | fallback if the clustered file is absent; same columns except `cluster` |

> ⚠️ **Column names matter.** In particular the dashboard expects:
> - `avg_txn_value` for Average Transaction Value
> - `events_per_session` for average purchase events per session
> - `recency_days`, `purchase_events`, `total_spend` for R / F / M
> - `cluster` (integer) and `user_id`
>
> If your notebook names them differently (e.g. `average_transaction_value`,
> `avg_purchase_events_per_session`), rename them in the export, or ask an AI agent
> to update `main.py`.

**B. Aggregate tables (product / category / brand / sales)**

| File | Produced by | Columns the dashboard needs |
|---|---|---|
| `outputs/tables/top_products.csv` | notebook 06 | `product_id`, `purchase_events`, `unique_customers`, `total_value`, `avg_value` |
| `outputs/tables/category_performance.csv` | notebook 06 | `category_code`, `purchase_events`, `unique_products`, `unique_customers`, `total_value`, `avg_value` |
| `outputs/tables/brand_performance.csv` | notebook 06 | `brand`, `purchase_events`, `unique_products`, `unique_customers`, `total_value`, `avg_value` |
| `outputs/tables/daily_sales.csv` | notebook 06 | `date`, `purchase_events`, `total_value` |
| `outputs/tables/day_of_week_sales.csv` | notebook 06 | `day_of_week`, `purchase_events`, `total_value` |
| `outputs/figures/customer_segments_pca.png` | notebook 05 | (image; optional — a synthetic projection is shown if missing) |
| `outputs/tables/customer_cluster_profile.csv` | notebook 05 | optional/reserved — currently only listed in the status panel |

> `avg_value` and `unique_*` columns are optional in practice: if absent the tables
> still render, but those columns will be missing from the detail tables. The charts
> only require `total_value` and `purchase_events` (and the name column).

### 5.2 Do the notebooks already write these files?

From `context.md`, the notebooks currently save **only**:

- `data/cleaned_ecommerce_oct.parquet` (notebook 02)
- `data/customer_analytics_oct.parquet` (notebook 03)
- `data/clustered_customers_oct.parquet` + `outputs/tables/customer_cluster_profile.csv`
  + `outputs/figures/customer_segments_pca.png` (notebook 05)

The **product / category / brand / sales aggregate tables are not saved as files yet.**
Notebook 06 mentions preparing "aggregated tables that can be reused by the dashboard",
but only the cluster artifacts are listed in `context.md`. So to move the
Product / Category, Brand, and Sales pages out of demo mode you must **add export
cells to notebook 06**.

### 5.3 How to add the missing exports (notebook 06)

For **pandas** DataFrames:

```python
import os
os.makedirs("../outputs/tables", exist_ok=True)

top_products.toPandas().to_csv("../outputs/tables/top_products.csv", index=False)
category_perf.toPandas().to_csv("../outputs/tables/category_performance.csv", index=False)
brand_perf.toPandas().to_csv("../outputs/tables/brand_performance.csv", index=False)
daily_sales.toPandas().to_csv("../outputs/tables/daily_sales.csv", index=False)
dow_sales.toPandas().to_csv("../outputs/tables/day_of_week_sales.csv", index=False)
```

For **Spark** DataFrames (if you prefer to write from Spark directly):

```python
top_products.write.mode("overwrite").option("header", True).csv("../outputs/tables/top_products_csv")
```

…then rename/move the part file, or read it back and write a single CSV with pandas.
The simplest reliable route is the pandas version above.

Make sure the exported column names match the contract in **5.1**. If your analysis
DataFrame already has the right names, no renaming is needed.

> Column naming tip: before exporting, run `df.columns.tolist()` and compare with the
> contract. Rename with `df = df.withColumnRenamed(...)` (Spark) or
> `df.rename(columns={...})` (pandas).

### 5.4 Changing the expected paths

If you store outputs somewhere else, edit the `DATA SOURCE PATHS` block near the top
of `main.py`:

```python
DATA_DIR   = BASE_DIR / "data"
TABLES_DIR = BASE_DIR / "outputs" / "tables"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

CLUSTERED_CUSTOMERS_PATH = DATA_DIR / "clustered_customers_oct.parquet"
TOP_PRODUCTS_PATH        = TABLES_DIR / "top_products.csv"
# ...and so on
```

After editing, **restart** the Streamlit app (or use the ↻ Rerun button in the
sidebar) — `@st.cache_data` means file contents are cached between runs.

---

## 6. What each page shows

The sidebar **Navigate** radio switches between seven pages:

1. **📊 Customer Overview** — KPI cards (customers, purchase events, revenue, average
   purchase value, spend per customer), the product/category/brand universe counts, a
   customer-share-by-cluster bar chart, and a spend distribution histogram.
2. **🎯 RFM & Segments** — Recency / Frequency / Monetary histograms (tabs), a cluster
   share donut, and an RFM summary statistics table.
3. **👥 Segment Profiles** — the 6-cluster profile table, a normalised radar chart
   comparing clusters, the PCA projection image (or a synthetic fallback), and cluster
   sizes.
4. **🛍️ Product & Category** — top products and categories by purchase value, with a
   `Products/Categories to show` slider.
5. **🏷️ Brand Performance** — brands ranked by purchase value, with a slider.
6. **📈 Sales Trends** — daily purchase value/events line chart with a date-range filter,
   plus a day-of-week pattern chart.
7. **📝 Methodology & Notes** — pipeline, features, model selection, cleaning decisions,
   limitations, and reproduction commands.

---

## 7. Sidebar filters

| Control | Where | Affects |
|---|---|---|
| **Customer cluster** | All customer pages | Which clusters are included in KPIs and charts |
| **Spend band** | All customer pages (if `spend_band` exists) | Filters customers by Low/Medium/High/Very High spend |
| **Date range / Metric** | 📈 Sales Trends | The daily trend chart only |
| **Day-of-week metric** | 📈 Sales Trends | The weekday chart |
| **Products/Brands to show** | Product / Brand pages | Number of bars shown |

Filters only change the view — they never modify your files.

---

## 8. Customising the dashboard

Everything you're likely to change is centralised near the top of `main.py`:

- **`DATA SOURCE PATHS`** — where files are read from.
- **`DOCUMENTED`** — headline KPI numbers used by demo mode.
- **`CLUSTER_SPEC`** / **`CLUSTER_LABELS`** — cluster descriptions shown in filters and
  tables. If notebook 05 produces different cluster labels, update these.
- **`CLUSTER_COLORS`** — chart colours per cluster.
- **`inr()`** — currency formatting (currently Indian ₹ with Lakh/Crore units).
- **`PAGES`** — the list of pages in the sidebar.

To add a whole new page: add a label to `PAGES`, then add a matching
`elif page == PAGES[n]:` block. Simple to do, and easy for an AI agent to extend.

---

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Sidebar shows 🧪 demo for a section | That file isn't at the expected path (or is empty) | Run the notebook/export step; check the path in `main.py` |
| `ModuleNotFoundError: streamlit` | Dependencies not installed in the active env | `pip install -r requirements.txt` |
| `ImportError: pyarrow` / parquet read fails | `pyarrow` missing | `pip install pyarrow` |
| `KeyError: 'avg_txn_value'` (or similar) | Column name mismatch | Rename the column in the export, or edit `main.py` |
| Charts blank / `total_value` KeyError | CSV missing required columns | Match the contract in 5.1 |
| Changed a file but dashboard still old | Streamlit cache | Rerun (↻) or restart; clear cache from the ☰ menu |
| Runs on demo but says files exist | File size is 0 bytes | Re-export the file |
| `relative_to()` / path errors | Running from a different directory | Always run `streamlit run main.py` from the repo root |

---

## 10. Asking an AI agent for help

The file header in `main.py` documents the data contract, and this guide documents the
column names. If you want an agent to wire things up for you, give it this prompt:

> "Read `dashboard_guide.md`, `main.py` and `context.md`. My notebook writes
> `<path/to/file>` with columns `<list columns>`. Update `main.py` (or the notebook
> export) so the dashboard reads it, mapping my column names to what the dashboard
> expects. Do not change the visual design."

---

## 11. Checklist to go from DEMO → REAL

- [ ] `pip install -r requirements.txt` and `pip install pyarrow`
- [ ] Run notebooks `01 → 06` in order
- [ ] Confirm `data/clustered_customers_oct.parquet` exists (notebook 05)
- [ ] Add export cells to notebook 06 for: `top_products.csv`, `category_performance.csv`,
      `brand_performance.csv`, `daily_sales.csv`, `day_of_week_sales.csv`
- [ ] Check every exported file's columns against section **5.1**
- [ ] Confirm `outputs/figures/customer_segments_pca.png` exists (notebook 05)
- [ ] Run `streamlit run main.py` from the repo root
- [ ] Open **🔌 Data source status** — everything should show ✅
- [ ] If any column errors appear, fix names in the export (or `main.py`) and rerun

---

## 12. Files referenced

| File | Role |
|---|---|
| `main.py` | The dashboard (this guide's subject) |
| `context.md` | Full project context and notebook results |
| `requirements.txt` | Python dependencies |
| `data/*.parquet` | Customer-level outputs (gitignored) |
| `outputs/tables/*.csv` | Aggregate tables (gitignored) |
| `outputs/figures/*.png` | Figures (gitignored) |
| `dashboard/app.py` | Older placeholder app (unchanged) |

Team: **Vaishnavi Poojary · Smith**
