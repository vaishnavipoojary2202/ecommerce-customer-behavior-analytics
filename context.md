# Project Context — E-Commerce Customer Behavior Analytics

> **Big Data Analytics Mini Project**
> Large-scale e-commerce behavior analysis with **Apache Spark / PySpark**, enhanced RFM
> customer segmentation via **K-Means**, and a **Streamlit** dashboard.

This document is the single-file orientation guide for the repository. It summarizes what the
project is, how the pipeline is organized, what each notebook does, what has already been
produced, and what still remains. It is meant to be read before working on any part of the
codebase.

---

## 1. What this project is

The project analyzes **event-level e-commerce data** (views, cart adds, purchases) to understand:

- Who the customers are and how they behave
- How purchasing behavior maps to value (RFM)
- Which customer **segments** exist and how they differ
- Which **products, categories, and brands** drive sales
- How **sales vary over time**

Customer-level behavioral features are engineered into an **Enhanced RFM** representation and
customers are segmented with **K-Means clustering** (Spark MLlib). The result is intended to feed
an interactive dashboard.

It is deliberately built as a **reproducible PySpark pipeline of notebooks**, not a single
monolithic notebook: each stage reads the previous stage's Parquet output and writes its own.

---

## 2. Dataset

**E-Commerce Behavior Data from a Multi-Category Store** (Kaggle)

- Source: <https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store>
- Working file for this project: `2019-Oct.csv` (October 2019 only)
- Expected local path: `data/2019-Oct.csv`
- The raw CSV is **not committed to GitHub** (too large) and is excluded via `.gitignore`.

### Expected columns

| Column | Meaning |
|---|---|
| `event_time` | Timestamp of the event |
| `event_type` | `view`, `cart`, or `purchase` |
| `product_id` | Product identifier |
| `category_id` | Category identifier |
| `category_code` | Human-readable category path (e.g. `electronics.smartphone`) |
| `brand` | Brand name |
| `price` | Item price |
| `user_id` | Customer identifier |
| `user_session` | Session identifier |

### Key data constraints (important for interpreting results)

- The dataset is **event-level**, not order-level.
- There is **no explicit order / transaction ID** and **no quantity field**.
- `user_session` is used only as a **session proxy**, never as a formal order ID.
- Consequently, "basket size" is approximated by *average purchase events per session*, and
  "frequency"/"monetary" are derived from **purchase events**.
- There is **no country/location attribute**, so country-wise analysis is intentionally omitted.
- Only **October 2019** is analyzed.

---

## 3. Pipeline

```text
Raw E-Commerce Events (2019-Oct.csv)
        ↓
01 — Data Exploration
        ↓
02 — Data Cleaning            → cleaned_ecommerce_oct.parquet
        ↓
03 — Customer Analytics       → customer_analytics_oct.parquet
        ↓
04 — Enhanced RFM             → feature set + K selection (Elbow / Silhouette)
        ↓
05 — Customer Segmentation    → clustered_customers_oct.parquet + profiles/figures
        ↓
06 — Product & Sales Analysis → aggregated tables/figures for the dashboard
        ↓
Streamlit Dashboard (dashboard/app.py)  ← currently a placeholder
```

Guiding principles:

- **Reproducibility** — each notebook writes Parquet outputs so later stages don't recompute
  from the raw CSV.
- **Traceability** — each stage documents its decisions, assumptions, and outputs.
- **No hard-coded results** — e.g. K is chosen from this dataset's own Elbow/Silhouette metrics,
  not copied from a paper.

---

## 4. Repository structure

```text
ecommerce-customer-behavior-analytics/
│
├── data/
│   └── README.md                 # dataset description; raw CSV + parquet live here (gitignored)
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_customer_analytics.ipynb
│   ├── 04_enhanced_rfm.ipynb
│   ├── 05_customer_segmentation.ipynb
│   └── 06_product_sales_analysis.ipynb
│
├── src/
│   └── README.md                 # placeholder for reusable Python utilities (not yet populated)
│
├── dashboard/
│   └── app.py                    # Streamlit dashboard (placeholder)
│
├── outputs/
│   ├── figures/                  # generated charts (gitignored, .gitkeep tracked)
│   └── tables/                   # generated CSV tables (gitignored, .gitkeep tracked)
│
├── requirements.txt
├── .gitignore
├── README.md
└── context.md                    # this file
```

---

## 5. Notebook responsibilities and current results

### `01_data_exploration.ipynb` — Understand the raw data
Explores dataset dimensions, schema and sample records, event-type distribution, unique
users/products/sessions, missing values, price statistics, event-time range. Establishes the
assumptions that drive cleaning.

### `02_data_cleaning.ipynb` — Clean and validate
Documented cleaning decisions:

1. **Missing `user_session`** — 2 records removed (session analysis requires a valid session ID).
2. **Non-positive prices** — 68,673 records removed (68,523 views, 150 cart adds; no purchases affected).
3. **Missing `category_code`** — replaced with `"unknown"` (retained due to high missingness).
4. **Missing `brand`** — replaced with `"unknown"` (retained, descriptive only).
5. **Event types** — retained only `view`, `cart`, `purchase`.
6. **Repeated purchase groups** — 76 groups identified; retained (no transaction ID, so they can't
   be confidently called duplicates).

**Output:** `data/cleaned_ecommerce_oct.parquet` — **42,380,089 records × 9 attributes**
(≈99.84% of the original).

### `03_customer_analytics.ipynb` — Customer-level summaries
Built customer-level features: purchase frequency, purchase sessions, unique products purchased,
total spend, average purchase value, first/last purchase timestamps; engagement ratios
(view→cart, cart→purchase, purchase→view); spend per session, purchases per session, views per
purchase; descriptive spend bands (Low/Medium/High/Very High); and recency relative to the latest
October purchase. Skew was noted in total spend and average purchase value.

**Output:** `data/customer_analytics_oct.parquet` — **347,118 customers × 18 features**, no missing
values. Core RFM: `recency_days`, `purchase_events`, `total_spend`.

### `04_enhanced_rfm.ipynb` — Feature engineering + K selection
Extends traditional RFM with seven features:

1. Recency  2. Frequency  3. Monetary  4. Average Transaction Value (ATV)
5. Average Purchase Events per Session  6. Amount Slope  7. Frequency Slope

Slope features were signed-log transformed; non-negative features used `log1p`; then
`StandardScaler` (Spark). K was selected with Elbow (WSSSE) and **Silhouette** on a reproducible
10% sample of **34,603 customers**; the evaluation supported **K = 6**, and the final model was
trained on all **347,118** purchasing customers.

### `05_customer_segmentation.ipynb` — Final clustering
Final K-Means (**K = 6**) applied to the 347,118 customers using the seven standardized features.

Cluster profiles (from the notebook):

| Cluster | Share | Avg Recency | Avg Frequency | Avg Monetary | Avg ATV | Events/Session | Profile |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 28.76% | 17.31 | 1.20 | ₹70.83 | ₹61.94 | 1.01 | Low-Activity, Low-Spend |
| 1 | 4.43% | 15.72 | 2.86 | ₹1,018.87 | ₹340.98 | 1.87 | Moderate-Frequency, High-Value |
| 2 | 35.66% | 18.59 | 1.32 | ₹546.10 | ₹423.91 | 1.00 | Infrequent, High-ATV |
| 3 | 17.26% | 3.86 | 1.62 | ₹422.33 | ₹270.17 | 1.01 | Recently Active, Low-Frequency |
| 4 | 4.65% | 8.23 | 9.41 | ₹3,501.22 | ₹358.40 | 1.29 | High-Frequency, High-Value |
| 5 | 9.24% | 12.88 | 5.16 | ₹1,801.13 | ₹331.63 | 1.76 | Frequent, High-Spend |

**Output artifacts:**
`outputs/tables/customer_cluster_profile.csv`,
`outputs/figures/customer_segments_pca.png`,
`data/clustered_customers_oct.parquet` (local, gitignored).

### `06_product_sales_analysis.ipynb` — Product, category, brand, time
Headline results for October 2019:

- Purchase events: **742,849**
- Purchasing customers: **347,118**
- Unique purchased products: **42,241**
- Unique purchased categories: **567**
- Unique purchased brands: **1,985**
- Total purchase value: **≈ ₹229.96 million**
- Average purchase-event value: **≈ ₹309.56**

Highlights: `electronics.smartphone` was the top category by purchase value; **Apple** and
**Samsung** led brand value; peak daily purchase value was **2019-10-16 (≈ ₹9.81M)**; **Wednesday**
had the most purchase events (119,201) and **Saturday** the fewest (96,012). Country analysis was
skipped (no location field).

---

## 6. Data & output artifacts

Large or generated files are **kept locally and excluded from GitHub**.

| Artifact | Path | Committed? |
|---|---|---|
| Raw events | `data/2019-Oct.csv` | No (gitignored) |
| Cleaned events | `data/cleaned_ecommerce_oct.parquet` | No |
| Customer analytics | `data/customer_analytics_oct.parquet` | No |
| Clustered customers | `data/clustered_customers_oct.parquet` | No |
| Cluster profile table | `outputs/tables/customer_cluster_profile.csv` | No (gitignored) |
| PCA segment figure | `outputs/figures/customer_segments_pca.png` | No (gitignored) |

> Note: the `.gitignore` excludes `*.csv`, `data/*.parquet`, and `outputs/**`, so the generated
> artifacts described above exist only in a local environment that has run the notebooks.

---

## 7. Technology stack

- **Python**
- **Apache Spark / PySpark** — distributed processing
- **Spark MLlib** — `StandardScaler`, K-Means
- **Pandas / NumPy**
- **Matplotlib / Seaborn / Plotly** — visualizations
- **scikit-learn** — supporting ML/metrics
- **Streamlit** — dashboard
- **Jupyter** — notebook environment
- **Git & GitHub**

Declared in `requirements.txt`: `pyspark`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`,
`scikit-learn`, `streamlit`.

---

## 8. Dashboard (`dashboard/app.py`) — status: placeholder

`app.py` is currently a stub Streamlit app:

- Sets the page config (title "E-Commerce Customer Behavior Analytics", icon 🛒, wide layout).
- Shows a title, caption, and an `st.info` note that data will be connected after notebooks finish.
- Lists **planned sections**:
  - Customer overview
  - RFM and customer segments
  - Segment profiles
  - Product and category performance
  - Sales trends

There is **no data loading, no charts, and no interactivity yet**. The intended data source is the
processed Parquet outputs (`data/*.parquet`, `outputs/tables/*`).

---

## 9. Current status summary

| Area | State |
|---|---|
| Notebooks 01–06 | **Implemented**, with documented final results and summaries |
| Raw data | Local only, gitignored |
| Intermediate Parquet | Produced locally (not in repo) |
| `src/` reusable utilities | **Not started** (placeholder README only) |
| `dashboard/app.py` | **Placeholder** — needs wiring to Parquet outputs |
| Root README status line | Says "setup complete" — **out of date** relative to notebooks |

**What remains:** connect the dashboard to the processed Parquet/tables, and optionally extract
reusable logic from the notebooks into `src/`.

---

## 10. How to run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Provide the dataset** — download October 2019 CSV from Kaggle and place it at
   `data/2019-Oct.csv`.
3. **Run notebooks in order** `01 → 06` in Jupyter. Each writes its Parquet output used by the next;
   artifacts land in `data/`, `outputs/figures/`, and `outputs/tables/`.
4. **Launch the dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

---

## 11. Team

- **Vaishnavi Poojary**
- **Smith**
