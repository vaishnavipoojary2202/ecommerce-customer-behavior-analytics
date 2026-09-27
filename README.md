# E-Commerce Customer Behavior Analytics

> **Big Data Analytics Mini Project**  
> Large-scale e-commerce behavior analysis using **Apache Spark / PySpark**, enhanced RFM-based customer segmentation, and an interactive dashboard.

## Overview

This project analyzes e-commerce event data to understand customer purchasing behavior, product performance, and sales patterns. Customer-level behavioral features are used to build an enhanced RFM representation and segment customers using **K-Means clustering**.

The project is designed as a reproducible PySpark pipeline rather than a single monolithic notebook.

## Project Pipeline

```text
Raw E-Commerce Events
        ↓
01 — Data Exploration
        ↓
02 — Data Cleaning
        ↓
03 — Customer Analytics
        ↓
04 — Enhanced RFM
        ↓
05 — Customer Segmentation
        ↓
06 — Product & Sales Analysis
        ↓
Streamlit Dashboard
```

## Repository Structure

```text
ecommerce-customer-behavior-analytics/
│
├── data/
│   └── README.md
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_customer_analytics.ipynb
│   ├── 04_enhanced_rfm.ipynb
│   ├── 05_customer_segmentation.ipynb
│   └── 06_product_sales_analysis.ipynb
│
├── dashboard/
│   └── app.py
│
├── outputs/
│   ├── figures/
│   └── tables/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Notebook Responsibilities

| Notebook | Purpose |
|---|---|
| `01_data_exploration` | Understand the raw dataset, schema, events, users, sessions, missing values and basic statistics |
| `02_data_cleaning` | Clean, validate and prepare reusable event/purchase data |
| `03_customer_analytics` | Build customer-level behavioral summaries |
| `04_enhanced_rfm` | Create RFM + enhanced customer features and prepare them for clustering |
| `05_customer_segmentation` | Evaluate K values and perform K-Means customer segmentation |
| `06_product_sales_analysis` | Analyze products, categories, brands and sales trends |

## Dataset

**E-Commerce Behavior Data from a Multi-Category Store**

The dataset contains event-level e-commerce interactions such as views, cart actions and purchases.

Source: [Kaggle dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store)

The raw CSV is intentionally **not stored in GitHub** because of its size. For the initial implementation, the working file is:

`2019-Oct.csv`

Place it locally at:

```text
data/2019-Oct.csv
```

## Technology Stack

- **Python**
- **Apache Spark / PySpark**
- **Spark MLlib**
- **Pandas / NumPy**
- **Matplotlib / Plotly**
- **Streamlit**
- **Jupyter**
- **Git & GitHub**

## Reproducibility

Large intermediate datasets should be stored locally as **Parquet** rather than repeatedly recomputing them from the raw CSV.

Raw data and generated large files are excluded through `.gitignore`.

## Team

- **Vaishnavi Poojary**
- **Smith**

## Project Status

🚧 **Project setup complete — implementation starting with Notebook 01.**
