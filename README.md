# E-commerce-Analytics-Pipeline

A complete pipeline for managing, analyzing, and visualizing e-commerce sales data from Amazon and Flipkart using Python, PostgreSQL, Metabase, and Docker. This project demonstrates an ETL (Extract, Transform, Load) process, data transformation using SQL, and creating interactive dashboards for business insights.

# Project Overview

This project streamlines the process of analyzing sales data by integrating data from multiple e-commerce platforms into a unified PostgreSQL database. It enables automated data cleaning, transformation, and visualization for actionable business insights.

### Key Features:
- **Automated ETL Process:** Upload and process Amazon and Flipkart sales data using Python.
- **Unified Data View:** Standardize and combine data from multiple platforms using advanced SQL queries.
- **Interactive Dashboards:** Visualize key metrics, trends, and KPIs in Metabase.
- **Technologies Used:** Python, PostgreSQL, Metabase, and Docker.

# Folder Structure

```plaintext
E-commerce-Analytics-Pipeline/
│
├── data/                   # Contains sample datasets for demonstration
│   ├── sample_amazon.csv
│   ├── sample_flipkart.xlsx
│
├── dashboards/             # Contains dashboard screenshots and configurations
│   ├── dashboard_screenshot.png
│
├── scripts/                # Python scripts for data processing
│   ├── upload_to_postgres.py
│
├── sql_queries/            # SQL queries for data transformation
│   ├── combined_data_query.sql
│
├── .gitignore              # Git ignore file
├── LICENSE                 # License for the repository
├── README.md               # Project documentation


## Workflow

### 1. Data Upload and Processing
**Input Data:** Sales data from Amazon and Flipkart in `.csv` or `.xlsx` formats.

**ETL Process:**
- The `upload_to_postgres.py` script automates:
  - Uploading sales data to PostgreSQL.
  - Deduplication of records using a hash-based `unique_id`.
  - Dynamic creation or updating of tables in PostgreSQL.

---

### 2. Data Transformation
- The SQL query in `combined_data_query.sql` performs:
  - Combining Amazon and Flipkart sales data into a single unified dataset.
  - Standardizing columns like `brand`, `SKU`, and `GMV`.
  - Enriching data by joining with additional pricing and product tables.

---

### 3. Data Visualization
**Metabase Dashboards:**
- Provides actionable insights on sales performance, brand contributions, and top-performing SKUs.
- Enables dynamic filtering by date, platform, and fulfillment channels.

---

## How to Use

### Prerequisites
1. Install **Docker** and **PostgreSQL** on your machine.
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/E-commerce-Analytics-Pipeline.git
   cd E-commerce-Analytics-Pipeline
