# E-Commerce Customer Behavior Analytics

Big Data Analytics project using **PySpark** for e-commerce customer behavior analysis, enhanced RFM feature engineering, and **K-Means customer segmentation**.

## Project Overview

This project analyzes large-scale e-commerce behavior data to understand how customers interact with products and to identify meaningful customer segments.

### Planned pipeline

```text
Raw E-Commerce Events
        ↓
PySpark Ingestion
        ↓
Data Cleaning & Transformation
        ↓
Customer / Product / Sales Analytics
        ↓
Purchase Data
        ↓
RFM & Enhanced Customer Features
        ↓
Feature Scaling
        ↓
K-Means Clustering
        ↓
Elbow + Silhouette Evaluation
        ↓
PCA Visualization
        ↓
Customer Segmentation
        ↓
Streamlit Dashboard
```

## Technology Stack

- Python
- Apache Spark / PySpark
- Spark MLlib
- Pandas
- Plotly / Matplotlib
- Streamlit
- Git & GitHub

## Dataset

The project uses the **E-Commerce Behavior Data from a Multi-Category Store** dataset from Kaggle.

The raw dataset is very large, so raw CSV files are **not stored in this repository**.

Dataset source:  
https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store

## Project Structure

```text
ecommerce-customer-behavior-analytics/
│
├── data/
│   └── README.md
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── src/
├── dashboard/
├── outputs/
│   ├── figures/
│   └── tables/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Team

**Vaishnavi Poojary**  
**Smith**

## Status

🚧 Project setup and dataset exploration in progress.
