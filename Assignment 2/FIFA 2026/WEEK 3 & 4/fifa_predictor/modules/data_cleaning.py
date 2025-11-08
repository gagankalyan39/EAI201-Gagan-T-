# modules/data_cleaning.py
from pathlib import Path
import pandas as pd

def load_and_clean_data(data_dir: Path):
    """Load CSV files and perform simple cleaning."""
    rank_df = pd.read_csv(data_dir / "fifa_ranking.csv")
    matches_df = pd.read_csv(data_dir / "Fifa_world_cup_matches.csv")
    players_df = pd.read_csv(data_dir / "fifaplayers.csv")
    results_df = pd.read_csv(data_dir / "results.csv")

    # normalize column names
    for df in (rank_df, matches_df, players_df, results_df):
        df.columns = [c.strip().replace("\n"," ").replace(" ","_") for c in df.columns]
        df.drop_duplicates(inplace=True)

    # numeric conversions
    if "age" in players_df.columns:
        players_df["age"] = pd.to_numeric(players_df["age"], errors="coerce")
        players_df["age"] = players_df["age"].fillna(players_df["age"].median())

    for c in ("home_score","away_score"):
        if c in results_df.columns:
            results_df[c] = pd.to_numeric(results_df[c], errors="coerce")
    # drop scoreless rows
    if "home_score" in results_df.columns and "away_score" in results_df.columns:
        results_df = results_df.dropna(subset=["home_score","away_score"])

    # ensure team name columns exist consistently
    # expected names: home_team, away_team in results_df
    # if not present, try to adapt (not exhaustive)
    if "home_team" not in results_df.columns and "HomeTeam" in results_df.columns:
        results_df = results_df.rename(columns={"HomeTeam":"home_team","AwayTeam":"away_team","FTHG":"home_score","FTAG":"away_score"})

    return rank_df, matches_df, players_df, results_df
