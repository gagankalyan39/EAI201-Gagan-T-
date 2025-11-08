
import pandas as pd
import numpy as np

def build_team_features(rank_df, players_df, results_df, recent_n=5):
    """
    Build team-level features:
      - Latest_FIFA_Rank
      - Average_Age
      - Historical_Win_Draw_Rate
      - Historical_Avg_Goal_Difference
      - Recent_Win_Rate_{n}
      - Recent_Avg_Goal_Diff_{n}
      - Matches_Played (history)
    """
    # avg age
    team_col = next((c for c in ("team_name","team","country","national_team","country_full") if c in players_df.columns), None)
    if team_col is None:
        raise KeyError("No team column found in players file.")
    avg_age = players_df.groupby(team_col)["age"].mean().rename("Average_Age")

    # latest FIFA rank
    rank_col = "rank" if "rank" in rank_df.columns else next((c for c in rank_df.columns if "rank" in c.lower()), None)
    date_col = next((c for c in rank_df.columns if "date" in c.lower() or "rank_date" in c.lower()), None)
    country_col = next((c for c in ("country_full","country") if c in rank_df.columns), None)
    if rank_col and country_col:
        if date_col:
            rank_df[date_col] = pd.to_datetime(rank_df[date_col], errors="coerce")
            latest_rank = rank_df.sort_values(date_col).groupby(country_col).last()[rank_col].rename("Latest_FIFA_Rank")
        else:
            latest_rank = rank_df.groupby(country_col).last()[rank_col].rename("Latest_FIFA_Rank")
    else:
        latest_rank = pd.Series(dtype=float, name="Latest_FIFA_Rank")

    # historical stats
    results = results_df.copy()
    # ensure columns
    if "home_team" not in results.columns or "away_team" not in results.columns:
        raise KeyError("results.csv missing home_team/away_team columns")

    teams = pd.unique(results[["home_team","away_team"]].values.ravel('K'))
    rows = []
    for team in teams:
        home = results[results["home_team"] == team]
        away = results[results["away_team"] == team]
        played = len(home) + len(away)
        if played == 0:
            continue
        wins = (home["home_score"] > home["away_score"]).sum() + (away["away_score"] > away["home_score"]).sum()
        draws = (home["home_score"] == home["away_score"]).sum() + (away["home_score"] == away["away_score"]).sum()
        wdr = (wins + draws) / played
        gd = ((home["home_score"] - home["away_score"]).sum() + (away["away_score"] - away["home_score"]).sum()) / played
        rows.append((team, played, wdr, gd))
    stats = pd.DataFrame(rows, columns=["team","Matches_Played","Historical_Win_Draw_Rate","Historical_Avg_Goal_Difference"]).set_index("team")

    # recent form features: last recent_n matches per team
    def recent_stats(team, n=recent_n):
        # filter matches involving team, sort by assumed chronological order if date exists
        df = results[(results["home_team"]==team) | (results["away_team"]==team)].copy()
        # try to find date column
        date_cols = [c for c in df.columns if "date" in c.lower()]
        if date_cols:
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
            df = df.sort_values(date_cols[0], ascending=False)
        else:
            df = df.iloc[::-1]  # fallback
        df = df.head(n)
        if df.empty:
            return 0.0, 0.0
        wins = 0
        gd_sum = 0
        for _, r in df.iterrows():
            if r["home_team"] == team:
                goals_for = r["home_score"]; goals_against = r["away_score"]
            else:
                goals_for = r["away_score"]; goals_against = r["home_score"]
            gd_sum += (goals_for - goals_against)
            if goals_for > goals_against:
                wins += 1
            elif goals_for == goals_against:
                wins += 0.5  # half credit for draw in recent win metric
        win_rate = wins / len(df)
        avg_gd = gd_sum / len(df)
        return win_rate, avg_gd

    rec_rows = []
    for team in teams:
        rwr, rgd = recent_stats(team, recent_n)
        rec_rows.append((team, rwr, rgd))
    recent = pd.DataFrame(rec_rows, columns=["team","Recent_Win_Rate","Recent_Avg_Goal_Diff"]).set_index("team")

    # join everything
    features = avg_age.to_frame().rename_axis("team").join(latest_rank, how="outer").rename_axis("team")
    features = features.join(stats, how="outer")
    features = features.join(recent, how="outer")
    # drop teams with no rank and no history
    features = features.dropna(subset=["Latest_FIFA_Rank","Historical_Win_Draw_Rate"], how='any')
    # fill remaining NaNs with sensible defaults
    features["Average_Age"] = features["Average_Age"].fillna(features["Average_Age"].median())
    features["Recent_Win_Rate"] = features["Recent_Win_Rate"].fillna(0.0)
    features["Recent_Avg_Goal_Diff"] = features["Recent_Avg_Goal_Diff"].fillna(0.0)
    features["Matches_Played"] = features["Matches_Played"].fillna(0)

    return features
