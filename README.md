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
