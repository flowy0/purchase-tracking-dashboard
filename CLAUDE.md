# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a purchase tracker application that manages and processes purchase data from Taobao orders. The application will feature a database backend and web dashboard for visualizing and managing purchase data, with initial data imported from CSV files.

## Data Structure

The application processes CSV files in the `data/` folder with the following structure:
- `SN`: Serial number
- `date`: Order date
- `tracking_number`: Tracking number
- `companyName`: Company name
- `itemName`: Product name/description
- `quantity`: Item quantity (appears twice in format)
- `itemPrice`: Item price
- `exportStatus`: Export status
- `orderId`: Unique order identifier

Data files are located in:
- `data/taobao-en-all.csv` - Contains English product descriptions and purchase data

## Planned Technology Stack

**Backend:**
- **Database:** DuckDB (for analytics and CSV processing)
- **Web Framework:** FastAPI (for API endpoints and async support)
- **Database Interface:** Direct DuckDB Python API (optimized for analytics)
- **Data Processing:** Polars + DuckDB (for CSV import and data manipulation)

**Frontend:**
- **Dashboard Framework:** Streamlit (for rapid prototyping) or React (for more complex UI)
- **Visualization:** Plotly or Chart.js (for purchase analytics and charts)

**Development Tools:**
- **Package Management:** uv (modern Python package management)
- **Code Quality:** ruff (linting and formatting)
- **Testing:** pytest

## Development Commands

```bash
# Install dependencies with uv
uv sync

# Run the application
python main.py

# Initialize DuckDB database
python main.py init

# Start the web dashboard
python main.py dashboard

# Start API server
python main.py api

# Import CSV data
python main.py import data/taobao-en-all.csv

# Direct script usage
python scripts/init_db.py
python scripts/import_csv.py <csv_file>

# Run tests
pytest

# Code formatting and linting
ruff check .
ruff format .
```

## Architecture

**Current State:**
- `main.py` - Entry point with basic hello world functionality
- CSV data processing capabilities (inferred from data files)
- Focus on processing English Taobao order data from the data folder

**Planned Architecture:**
- `main.py` - Application entry point
- `app/` - Main application package
  - `models/` - Database schema and queries (DuckDB)
  - `api/` - FastAPI routes and endpoints
  - `services/` - Business logic and data processing
  - `database.py` - DuckDB configuration and connection
- `scripts/` - Utility scripts for data import and management
- `dashboard.py` - Streamlit dashboard application
- `tests/` - Test suite
- `purchase_tracker.db` - DuckDB database file

**Key Features to Implement:**
- CSV data import functionality
- Database schema for purchase tracking
- Web dashboard for data visualization
- Purchase analytics and reporting
- Search and filtering capabilities
- Export functionality