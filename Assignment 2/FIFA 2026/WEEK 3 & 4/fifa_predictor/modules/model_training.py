
import os, pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

def prepare_training_data(results_df, team_features):
    rows = []
    for _, r in results_df.iterrows():
        h, a = r["home_team"], r["away_team"]
        if h not in team_features.index or a not in team_features.index:
            continue
        ha = team_features.loc[h]
        aw = team_features.loc[a]
        row = {
            "Latest_FIFA_Rank_Diff": aw["Latest_FIFA_Rank"] - ha["Latest_FIFA_Rank"],
            "Average_Age_Diff": ha["Average_Age"] - aw["Average_Age"],
            "Historical_Win_Draw_Rate_Diff": ha["Historical_Win_Draw_Rate"] - aw["Historical_Win_Draw_Rate"],
            "Historical_Avg_Goal_Difference_Diff": ha["Historical_Avg_Goal_Difference"] - aw["Historical_Avg_Goal_Difference"],
            "Recent_Win_Rate_Diff": ha["Recent_Win_Rate"] - aw["Recent_Win_Rate"],
            "Recent_Avg_Goal_Diff_Diff": ha["Recent_Avg_Goal_Diff"] - aw["Recent_Avg_Goal_Diff"]
        }
        # label: 2 home win,1 draw,0 away win
        if r["home_score"] > r["away_score"]:
            y = 2
        elif r["home_score"] == r["away_score"]:
            y = 1
        else:
            y = 0
        row["y"] = y
        rows.append(row)
    df = pd.DataFrame(rows)
    return df

def train_model(df, team_features):
    # drop rows with all NaNs
    df = df.dropna(how="all")
    # fill remaining NaNs with column median
    df = df.fillna(df.median())
    X = df.drop(columns="y")
    y = df["y"]

    # split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # use HistGradientBoosting (handles missing values, fast)
    base = HistGradientBoostingClassifier(max_iter=300, random_state=42)
    # calibrate probabilities (Platt) for reliable percentages
    model = CalibratedClassifierCV(base, cv=3)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"Model accuracy: {acc:.3f}")

    # save best model + features
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with open(os.path.join(base_dir, "model.pkl"), "wb") as f:
        pickle.dump(model, f)
    with open(os.path.join(base_dir, "features.pkl"), "wb") as f:
        pickle.dump(team_features, f)
    return model, X_test, y_test
