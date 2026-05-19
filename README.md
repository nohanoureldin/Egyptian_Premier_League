# Egyptian Premier League Analytics
## 10 Seasons of Football Match Data (2015–2025)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Snowflake-Cloud_Data_Warehouse-29B5E8?style=for-the-badge&logo=snowflake&logoColor=white" />
  <img src="https://img.shields.io/badge/Power_BI-Data_Visualization-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" />
  <img src="https://img.shields.io/badge/pandas-Data_Processing-150458?style=for-the-badge&logo=pandas&logoColor=white" />
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [What This Project Does](#what-this-project-does)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Medallion Architecture](#medallion-architecture)
- [Dimensional Data Model](#dimensional-data-model)
- [Data Sources](#data-sources)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Data Pipeline Execution Flow](#data-pipeline-execution-flow)
- [Key Data Sources](#key-data-sources)
- [Data Quality](#data-quality)
- [Performance & Scalability](#performance--scalability)
- [Troubleshooting](#troubleshooting)
- [Team](#team)
- [Roadmap](#roadmap)

---

## Overview

**Egyptian Premier League Analytics** is a comprehensive data engineering solution that collects, transforms, and analyzes football match data from Egypt's top-tier league across 10 seasons. It aggregates match results, goal details, player statistics, and referee/stadium information to provide actionable insights for football analytics.

The pipeline processes raw CSV data from Kaggle and builds a modern data warehouse using Python for transformation, Snowflake for storage, and Power BI for visualization.

---

## What This Project Does

This project automates the complete lifecycle of Egyptian football data:

### Data Collection
- **Match Results Data**: Reads 10 season CSV files using pandas and glob
- **Goal Details**: Extracts per-goal information including scorers, assists, and goal types
- **Referee & Stadium Data**: Gathers match official and venue information
- **Dimension Tables**: Automatically generates reference data for teams, seasons, dates, referees, and stadiums

### Data Transformation
- Cleans and standardizes raw data into production-ready analytics tables
- Creates reusable dimensional and fact tables following the **medallion architecture pattern**
- Implements data quality checks and validation
- Generates surrogate keys for dimension tables

### Data Delivery
- Publishes analytics-ready tables for business intelligence tools (Power BI)
- Enables interactive dashboards and ad-hoc queries via DirectQuery

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Extract** | Python (pandas, glob) | Read and combine multiple CSV files |
| **Transform** | Python (pandas) | Data cleaning, validation, derived columns |
| **Load** | snowflake-connector-python, write_pandas | Bulk upload to cloud warehouse |
| **Data Warehouse** | Snowflake | Centralized cloud data storage |
| **Orchestration** | Python scripts | Sequential ETL execution |
| **Language** | Python 3.13+ | Scripting and data processing |
| **Dashboarding** | Power BI Desktop | Business intelligence visualizations |

---

## Architecture

### Data Flow Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   DATA SOURCE   │────▶│    EXTRACT      │────▶│   TRANSFORM     │────▶│    STAGING      │
│                 │     │                 │     │                 │     │                 │
│  Kaggle CSVs    │     │  Python         │     │  Python         │     │  Local CSV      │
│  (3 files)      │     │  (pandas, glob) │     │  (pandas)       │     │  Files          │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                                                │
                                                                                ▼
┌─────────────────┐     ┌─────────────────────────────────────────┐     ┌─────────────────┐
│ VISUALIZATION   │◀────│         DATA WAREHOUSE (SNOWFLAKE)     │◀────│      LOAD       │
│                 │     │                                         │     │                 │
│  Power BI       │     │  ┌─────────┐  ┌─────────┐  ┌─────────┐│     │  Python         │
│  Desktop        │     │  │  Bronze │──▶│ Silver  │──▶│  Gold   ││     │  (snowflake-   │
│  (DirectQuery)  │     │  │  (Raw)  │  │ (Clean) │  │(Business││     │  connector)     │
│                 │     │  └─────────┘  └─────────┘  │  Ready) ││     │                 │
└─────────────────┘     │                          └─────────┘│     └─────────────────┘
                          │                                         │
                          │  Star Schema                            │
                          │  • 1 Fact Table + 5 Dimension Tables    │
                          └─────────────────────────────────────────┘
```

### Pipeline Steps

| Step | Stage | Tool | What Happens |
|------|-------|------|--------------|
| 1 | **Data Source** | Kaggle CSVs | 3 raw CSV files with match, goal, and referee data |
| 2 | **Extract** | Python + pandas + glob | Read and combine 10 season files into unified DataFrames |
| 3 | **Transform** | Python + pandas | Clean, validate, derive columns, generate surrogate keys |
| 4 | **Staging** | Local CSV files | Save clean transformed data as intermediate checkpoint |
| 5 | **Load** | snowflake-connector-python | Bulk upload to Snowflake cloud warehouse |
| 6 | **Data Warehouse** | Snowflake | Medallion Architecture: Bronze → Silver → Gold |
| 7 | **Visualization** | Power BI Desktop | 4-page interactive dashboard with DirectQuery |

---

## Medallion Architecture

The project follows the **medallion (bronze-silver-gold)** data architecture pattern within Snowflake:

### 🥉 Bronze Layer (`RAW`)
Raw data ingested from source systems with minimal transformations.
- `raw_results` — Match results exactly as loaded from CSV
- `raw_goals` — Goal details exactly as loaded from CSV
- `raw_referee_stadium` — Referee and stadium data exactly as loaded

**Characteristics:**
- Data types preserved as VARCHAR for safe loading
- No business logic applied
- Audit trail maintained
- Source of truth for reprocessing

### 🥈 Silver Layer (`SILVER`)
Business logic applied, data cleaned, normalized, and enriched.
- `silver_results` — Standardized match results with proper data types
- `silver_goals` — Cleaned goal data with derived columns
- `silver_referee_stadium` — Normalized referee and stadium data

**Transformations Applied:**
- Date parsing: `match_date` converted from VARCHAR to DATE
- Data validation: Goals consistency checks, status validation
- Derived columns: `goal_diff`, `total_goals`, `is_derby`, `goal_type`
- Column renaming: Standardized to snake_case
- Data type normalization: Proper INTEGER, BOOLEAN, VARCHAR types

### 🥇 Gold Layer (`WAREHOUSE` / Analytics-Ready)
Analytics-ready dimensional and fact tables for BI tools and reporting.

**Dimensions (Reference Tables):**
- `dim_team` — Team master dimension (35 teams)
- `dim_season` — Season dimension (10 seasons)
- `dim_date` — Date dimension for time-based analysis (1,303 dates)
- `dim_referee` — Referee dimension (138 referees)
- `dim_stadium` — Stadium dimension (27 stadiums)

**Facts (Event/Measure Tables):**
- `fact_matches` — Match-level facts (2,907 rows): scores, status, derby flags, goal aggregations

**Schema Type: Star Schema**
- One central fact table surrounded by dimension tables
- All dimensions connect directly to the fact table
- Optimized for query performance and simplicity

---

## Dimensional Data Model

### Star Schema Diagram

```
                         dim_date (1,303)
                              │
                              │
    dim_team (35) ────────────┼─────────── fact_matches (2,907)
                              │                │
                              │                │
                              │                │
                         dim_season (10)      dim_referee (138)
                              │                │
                              │                │
                              │                │
                         dim_stadium (27)
```

### Key Dimensions

| Dimension | Purpose | Key Attributes | Rows |
|-----------|---------|----------------|------|
| **dim_team** | Team reference | team_sk (surrogate), team_name | 35 |
| **dim_season** | Season reference | season_key, start_year, is_complete | 10 |
| **dim_date** | Time reference | date_key, year, quarter, month, day | 1,303 |
| **dim_referee** | Referee reference | referee_id, referee_name, match_count | 138 |
| **dim_stadium** | Stadium reference | stadium_id, stadium_name, match_count | 27 |

### Key Facts

| Fact Table | Grain | Key Measures | Rows |
|-----------|-------|--------------|------|
| **fact_matches** | One row per match | home_goals, away_goals, total_goals, goal_diff, match_status, is_derby | 2,907 |

### Role-Playing Dimension
- `dim_team` is referenced **twice** in `fact_matches`:
  - `home_team_sk` → dim_team (active relationship)
  - `away_team_sk` → dim_team (inactive, handled via DAX)

### Goal Data Handling
- Goal-level details (6,635 goals) are **aggregated within the fact table** via:
  - `total_goals` — sum of home + away goals per match
  - `home_goals` — goals scored by home team
  - `away_goals` — goals scored by away team
- Player-level goal analysis (top scorers, assisters) is handled in Power BI via DAX measures querying the goals CSV directly or through calculated tables

---

## Data Sources

### Primary Source
**Kaggle — 10 Seasons Egyptian League**
- URL: https://www.kaggle.com/datasets/ahmedaelgohary/10-seasons-egyptian-league
- Coverage: 10 seasons (2015–2016 to 2024–2025)
- Total Records: 12,449 rows across 3 files

### Source Files

#### `results_cleaned_final.csv` — Match Results
| Column | Type | Description |
|--------|------|-------------|
| `match_id` | Integer | Natural key (e.g., 2015000 = season 2015, match 000) |
| `Season` | String | Season label (e.g., "2015-2016") |
| `match_date` | Date | Match date (YYYY-MM-DD) |
| `match_month_name` | String | Month name for filtering |
| `gameweek` | Integer | Week number in season |
| `home_team` | String | Home team name |
| `away_team` | String | Away team name |
| `home_goals` | Integer | Goals scored by home team |
| `away_goals` | Integer | Goals scored by away team |
| `goal_diff` | Integer | Derived: home_goals - away_goals |
| `total_goals` | Integer | Derived: home_goals + away_goals |
| `match_status` | String | "HomeWin", "AwayWin", or "Tie" |
| `is_derby` | Boolean | TRUE for Ahly SC vs Zamalek matches |
| `is_season_complete` | Boolean | Season completion flag |

**Rows**: 2,907 (one per match)

#### `goals_cleaned.csv` — Goal Details
| Column | Type | Description |
|--------|------|-------------|
| `goal_id` | Integer | Natural key |
| `match_id` | Integer | Foreign key to results |
| `Season` | String | Season label |
| `GoalScorer` | String | Player who scored |
| `Assist` | String | Assisting player (NULL if unassisted) |
| `TeamScored` | String | Team that scored |
| `TeamConceded` | String | Team that conceded |
| `OG` | Boolean | Own goal flag |
| `Penalty` | Boolean | Penalty flag |
| `is_assisted` | Boolean | TRUE if Assist is not NULL |
| `goal_type` | String | Derived: "Open Play", "Penalty", "Own Goal" |
| `AssistType` | String | Type of assist: Pass, Cross, Header, Free kick |
| `minute` | Integer | Minute goal was scored |

**Rows**: 6,635 (one per goal)
- **Note**: Goal data is used for Power BI calculated tables and DAX measures, not as a separate fact table in the Star Schema

#### `referee_stadium_final.csv` — Match Officials & Venues
| Column | Type | Description |
|--------|------|-------------|
| `match_id` | Integer | Foreign key to results |
| `Season` | String | Season label |
| `Referee` | String | Match referee name |
| `Stadium` | String | Stadium name |
| `RefereeMatchCount` | Integer | Derived: total matches by this referee |
| `StadiumMatchCount` | Integer | Derived: total matches at this stadium |

**Rows**: 2,907 (one per match)

---

## Project Structure

```
Egyptian-Premier-League-Analytics/
│
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── 📂 data/
│   ├── 📂 raw/                        # Original Kaggle CSVs
│   │   ├── results_2015_2016.csv
│   │   ├── results_2016_2017.csv
│   │   ├── ... (10 season files)
│   │   ├── goals.csv
│   │   └── referee_stadium.csv
│   │
│   └── 📂 cleaned/                    # Cleaned output files (Silver layer)
│       ├── results_cleaned_final.csv
│       ├── goals_cleaned.csv
│       └── referee_stadium_final.csv
│
├── 📂 etl/                            # ETL Pipeline scripts
│   ├── extract.py                     # Read & combine CSVs (Extract)
│   ├── transform.py                   # Clean, validate, derive (Transform)
│   ├── load.py                        # Snowflake bulk load (Load)
│   └── config.py                      # Snowflake credentials & config
│
├── 📂 snowflake/                      # Snowflake DDL & DML
│   ├── 📂 ddl/
│   │   ├── 01_create_database.sql     # Create database & schemas
│   │   ├── 02_create_bronze.sql       # Bronze layer tables (RAW)
│   │   ├── 03_create_silver.sql      # Silver layer tables (Cleaned)
│   │   └── 04_create_gold.sql        # Gold layer tables (Dimensions + Facts)
│   └── 📂 dml/
│       ├── 01_load_bronze.sql         # Load raw data
│       ├── 02_transform_silver.sql     # Silver transformations
│       └── 03_verify_loads.sql       # Data validation queries
│
├── 📂 powerbi/                        # Power BI artifacts
│   ├── egyptian_league_dashboard.pbix # Main dashboard file
│   └── 📂 screenshots/                # Dashboard page images
│       ├── page1_season_overview.png
│       ├── page2_team_performance.png
│       ├── page3_goals_analysis.png
│       └── page4_stadiums_referees.png
│
├── 📂 docs/
│   ├── architecture_diagram.png       # 7-step pipeline diagram
│   ├── medallion_architecture.png     # Bronze-Silver-Gold layers
│   ├── star_schema_diagram.drawio     # Star Schema diagram
│   └── data_dictionary.md             # Full column documentation
│
└── 📂 notebooks/                      # Jupyter notebooks for EDA
    └── exploratory_analysis.ipynb
```

---

## Getting Started

### Prerequisites

- Python 3.13 or higher
- Snowflake account (free trial available)
- Power BI Desktop
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Egyptian-Premier-League-Analytics.git
   cd Egyptian-Premier-League-Analytics
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scriptsctivate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Snowflake connection:**
   Edit `etl/config.py` with your Snowflake credentials:
   ```python
   SNOWFLAKE_CONFIG = {
       "account": "your_account",
       "user": "your_user",
       "password": "your_password",
       "warehouse": "EGYPTIAN_WH",
       "database": "EGYPTIAN_LEAGUE",
       "schema": "WAREHOUSE",
       "role": "SYSADMIN"
   }
   ```

### Running the Pipeline

#### Option 1: Run Full ETL Pipeline
```bash
cd etl
python extract.py      # Step 1: Extract from Kaggle CSVs
python transform.py    # Step 2: Clean and transform
python load.py         # Step 3: Load to Snowflake
```

#### Option 2: Run Individual Steps
```bash
# Extract only
python etl/extract.py

# Transform only (requires extracted data)
python etl/transform.py

# Load only (requires transformed data in staging)
python etl/load.py
```

#### Option 3: Run with Snowflake SQL
```sql
-- Create database and schemas
USE ROLE SYSADMIN;
CREATE DATABASE EGYPTIAN_LEAGUE_DW;
CREATE SCHEMA RAW;
CREATE SCHEMA SILVER;
CREATE SCHEMA WAREHOUSE;

-- Load Bronze layer
COPY INTO RAW.RESULTS FROM @my_stage/results_cleaned_final.csv;
COPY INTO RAW.GOALS FROM @my_stage/goals_cleaned.csv;
COPY INTO RAW.REFEREE_STADIUM FROM @my_stage/referee_stadium_final.csv;

-- Transform to Silver
CREATE TABLE SILVER.RESULTS AS SELECT * FROM RAW.RESULTS;
-- (apply transformations)

-- Build Gold layer (dimensions and facts)
CREATE TABLE WAREHOUSE.DIM_TEAM AS ...;
CREATE TABLE WAREHOUSE.FACT_MATCHES AS ...;
```

### Open Power BI Dashboard

1. Open `powerbi/egyptian_league_dashboard.pbix`
2. Refresh the data connection to your Snowflake instance
3. Explore the 4 dashboard pages

---

## Data Pipeline Execution Flow

```
Sequence:
1. Kaggle CSVs → Python Extract (pandas, glob)
2. Raw DataFrames → Python Transform (cleaning, validation, derivation)
3. Clean CSVs → Local Staging (intermediate checkpoint)
4. Staging CSVs → Snowflake Load (write_pandas bulk insert)
5. Bronze Tables (RAW) → Silver Tables (SILVER) → Gold Tables (WAREHOUSE)
6. Gold Tables → Power BI DirectQuery
7. Power BI → Interactive Dashboards & Reports
```

### Load Order (Critical for Referential Integrity)

```
Bronze Layer:
  1. raw_results
  2. raw_goals
  3. raw_referee_stadium

Silver Layer:
  4. silver_results (cleaned, typed)
  5. silver_goals (cleaned, typed)
  6. silver_referee_stadium (cleaned, typed)

Gold Layer — Dimensions First:
  7. dim_team
  8. dim_season
  9. dim_date
  10. dim_referee
  11. dim_stadium

Gold Layer — Fact Last:
  12. fact_matches (references all dimensions)
```

---

## Key Data Sources

### Kaggle — 10 Seasons Egyptian League
- **URL**: https://www.kaggle.com/datasets/ahmedaelgohary/10-seasons-egyptian-league
- **Data**: Match results, goal details, referee and stadium records
- **Update Frequency**: Static dataset (historical 10 seasons)
- **Format**: 3 CSV files

### Data Characteristics
- **Coverage**: 10 seasons (2015–2016 to 2024–2025)
- **Matches**: 2,907
- **Goals**: 6,635 (aggregated within fact_matches via total_goals, home_goals, away_goals)
- **Teams**: 35 unique teams
- **Referees**: 138 unique referees
- **Stadiums**: 27 unique stadiums
- **Derbies**: 19 (Ahly SC vs Zamalek)

---

## Data Quality

The project implements multiple data quality checks:

### Validation Checks

| Check | Result | Status |
|-------|--------|--------|
| match_id consistency across all 3 tables | All 2,907 match_ids present | ✅ Pass |
| Zero nulls in referee_stadium | 0 nulls | ✅ Pass |
| Zero nulls in results | 0 nulls | ✅ Pass |
| Assist nulls in goals | 1,666 nulls (expected — unassisted goals) | ✅ Pass |
| Season range | 2015-2016 to 2024-2025 (10 seasons) | ✅ Pass |
| Team count | 35 unique teams | ✅ Pass |
| Referee count | 138 unique referees | ✅ Pass |
| Stadium count | 27 unique stadiums | ✅ Pass |
| Derby matches | 19 (Ahly SC vs Zamalek) | ✅ Pass |
| Goals per match average | 2.28 | ✅ Pass |

### Data Quality Issues Identified
- **455 missing kickoff times**: Flagged with binary column during transformation
- **1,666 unassisted goals**: Expected NULLs in Assist column (is_assisted = False)
- **2022-2023 season**: Sharp drop in goals (likely COVID/incomplete season)
- **2024-2025 season**: Very low volume (season in progress at extraction time)

---

## Performance & Scalability

### ETL Performance
- **Extract**: ~2 minutes to read and combine all CSV files
- **Transform**: ~3 minutes for cleaning, validation, and derivation
- **Load**: ~5 minutes for bulk upload to Snowflake via write_pandas
- **Total pipeline time**: ~10 minutes for full historical data refresh

### Data Warehouse Performance
- **Snowflake warehouse size**: X-SMALL (cost-efficient for academic project)
- **Auto-suspend**: 60 seconds (saves free trial credits)
- **Auto-resume**: TRUE
- **Storage**: ~50MB for all tables

### Power BI Performance
- **Connection mode**: DirectQuery (queries Snowflake live)
- **Query response time**: <2 seconds per visual
- **Dashboard refresh**: On-demand (historical data, no real-time needed)

---

## Troubleshooting

### ETL Issues

**Problem**: "FileNotFoundError: No such file or directory"
- **Cause**: CSV files not in expected path
- **Solution**: Verify `BASE` path in `etl/config.py` matches your local file location

**Problem**: "MissingDependencyError: pandas"
- **Cause**: snowflake-connector-python pandas extras not installed
- **Solution**: Run `pip install "snowflake-connector-python[pandas]"`

**Problem**: "No active warehouse selected"
- **Cause**: Warehouse not specified or doesn't exist
- **Solution**: Verify `warehouse` in connection config; create warehouse if missing:
  ```sql
  CREATE WAREHOUSE IF NOT EXISTS EGYPTIAN_WH
      WAREHOUSE_SIZE = 'X-SMALL'
      AUTO_SUSPEND = 60
      AUTO_RESUME = TRUE;
  ```

### Snowflake Issues

**Problem**: "Object does not exist, or operation cannot be performed"
- **Cause**: Schema name mismatch
- **Solution**: Verify schema name in connection (WAREHOUSE vs ANALYTICS vs RAW)

**Problem**: "Incorrect username or password"
- **Cause**: Snowflake credentials incorrect
- **Solution**: Verify account identifier format (e.g., `uf04855.eu-central-2.aws`)

### Power BI Issues

**Problem**: "Ambiguous paths between tables"
- **Cause**: Multiple relationship paths between fact_matches and dim_team
- **Solution**: Keep only one active relationship (home_team_sk); handle away_team via DAX USERELATIONSHIP()

**Problem**: "FORMAT() measure breaks charts"
- **Cause**: FORMAT() returns text, not number
- **Solution**: Create separate measures — numeric for charts, formatted for cards

---

## Team

| Role | Member | Responsibility |
|------|--------|---------------|
| **Data Engineer** | [Name] | Python ETL pipeline: extract, transform, load |
| **DWH Architect** | [Name] | Snowflake schema design, medallion architecture, data validation |
| **BI Developer** | [Name] | Power BI model, DAX measures, dashboard design, visual polish |

**Institution**: Information Technology Institute (ITI) — Data Engineering Track

---

## Roadmap

- [ ] Add incremental season updates (append new season data)
- [ ] Implement player market value analysis
- [ ] Add predictive analytics (match outcome prediction)
- [ ] Optimize ETL with Apache Airflow orchestration
- [ ] Add data lineage documentation
- [ ] Expand dashboard with real-time match tracking
- [ ] Implement automated data quality monitoring
- [ ] Add anomaly detection for referee bias analysis

---

## Appendix: Visual Placeholders

### 1. Data Architecture Diagram
Shows: Data sources → Extract → Transform → Staging → Load → Bronze → Silver → Gold → Power BI

### 2. Medallion Architecture Diagram
Shows: Bronze (RAW) → Silver (Cleaned) → Gold (Dimensions + Facts)

### 3. Star Schema Diagram
Shows: fact_matches in center with dim_team, dim_season, dim_date, dim_referee, dim_stadium surrounding it

### 4. Pipeline Execution Flow
Shows: Sequential ETL steps with load order and dependencies

### 5. Sample Dashboard — Season Overview
Shows: KPI cards, goals per season bar chart, match results donut, season slicer

### 6. Sample Dashboard — Team Performance
Shows: Top 10 teams by goals, top 10 by wins, home vs away goals

### 7. Sample Dashboard — Goals Analysis
Shows: Top scorers, top assisters, goal type breakdown, assist type breakdown

### 8. Sample Dashboard — Stadiums & Referees
Shows: Top stadiums, top referees, venue distribution

---

<p align="center">
  <b>Built with 💚 for Egyptian Football</b><br>
  <sub>ITI Data Engineering Track · Graduation Project · 2026</sub>
</p>
