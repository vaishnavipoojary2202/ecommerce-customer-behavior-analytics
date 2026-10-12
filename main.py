"""
============================================================================
 E-COMMERCE CUSTOMER BEHAVIOR ANALYTICS — STREAMLIT DASHBOARD (frontend)
============================================================================

This is the frontend/demo dashboard for the Big Data Analytics mini project.
It visualises the results produced by notebooks 01-06 (see context.md).

HOW THE DATA IS WIRED
---------------------
The project keeps its large generated files OUT of GitHub (see .gitignore),
so the real outputs only exist in a local environment that has run the
notebooks. This dashboard therefore:

  1) TRIES to load the real generated files from the paths in the
     "DATA SOURCE PATHS" section below.
  2) If a file is missing, it FALLS BACK to an embedded, self-contained
     "demo" dataset whose numbers are taken from the notebook summaries
     documented in context.md, so the UI always renders.

>>> TO CONNECT REAL DATA: run notebooks 01-06 (they write the files listed
>>> below), then restart this app. No code change should be needed — just
>>> make sure the file paths and column names match. If the owner is unsure,
>>> point an AI agent at this header comment and the paths below.

Expected files / columns (from context.md):
  data/cleaned_ecommerce_oct.parquet     -> event-level cleaned data (42,380,089 rows)
  data/customer_analytics_oct.parquet    -> 347,118 customers x 18 features
  data/clustered_customers_oct.parquet   -> customer features + "cluster" assignment
  outputs/tables/customer_cluster_profile.csv
  outputs/figures/customer_segments_pca.png
  outputs/tables/top_products.csv        -> (product_id, purchase_events, unique_customers, total_value)
  outputs/tables/category_performance.csv-> (category_code, purchase_events, unique_products, unique_customers, total_value)
  outputs/tables/brand_performance.csv   -> (brand, purchase_events, unique_products, unique_customers, total_value)
  outputs/tables/daily_sales.csv         -> (date, purchase_events, total_value)
  outputs/tables/day_of_week_sales.csv   -> (day_of_week, purchase_events, total_value)

Run with:
    streamlit run main.py
============================================================================
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================================
# DATA SOURCE PATHS  <-- point these at the notebook outputs
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TABLES_DIR = BASE_DIR / "outputs" / "tables"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

CLEANED_EVENTS_PATH = DATA_DIR / "cleaned_ecommerce_oct.parquet"
CUSTOMER_ANALYTICS_PATH = DATA_DIR / "customer_analytics_oct.parquet"
CLUSTERED_CUSTOMERS_PATH = DATA_DIR / "clustered_customers_oct.parquet"
CLUSTER_PROFILE_PATH = TABLES_DIR / "customer_cluster_profile.csv"
PCA_FIGURE_PATH = FIGURES_DIR / "customer_segments_pca.png"
TOP_PRODUCTS_PATH = TABLES_DIR / "top_products.csv"
CATEGORY_PERFORMANCE_PATH = TABLES_DIR / "category_performance.csv"
BRAND_PERFORMANCE_PATH = TABLES_DIR / "brand_performance.csv"
DAILY_SALES_PATH = TABLES_DIR / "daily_sales.csv"
DOW_SALES_PATH = TABLES_DIR / "day_of_week_sales.csv"

# All paths are also listed here so the sidebar can report what was found.
EXPECTED_FILES = [
    ("Cleaned events", CLEANED_EVENTS_PATH),
    ("Customer analytics", CUSTOMER_ANALYTICS_PATH),
    ("Clustered customers", CLUSTERED_CUSTOMERS_PATH),
    ("Cluster profile", CLUSTER_PROFILE_PATH),
    ("PCA figure", PCA_FIGURE_PATH),
    ("Top products", TOP_PRODUCTS_PATH),
    ("Category performance", CATEGORY_PERFORMANCE_PATH),
    ("Brand performance", BRAND_PERFORMANCE_PATH),
    ("Daily sales", DAILY_SALES_PATH),
    ("Day-of-week sales", DOW_SALES_PATH),
]

# ============================================================================
# DOCUMENTED HEADLINE NUMBERS (context.md / notebook 06) — used for KPI cards
# and as the basis of the embedded demo data.
# ============================================================================
DOCUMENTED = {
    "total_purchase_events": 742_849,
    "purchasing_customers": 347_118,
    "unique_products": 42_241,
    "unique_categories": 567,
    "unique_brands": 1_985,
    "total_purchase_value": 229_960_000.0,   # approx ₹229.96 million
    "avg_purchase_value": 309.56,
}

# Cluster specification from notebook 05 (id, label, n, recency, freq, monetary, atv, events/session)
CLUSTER_SPEC = [
    (0, "Low-Activity, Low-Spend Customers",          99_824, 17.31, 1.20,    70.83,  61.94, 1.01),
    (1, "Moderate-Frequency, High-Value Customers",    15_363, 15.72, 2.86, 1_018.87, 340.98, 1.87),
    (2, "Infrequent, High-ATV Customers",             123_777, 18.59, 1.32,   546.10, 423.91, 1.00),
    (3, "Recently Active, Low-Frequency Customers",    59_926,  3.86, 1.62,   422.33, 270.17, 1.01),
    (4, "High-Frequency, High-Value Customers",        16_156,  8.23, 9.41, 3_501.22, 358.40, 1.29),
    (5, "Frequent, High-Spend Customers",              32_072, 12.88, 5.16, 1_801.13, 331.63, 1.76),
]
CLUSTER_LABELS = {cid: label for cid, label, *_ in CLUSTER_SPEC}
CLUSTER_COLORS = {
    0: "#8c8c8c", 1: "#2ca02c", 2: "#1f77b4",
    3: "#ff7f0e", 4: "#d62728", 5: "#9467bd",
}
SPEND_BANDS = ["Low Spend", "Medium Spend", "High Spend", "Very High Spend"]


# ============================================================================
# Helpers
# ============================================================================
def inr(value: float) -> str:
    """Format a rupee amount using Indian units (Lakh / Crore)."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "—"
    if abs(value) >= 1e7:
        return f"₹{value / 1e7:,.2f} Cr"
    if abs(value) >= 1e5:
        return f"₹{value / 1e5:,.2f} L"
    return f"₹{value:,.2f}"


def _file_exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


# ============================================================================
# Real-data loaders (try file first; return None if unavailable)
# ============================================================================
@st.cache_data(show_spinner="Loading customer analytics…")
def try_load_customer_analytics() -> pd.DataFrame | None:
    if not _file_exists(CUSTOMER_ANALYTICS_PATH):
        return None
    return pd.read_parquet(CUSTOMER_ANALYTICS_PATH)


@st.cache_data(show_spinner="Loading clustered customers…")
def try_load_clustered_customers() -> pd.DataFrame | None:
    if not _file_exists(CLUSTERED_CUSTOMERS_PATH):
        return None
    return pd.read_parquet(CLUSTERED_CUSTOMERS_PATH)


@st.cache_data(show_spinner="Loading cluster profile…")
def try_load_cluster_profile() -> pd.DataFrame | None:
    if not _file_exists(CLUSTER_PROFILE_PATH):
        return None
    return pd.read_csv(CLUSTER_PROFILE_PATH)


@st.cache_data(show_spinner="Loading product/category/brand tables…")
def try_load_table(path: Path) -> pd.DataFrame | None:
    if not _file_exists(path):
        return None
    return pd.read_csv(path)


# ============================================================================
# Embedded DEMO data (fallback so the dashboard always renders)
# Numbers are derived from the notebook summaries in context.md.
# ============================================================================
@st.cache_data(show_spinner="Preparing demo dataset…")
def build_demo_customers() -> pd.DataFrame:
    """Reproduce 347,118 customers across the 6 documented clusters."""
    rng = np.random.default_rng(42)
    frames = []
    for cid, label, n, rec, freq, mon, atv, evs in CLUSTER_SPEC:
        recency = np.clip(rng.normal(rec, rec * 0.35 + 1.0, n), 0, 30)
        frequency = np.clip(rng.normal(freq, max(freq * 0.15, 0.1), n), 1, None)
        monetary = np.clip(rng.normal(mon, mon * 0.45 + 5.0, n), 0.5, None)
        atv_arr = np.clip(rng.normal(atv, atv * 0.30 + 5.0, n), 1, None)
        evs_arr = np.clip(rng.normal(evs, evs * 0.12 + 0.02, n), 1, None)
        frames.append(
            pd.DataFrame(
                {
                    "cluster": cid,
                    "cluster_label": label,
                    "recency_days": recency,
                    "purchase_events": frequency,
                    "total_spend": monetary,
                    "avg_txn_value": atv_arr,
                    "events_per_session": evs_arr,
                }
            )
        )
    df = pd.concat(frames, ignore_index=True)
    df["user_id"] = np.arange(1, len(df) + 1)
    df["spend_band"] = pd.qcut(
        df["total_spend"], q=4, labels=SPEND_BANDS, duplicates="drop"
    ).astype(str)
    return df


def _demo_from_value_dict(
    key: str, rows: list[tuple[str, float, int, int]], total_events: int
) -> pd.DataFrame:
    """Build a demo aggregate table from (key, total_value, events, unique_products)."""
    records = []
    for name, value, events, uniq_products in rows:
        records.append(
            {
                key: name,
                "purchase_events": events,
                "unique_products": uniq_products,
                "unique_customers": int(round(events * 0.42)),
                "total_value": value,
                "avg_value": value / events if events else 0.0,
            }
        )
    return pd.DataFrame(records).sort_values("total_value", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def build_demo_top_products() -> pd.DataFrame:
    rows = [
        ("P1001", 9_420_000.0, 3_050, 1),
        ("P1002", 8_150_000.0, 2_980, 1),
        ("P1003", 6_740_000.0, 2_410, 1),
        ("P1004", 5_980_000.0, 2_120, 1),
        ("P1005", 5_120_000.0, 4_050, 1),
        ("P1006", 4_780_000.0, 1_990, 1),
        ("P1007", 4_310_000.0, 3_640, 1),
        ("P1008", 3_960_000.0, 1_760, 1),
        ("P1009", 3_540_000.0, 3_010, 1),
        ("P1010", 3_180_000.0, 2_870, 1),
    ]
    return _demo_from_value_dict("product_id", rows, DOCUMENTED["total_purchase_events"])


@st.cache_data(show_spinner=False)
def build_demo_categories() -> pd.DataFrame:
    rows = [
        ("electronics.smartphone", 58_200_000.0, 263_000, 320),
        ("electronics.audio.headphone", 22_400_000.0, 78_000, 210),
        ("appliances.kitchen.washer", 18_900_000.0, 12_000, 45),
        ("electronics.video.tv", 16_300_000.0, 21_000, 90),
        ("computers.notebook", 14_100_000.0, 19_000, 130),
        ("appliances.environment.vacuum", 12_700_000.0, 26_000, 70),
        ("electronics.clocks", 9_400_000.0, 34_000, 60),
        ("appliances.kitchen.refrigerators", 8_800_000.0, 9_000, 40),
        ("computers.desktop", 7_200_000.0, 11_000, 85),
        ("electronics.audio.subwoofer", 5_600_000.0, 15_000, 55),
        ("appliances.kitchen.oven", 5_100_000.0, 13_000, 48),
        ("electronics.video.projector", 4_300_000.0, 7_000, 30),
        ("unknown", 12_000_000.0, 90_000, 400),
    ]
    return _demo_from_value_dict("category_code", rows, DOCUMENTED["total_purchase_events"])


@st.cache_data(show_spinner=False)
def build_demo_brands() -> pd.DataFrame:
    rows = [
        ("apple", 46_500_000.0, 88_000, 210),
        ("samsung", 38_200_000.0, 121_000, 540),
        ("xiaomi", 21_400_000.0, 74_000, 260),
        ("huawei", 17_800_000.0, 52_000, 190),
        ("oppo", 12_200_000.0, 41_000, 150),
        ("honor", 10_500_000.0, 36_000, 120),
        ("acer", 8_800_000.0, 22_000, 95),
        ("asus", 7_900_000.0, 20_000, 110),
        ("lenovo", 6_700_000.0, 18_000, 130),
        ("sony", 6_100_000.0, 14_000, 80),
        ("lg", 5_400_000.0, 12_500, 85),
        ("hp", 5_000_000.0, 11_000, 100),
        ("dell", 4_600_000.0, 9_800, 90),
        ("bosch", 4_100_000.0, 8_200, 60),
        ("philips", 3_800_000.0, 7_600, 55),
        ("unknown", 26_000_000.0, 190_000, 900),
    ]
    return _demo_from_value_dict("brand", rows, DOCUMENTED["total_purchase_events"])


@st.cache_data(show_spinner=False)
def build_demo_daily_sales() -> pd.DataFrame:
    dates = pd.date_range("2019-10-01", "2019-10-31", freq="D")
    rng = np.random.default_rng(7)
    # Weekday effect: Wednesday highest, Saturday lowest (notebook 06).
    weekday_factor = {0: 0.98, 1: 1.00, 2: 1.08, 3: 1.01, 4: 0.97, 5: 0.88, 6: 0.95}
    base_events = 23_963
    events = [
        int(base_events * weekday_factor[d.weekday()] * rng.normal(1.0, 0.05))
        for d in dates
    ]
    avg_value = 309.56
    value = [e * avg_value * rng.normal(1.0, 0.04) for e in events]
    df = pd.DataFrame({"date": dates, "purchase_events": events, "total_value": value})
    # Force the documented peak: 2019-10-16 ≈ ₹9.81M.
    peak_idx = df.index[df["date"] == pd.Timestamp("2019-10-16")][0]
    df.loc[peak_idx, "total_value"] = 9_810_000.0
    return df


@st.cache_data(show_spinner=False)
def build_demo_day_of_week() -> pd.DataFrame:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # Documented: Wednesday 119,201 (max) and Saturday 96,012 (min).
    events = {
        "Monday": 106_500, "Tuesday": 111_200, "Wednesday": 119_201,
        "Thursday": 109_400, "Friday": 103_800, "Saturday": 96_012, "Sunday": 96_736,
    }
    df = pd.DataFrame(
        {"day_of_week": order, "purchase_events": [events[d] for d in order]}
    )
    df["total_value"] = df["purchase_events"] * 309.56
    return df


# ============================================================================
# Resolved data (real if available, else demo) + data-source status
# ============================================================================
def resolve_customers() -> tuple[pd.DataFrame, bool]:
    real = try_load_clustered_customers()
    if real is None:
        real = try_load_customer_analytics()
    if real is not None and "cluster" in real.columns:
        return real, True
    return build_demo_customers(), False


def resolve_table(path: Path, demo_builder) -> tuple[pd.DataFrame, bool]:
    real = try_load_table(path)
    if real is not None:
        return real, True
    return demo_builder(), False


def render_data_status() -> None:
    with st.sidebar.expander("🔌 Data source status", expanded=False):
        st.caption(
            "Real notebook outputs are loaded when present; otherwise an "
            "embedded demo dataset is shown."
        )
        for label, path in EXPECTED_FILES:
            found = _file_exists(path)
            icon = "✅" if found else "🧪 demo"
            st.write(f"{icon} — {label}")
            st.caption(f"`{path.relative_to(BASE_DIR)}`")


# ============================================================================
# Page config
# ============================================================================
st.set_page_config(
    page_title="E-Commerce Customer Behavior Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Sidebar navigation + filters
# ============================================================================
st.sidebar.title("🛒 Analytics")
st.sidebar.caption("PySpark · RFM · K-Means segmentation")

PAGES = [
    "📊 Customer Overview",
    "🎯 RFM & Segments",
    "👥 Segment Profiles",
    "🛍️ Product & Category",
    "🏷️ Brand Performance",
    "📈 Sales Trends",
    "📝 Methodology & Notes",
]
page = st.sidebar.radio("Navigate", PAGES, index=0)

customers, customers_is_real = resolve_customers()

st.sidebar.divider()
st.sidebar.subheader("Filters")

all_clusters = sorted(customers["cluster"].unique().tolist())
selected_clusters = st.sidebar.multiselect(
    "Customer cluster",
    options=all_clusters,
    default=all_clusters,
    format_func=lambda c: f"Cluster {c} — {CLUSTER_LABELS.get(int(c), '')}",
)

if "spend_band" in customers.columns:
    band_options = [b for b in SPEND_BANDS if b in customers["spend_band"].unique()]
    selected_bands = st.sidebar.multiselect(
        "Spend band", options=band_options, default=band_options
    )
else:
    selected_bands = None

# Apply global filters
mask = customers["cluster"].isin(selected_clusters)
if selected_bands is not None:
    mask &= customers["spend_band"].isin(selected_bands)
cdf = customers[mask]

st.sidebar.divider()
render_data_status()
if not customers_is_real:
    st.sidebar.warning(
        "Running on **demo data**. Run notebooks 01–06 to generate the real "
        "outputs in `data/` and `outputs/tables/`.",
        icon="🧪",
    )

# ============================================================================
# Shared helpers for sections
# ============================================================================
def kpi_row(df: pd.DataFrame) -> None:
    total_customers = int(len(df))
    purchases = int(round(df["purchase_events"].sum()))
    revenue = float(df["total_spend"].sum())
    aov = revenue / purchases if purchases else 0.0
    spend_per_customer = revenue / total_customers if total_customers else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Customers", f"{total_customers:,}")
    c2.metric("Purchase events", f"{purchases:,}")
    c3.metric("Total purchase value", inr(revenue))
    c4.metric("Avg purchase value", inr(aov))
    c5.metric("Spend / customer", inr(spend_per_customer))


def cluster_palette(df: pd.DataFrame) -> dict:
    return {cid: CLUSTER_COLORS.get(int(cid), "#888") for cid in sorted(df["cluster"].unique())}


def add_cluster_labels(series: pd.Series) -> pd.Series:
    return series.map(lambda c: f"Cluster {int(c)}")


# ============================================================================
# SECTION 1 — Customer Overview
# ============================================================================
if page == PAGES[0]:
    st.title("📊 Customer Overview")
    st.caption(
        "High-level health of the October 2019 customer base. "
        "Numbers react to the sidebar filters."
    )

    kpi_row(cdf)

    st.divider()
    col_a, col_b = st.columns([2, 3])

    with col_a:
        st.subheader("Event universe")
        st.caption(
            "Unique products / categories / brands are total dimensions from the "
            "purchase events (not affected by customer filters)."
        )
        e1, e2, e3 = st.columns(3)
        e1.metric("Products", f"{DOCUMENTED['unique_products']:,}")
        e2.metric("Categories", f"{DOCUMENTED['unique_categories']:,}")
        e3.metric("Brands", f"{DOCUMENTED['unique_brands']:,}")

    with col_b:
        st.subheader("Customer share by cluster")
        share = (
            cdf.groupby("cluster")
            .size()
            .reset_index(name="customers")
            .assign(cluster_label=lambda d: d["cluster"].map(CLUSTER_LABELS))
        )
        fig = px.bar(
            share,
            x="customers",
            y="cluster_label",
            orientation="h",
            color="cluster",
            color_discrete_map=cluster_palette(cdf),
            text="customers",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(
            showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Customers", yaxis_title="",
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Spend distribution")
    fig = px.histogram(
        cdf,
        x="total_spend",
        color=add_cluster_labels(cdf["cluster"]),
        nbins=60,
        log_y=True,
        labels={"total_spend": "Total spend (₹)", "color": "Cluster"},
    )
    fig.update_layout(
        height=380, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Total spend (₹) — log count axis",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Total spend is strongly right-skewed, as noted in notebook 03.")


# ============================================================================
# SECTION 2 — RFM & Segments
# ============================================================================
elif page == PAGES[1]:
    st.title("🎯 RFM & Segments")
    st.caption(
        "Recency, Frequency and Monetary (RFM) distributions plus the "
        "K-Means cluster size breakdown."
    )

    kpi_row(cdf)
    st.divider()

    tab_rec, tab_freq, tab_mon, tab_share = st.tabs(
        ["Recency", "Frequency", "Monetary", "Cluster share"]
    )

    with tab_rec:
        fig = px.histogram(
            cdf, x="recency_days", color=add_cluster_labels(cdf["cluster"]),
            nbins=50, labels={"recency_days": "Recency (days)", "color": "Cluster"},
        )
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Recency = days since the customer's latest purchase (notebook 03).")

    with tab_freq:
        fig = px.histogram(
            cdf, x="purchase_events", color=add_cluster_labels(cdf["cluster"]),
            nbins=40, log_y=True,
            labels={"purchase_events": "Purchase events (frequency)", "color": "Cluster"},
        )
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab_mon:
        fig = px.histogram(
            cdf, x="total_spend", color=add_cluster_labels(cdf["cluster"]),
            nbins=60, log_y=True,
            labels={"total_spend": "Monetary — total spend (₹)", "color": "Cluster"},
        )
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab_share:
        share = cdf.groupby("cluster").size().reset_index(name="customers")
        share["cluster_label"] = share["cluster"].map(CLUSTER_LABELS)
        fig = px.pie(
            share, names="cluster_label", values="customers", hole=0.45,
            color="cluster", color_discrete_map=cluster_palette(cdf),
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("RFM summary")
    summary = pd.DataFrame(
        {
            "Recency (days)": cdf["recency_days"].describe(),
            "Frequency (events)": cdf["purchase_events"].describe(),
            "Monetary (₹)": cdf["total_spend"].describe(),
        }
    ).T
    st.dataframe(summary.style.format("{:,.2f}"), use_container_width=True)


# ============================================================================
# SECTION 3 — Segment Profiles
# ============================================================================
elif page == PAGES[2]:
    st.title("👥 Segment Profiles")
    st.caption(
        "Behavioural profile of each K-Means cluster (K = 6), plus the PCA "
        "projection of the seven-feature space."
    )

    profile = (
        cdf.groupby("cluster")
        .agg(
            customers=("user_id", "count"),
            avg_recency=("recency_days", "mean"),
            avg_frequency=("purchase_events", "mean"),
            avg_monetary=("total_spend", "mean"),
            avg_atv=("avg_txn_value", "mean"),
            avg_events_per_session=("events_per_session", "mean"),
        )
        .reset_index()
    )
    profile["share_pct"] = profile["customers"] / profile["customers"].sum() * 100
    profile["profile"] = profile["cluster"].map(CLUSTER_LABELS)

    display = profile[
        ["cluster", "share_pct", "avg_recency", "avg_frequency",
         "avg_monetary", "avg_atv", "avg_events_per_session", "profile"]
    ].rename(
        columns={
            "cluster": "Cluster",
            "share_pct": "Share %",
            "avg_recency": "Avg Recency",
            "avg_frequency": "Avg Frequency",
            "avg_monetary": "Avg Monetary (₹)",
            "avg_atv": "Avg ATV (₹)",
            "avg_events_per_session": "Events/Session",
            "profile": "Descriptive Profile",
        }
    )
    st.subheader("Cluster profile table")
    st.dataframe(
        display.style.format(
            {
                "Share %": "{:.2f}%",
                "Avg Recency": "{:.2f}",
                "Avg Frequency": "{:.2f}",
                "Avg Monetary (₹)": "{:,.2f}",
                "Avg ATV (₹)": "{:,.2f}",
                "Events/Session": "{:.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    col_table, col_radar = st.columns([1, 1])

    with col_table:
        st.subheader("Normalised feature comparison")
        metrics = ["avg_recency", "avg_frequency", "avg_monetary", "avg_atv", "avg_events_per_session"]
        norm = profile.copy()
        for m in metrics:
            lo, hi = norm[m].min(), norm[m].max()
            norm[m] = (norm[m] - lo) / (hi - lo) if hi > lo else 0.5
        fig = go.Figure()
        for _, row in norm.iterrows():
            fig.add_trace(
                go.Scatterpolar(
                    r=[row[m] for m in metrics],
                    theta=["Recency", "Frequency", "Monetary", "ATV", "Events/Session"],
                    name=f"Cluster {int(row['cluster'])}",
                    line=dict(color=CLUSTER_COLORS.get(int(row["cluster"]), "#888")),
                    fill="toself",
                    opacity=0.35,
                )
            )
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True, height=460, margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_radar:
        st.subheader("PCA projection")
        if _file_exists(PCA_FIGURE_PATH):
            st.image(str(PCA_FIGURE_PATH), caption="customer_segments_pca.png (notebook 05)")
        else:
            # Fallback synthetic 2-D projection of the clusters.
            rng = np.random.default_rng(11)
            pts = []
            for _, row in profile.iterrows():
                n = min(int(row["customers"]), 4000)
                x = rng.normal(row["avg_monetary"] / 500, 1.2, n)
                y = rng.normal(row["avg_frequency"], 0.6, n)
                pts.append(pd.DataFrame({"x": x, "y": y, "cluster": int(row["cluster"])}))
            proj = pd.concat(pts, ignore_index=True)
            proj["cluster_label"] = proj["cluster"].map(lambda c: f"Cluster {c}")
            fig = px.scatter(
                proj, x="x", y="y", color="cluster_label",
                color_discrete_map={f"Cluster {k}": v for k, v in CLUSTER_COLORS.items()},
                opacity=0.5,
                labels={"x": "PCA component 1", "y": "PCA component 2", "cluster_label": "Cluster"},
            )
            fig.update_layout(height=460, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Demo projection — run notebook 05 to render the real "
                "`outputs/figures/customer_segments_pca.png`."
            )

    st.divider()
    st.subheader("Cluster size")
    fig = px.bar(
        profile,
        x="cluster", y="customers",
        color="profile", text="customers",
        labels={"cluster": "Cluster", "customers": "Customers", "profile": "Profile"},
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# SECTION 4 — Product & Category
# ============================================================================
elif page == PAGES[3]:
    st.title("🛍️ Product & Category Performance")
    st.caption("Top products and categories by purchase value (notebook 06).")

    products, products_real = resolve_table(TOP_PRODUCTS_PATH, build_demo_top_products)
    categories, categories_real = resolve_table(CATEGORY_PERFORMANCE_PATH, build_demo_categories)

    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("Products to show", 5, min(20, len(products)), 10)
    with col2:
        cat_n = st.slider("Categories to show", 5, min(20, len(categories)), 10)

    st.divider()
    st.subheader("Top products by purchase value")
    prod = products.head(top_n).copy()
    fig = px.bar(
        prod.sort_values("total_value"),
        x="total_value", y="product_id", orientation="h",
        text="total_value",
        labels={"total_value": "Purchase value (₹)", "product_id": "Product"},
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(height=430, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(prod, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Category performance")
    cat = categories.head(cat_n).copy()
    fig = px.bar(
        cat.sort_values("total_value"),
        x="total_value", y="category_code", orientation="h",
        text="total_value",
        labels={"total_value": "Purchase value (₹)", "category_code": "Category"},
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category detail")
    st.dataframe(
        cat[["category_code", "purchase_events", "unique_products", "unique_customers", "total_value", "avg_value"]],
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "`electronics.smartphone` was the top category by purchase value in "
        "October 2019 (notebook 06)."
    )


# ============================================================================
# SECTION 5 — Brand Performance
# ============================================================================
elif page == PAGES[4]:
    st.title("🏷️ Brand Performance")
    st.caption("Brands ranked by purchase value and product breadth (notebook 06).")

    brands, brands_real = resolve_table(BRAND_PERFORMANCE_PATH, build_demo_brands)
    brand_n = st.slider("Brands to show", 5, min(20, len(brands)), 12)

    st.divider()
    top = brands.head(brand_n).copy()
    fig = px.bar(
        top.sort_values("total_value"),
        x="total_value", y="brand", orientation="h",
        text="total_value", color="total_value", color_continuous_scale="Blues",
        labels={"total_value": "Purchase value (₹)", "brand": "Brand"},
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(
        height=520, coloraxis_showscale=False, margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Brand detail")
    st.dataframe(
        top[["brand", "purchase_events", "unique_products", "unique_customers", "total_value", "avg_value"]],
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Apple and Samsung accounted for substantial purchase value (notebook 06).")


# ============================================================================
# SECTION 6 — Sales Trends
# ============================================================================
elif page == PAGES[5]:
    st.title("📈 Sales Trends")
    st.caption("Daily and day-of-week purchase activity across October 2019 (notebook 06).")

    daily, daily_real = resolve_table(DAILY_SALES_PATH, build_demo_daily_sales)
    dow, dow_real = resolve_table(DOW_SALES_PATH, build_demo_day_of_week)

    daily["date"] = pd.to_datetime(daily["date"])

    st.sidebar.divider()
    st.sidebar.subheader("Sales filters")
    min_d, max_d = daily["date"].min().date(), daily["date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d
    )
    metric = st.sidebar.radio("Metric", ["Purchase value", "Purchase events"])

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        d = daily[(daily["date"].dt.date >= start) & (daily["date"].dt.date <= end)]
    else:
        d = daily

    y_col = "total_value" if metric == "Purchase value" else "purchase_events"
    total = d[y_col].sum()
    peak_row = d.loc[d[y_col].idxmax()] if len(d) else None

    c1, c2, c3 = st.columns(3)
    c1.metric("Days shown", f"{len(d):,}")
    c2.metric("Total", inr(total) if metric == "Purchase value" else f"{int(total):,}")
    if peak_row is not None:
        peak_val = inr(peak_row["total_value"]) if metric == "Purchase value" else f"{int(peak_row['purchase_events']):,}"
        c3.metric("Peak day", peak_row["date"].strftime("%d %b %Y"), delta=peak_val, delta_color="off")

    st.divider()
    fig = px.line(
        d, x="date", y=y_col, markers=True,
        labels={"date": "Date", "total_value": "Purchase value (₹)", "purchase_events": "Purchase events"},
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Day-of-week pattern")
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = dow.copy()
    dow["day_of_week"] = pd.Categorical(dow["day_of_week"], categories=dow_order, ordered=True)
    dow = dow.sort_values("day_of_week")
    metric_dow = st.radio("Day-of-week metric", ["Purchase events", "Purchase value"], horizontal=True)
    ydow = "purchase_events" if metric_dow == "Purchase events" else "total_value"
    fig = px.bar(
        dow, x="day_of_week", y=ydow, text=ydow,
        color=ydow, color_continuous_scale="Teal",
        labels={"day_of_week": "", "purchase_events": "Purchase events", "total_value": "Purchase value (₹)"},
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}", textposition="outside"
    )
    fig.update_layout(height=400, coloraxis_showscale=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Wednesday recorded the most purchase events; Saturday the fewest (notebook 06).")


# ============================================================================
# SECTION 7 — Methodology & Notes
# ============================================================================
elif page == PAGES[6]:
    st.title("📝 Methodology & Data Notes")

    st.markdown(
        """
### Pipeline
Raw e-commerce events are processed by a reproducible PySpark notebook pipeline:

`01 Exploration → 02 Cleaning → 03 Customer Analytics → 04 Enhanced RFM → 05 Segmentation → 06 Product & Sales`

### Enhanced RFM features (notebook 04)
Traditional RFM extended to **seven** customer-level features used for clustering:

1. Recency  2. Frequency  3. Monetary  4. Average Transaction Value (ATV)
5. Average Purchase Events per Session  6. Amount Slope  7. Frequency Slope

Slope features were signed-log transformed, non-negative features used `log1p`, and all
features were standardised (Spark `StandardScaler`) before K-Means.

### Model selection (notebooks 04–05)
K was chosen from this dataset's own **Elbow (WSSSE)** and **Silhouette** metrics on a
reproducible 10% sample (34,603 customers). The evaluation supported **K = 6**, and the final
model was trained on all 347,118 purchasing customers.

### Cleaning decisions (notebook 02)
- Removed 2 records with missing `user_session`.
- Removed 68,673 records with non-positive `price` (no purchase events affected).
- Filled missing `category_code` and `brand` with `"unknown"`.
- Retained only `view`, `cart`, `purchase` event types.
- Retained repeated purchase groups (no transaction ID to confirm duplicates).

Final cleaned dataset: **42,380,089 records** (≈99.84% of the raw data).

### Important limitations
- The data is **event-level**, not order-level.
- There is **no explicit order/transaction ID** and **no quantity field**.
- `user_session` is a **session proxy**, not a formal order identifier.
- "Basket size" is approximated by average purchase events per session.
- There is **no country/location** attribute, so country analysis is omitted.
- Only **October 2019** is covered.
- Cluster IDs are algorithm-generated and do not imply business value on their own.
        """
    )

    st.divider()
    st.subheader("Reproducing the outputs")
    st.code(
        """# 1) install dependencies
pip install -r requirements.txt

# 2) place the October 2019 dataset at:
#    data/2019-Oct.csv

# 3) run notebooks 01 -> 06 in Jupyter (they write data/*.parquet and outputs/**)

# 4) launch this dashboard
streamlit run main.py""",
        language="bash",
    )
    st.info(
        "The dashboard auto-detects the notebook outputs at the paths listed at the top of "
        "`main.py`. When a file is missing it uses embedded demo data, so the UI always renders.",
        icon="💡",
    )


# ============================================================================
# Footer
# ============================================================================
st.sidebar.divider()
st.sidebar.caption(
    "E-Commerce Customer Behavior Analytics · Big Data Analytics Mini Project\n\n"
    "Team: Vaishnavi Poojary · Smith"
)
