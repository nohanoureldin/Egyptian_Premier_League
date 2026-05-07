import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import os
import numpy as np

# ─────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────

conn = snowflake.connector.connect(
    account   = "uf04855.eu-central-2.aws",
    user      = "NOHANOURELDEAN",
    password  = "NRNYSs@#$2003s",
    warehouse = "EGYPTIAN_WH",
    database  = "EGYPTIAN_LEAGUE",
    schema    = "WAREHOUSE",
    role      = "SYSADMIN"
)

cur = conn.cursor()
print("Connected to Snowflake")

# ─────────────────────────────────────────
# FILE PATHS
# ─────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))

results  = pd.read_csv(os.path.join(BASE, "results_cleaned_final.csv"))
goals    = pd.read_csv(os.path.join(BASE, "goals_cleaned_final.csv"))
ref_stad = pd.read_csv(os.path.join(BASE, "referee_stadium_final.csv"))

print(f"Loaded: results({len(results)}), goals({len(goals)}), ref_stad({len(ref_stad)})")

# ─────────────────────────────────────────
# DATA CLEANING & DERIVATION
# ─────────────────────────────────────────

# Fix date format and ensure it's datetime
results["match_date"] = pd.to_datetime(results["match_date"], format="%m/%d/%Y")
results["season_start_year"] = results["Season"].str[:4].astype(int)

# ─────────────────────────────────────────
# DIM_TEAM
# ─────────────────────────────────────────

all_teams = pd.Series(
    pd.concat([results["home_team"], results["away_team"]]).unique()
).sort_values().reset_index(drop=True)

dim_team = pd.DataFrame({
    "TEAM_ID":   range(1, len(all_teams) + 1),
    "TEAM_NAME": all_teams
})

# ─────────────────────────────────────────
# DIM_SEASON (Normalized: Contains IS_COMPLETE)
# ─────────────────────────────────────────

dim_season = results[["Season","season_start_year","is_season_complete"]].drop_duplicates(subset="Season").copy()
dim_season = dim_season.sort_values("season_start_year").reset_index(drop=True)
dim_season.insert(0, "SEASON_ID", range(1, len(dim_season) + 1))
dim_season.columns = ["SEASON_ID","SEASON","SEASON_START_YEAR","IS_COMPLETE"]

# ─────────────────────────────────────────
# DIM_DATE
# ─────────────────────────────────────────

dim_date = results[["match_date"]].drop_duplicates().copy()
dim_date["match_year"]    = dim_date["match_date"].dt.year
dim_date["match_month"]   = dim_date["match_date"].dt.month
dim_date["month_name"]    = dim_date["match_date"].dt.month_name()
dim_date["match_quarter"] = dim_date["match_date"].dt.quarter
dim_date["match_weekday"] = dim_date["match_date"].dt.day_name()

dim_date = dim_date.sort_values("match_date").reset_index(drop=True)
dim_date.insert(0, "DATE_ID", range(1, len(dim_date) + 1))
dim_date.columns = ["DATE_ID","MATCH_DATE","MATCH_YEAR","MATCH_MONTH",
                    "MONTH_NAME","QUARTER","WEEKDAY"]
dim_date["MATCH_DATE"] = dim_date["MATCH_DATE"].dt.strftime("%Y-%m-%d")

# ─────────────────────────────────────────
# DIM_REFEREE (Clean - Static counts removed)
# ─────────────────────────────────────────

dim_referee = ref_stad[["Referee"]].drop_duplicates().sort_values("Referee").reset_index(drop=True)
dim_referee.insert(0, "REFEREE_ID", range(1, len(dim_referee) + 1))
dim_referee.columns = ["REFEREE_ID","REFEREE_NAME"]

# ─────────────────────────────────────────
# DIM_STADIUM (Clean - Static counts removed)
# ─────────────────────────────────────────

dim_stadium = ref_stad[["Stadium"]].drop_duplicates().sort_values("Stadium").reset_index(drop=True)
dim_stadium.insert(0, "STADIUM_ID", range(1, len(dim_stadium) + 1))
dim_stadium.columns = ["STADIUM_ID","STADIUM_NAME"]

# ─────────────────────────────────────────
# PREPARE FACT_MATCHES
# ─────────────────────────────────────────

fact = results.copy()

# Join IDs
fact = fact.merge(dim_season[["SEASON_ID","SEASON"]], left_on="Season", right_on="SEASON", how="left")
fact = fact.merge(dim_date[["DATE_ID","MATCH_DATE"]], 
                 left_on=fact["match_date"].dt.strftime("%Y-%m-%d"), 
                 right_on="MATCH_DATE", how="left")
fact = fact.merge(dim_team.rename(columns={"TEAM_ID":"HOME_TEAM_ID","TEAM_NAME":"ht"}), left_on="home_team", right_on="ht", how="left")
fact = fact.merge(dim_team.rename(columns={"TEAM_ID":"AWAY_TEAM_ID","TEAM_NAME":"at"}), left_on="away_team", right_on="at", how="left")

match_ref_stad = ref_stad.merge(dim_referee, left_on="Referee", right_on="REFEREE_NAME", how="left") \
                         .merge(dim_stadium, left_on="Stadium", right_on="STADIUM_NAME", how="left")
fact = fact.merge(match_ref_stad[["match_id","REFEREE_ID","STADIUM_ID"]], on="match_id", how="left")

# FACT_MATCHES Selection (Redundant IS_SEASON_COMPLETE removed)
fact_matches = fact[[
    "match_id","SEASON_ID","DATE_ID","HOME_TEAM_ID","AWAY_TEAM_ID",
    "REFEREE_ID","STADIUM_ID","gameweek","home_goals","away_goals",
    "goal_diff","total_goals","match_status","is_derby"
]].copy()

fact_matches.columns = [
    "MATCH_ID","SEASON_ID","DATE_ID","HOME_TEAM_ID","AWAY_TEAM_ID",
    "REFEREE_ID","STADIUM_ID","GAMEWEEK","HOME_GOALS","AWAY_GOALS",
    "GOAL_DIFF","TOTAL_GOALS","MATCH_STATUS","IS_DERBY"
]

# ─────────────────────────────────────────
# FACT_TEAM_RESULTS (Professional Team-Match Grain)
# ─────────────────────────────────────────

home_perf = fact_matches.copy()
home_perf["TEAM_ID"]     = home_perf["HOME_TEAM_ID"]
home_perf["OPPONENT_ID"] = home_perf["AWAY_TEAM_ID"]
home_perf["GOALS_FOR"]   = home_perf["HOME_GOALS"]
home_perf["GOALS_AGAINST"] = home_perf["AWAY_GOALS"]
home_perf["IS_HOME"]     = True

away_perf = fact_matches.copy()
away_perf["TEAM_ID"]     = away_perf["AWAY_TEAM_ID"]
away_perf["OPPONENT_ID"] = away_perf["HOME_TEAM_ID"]
away_perf["GOALS_FOR"]   = away_perf["AWAY_GOALS"]
away_perf["GOALS_AGAINST"] = away_perf["HOME_GOALS"]
away_perf["IS_HOME"]     = False

fact_team_results = pd.concat([home_perf, away_perf], ignore_index=True)

def get_pts(row):
    if row["GOALS_FOR"] > row["GOALS_AGAINST"]: return 3
    if row["GOALS_FOR"] == row["GOALS_AGAINST"]: return 1
    return 0

fact_team_results["POINTS"] = fact_team_results.apply(get_pts, axis=1)
fact_team_results["RESULT"] = np.where(fact_team_results["POINTS"]==3, "W", 
                              np.where(fact_team_results["POINTS"]==1, "D", "L"))

fact_team_results = fact_team_results[[
    "MATCH_ID","TEAM_ID","OPPONENT_ID","SEASON_ID","DATE_ID",
    "GOALS_FOR","GOALS_AGAINST","POINTS","RESULT","IS_HOME","IS_DERBY"
]]

# ─────────────────────────────────────────
# FACT_GOALS
# ─────────────────────────────────────────

fact_goals = goals.merge(dim_team, left_on="TeamScored", right_on="TEAM_NAME", how="left")[[
    "goal_id","match_id","TEAM_ID","GoalScorer",
    "Assist","AssistType","OG","Penalty","is_assisted","goal_type"
]].copy()

fact_goals.columns = [
    "GOAL_ID","MATCH_ID","TEAM_ID","GOAL_SCORER",
    "ASSIST","ASSIST_TYPE","IS_OG","IS_PENALTY","IS_ASSISTED","GOAL_TYPE"
]

# ─────────────────────────────────────────
# LOAD TO SNOWFLAKE
# ─────────────────────────────────────────

def load_table(df, table_name):
    print(f"Loading {table_name} ({len(df)} rows)...")
    write_pandas(conn, df, table_name, database="EGYPTIAN_LEAGUE", schema="WAREHOUSE", overwrite=True)

load_table(dim_team,         "DIM_TEAM")
load_table(dim_season,       "DIM_SEASON")
load_table(dim_date,         "DIM_DATE")
load_table(dim_referee,      "DIM_REFEREE")
load_table(dim_stadium,      "DIM_STADIUM")
load_table(fact_matches,     "FACT_MATCHES")
load_table(fact_team_results,"FACT_TEAM_RESULTS")
load_table(fact_goals,       "FACT_GOALS")

cur.close()
conn.close()
print("\n[SUCCESS] Egyptian League Professional Star Schema loaded to Snowflake.")
