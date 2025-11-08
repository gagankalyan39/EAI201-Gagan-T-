
import pandas as pd

def find_best_key(index, name):
    
    if name in index:
        return name
    
    lower = {str(k).lower(): k for k in index}
    if name.lower() in lower:
        return lower[name.lower()]
    
    for k in index:
        if name.lower() in str(k).lower() or str(k).lower() in name.lower():
            return k
    return None

def get_prediction_features(team_a, team_b, team_features):
    a_key = find_best_key(team_features.index, team_a)
    b_key = find_best_key(team_features.index, team_b)
    if a_key is None or b_key is None:
        raise KeyError(f"Feature data missing for {team_a if a_key is None else ''} {team_b if b_key is None else ''}".strip())
    ha = team_features.loc[a_key]
    aw = team_features.loc[b_key]
    feats = {
        "Latest_FIFA_Rank_Diff": aw["Latest_FIFA_Rank"] - ha["Latest_FIFA_Rank"],
        "Average_Age_Diff": ha["Average_Age"] - aw["Average_Age"],
        "Historical_Win_Draw_Rate_Diff": ha["Historical_Win_Draw_Rate"] - aw["Historical_Win_Draw_Rate"],
        "Historical_Avg_Goal_Difference_Diff": ha["Historical_Avg_Goal_Difference"] - aw["Historical_Avg_Goal_Difference"],
        "Recent_Win_Rate_Diff": ha.get("Recent_Win_Rate", 0.0) - aw.get("Recent_Win_Rate", 0.0),
        "Recent_Avg_Goal_Diff_Diff": ha.get("Recent_Avg_Goal_Diff", 0.0) - aw.get("Recent_Avg_Goal_Diff", 0.0)
    }
    return pd.DataFrame([feats])
