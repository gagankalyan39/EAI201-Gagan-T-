# main_pipeline.py
from pathlib import Path
import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from modules.data_cleaning import load_and_clean_data
from modules.feature_engineering import build_team_features
from modules.model_training import prepare_training_data, train_model
from modules.model_evaluation import evaluate_model
from modules.model_inference import get_prediction_features

DATA_DIR = Path(__file__).parent / "data"

# --- STEP 1: Load and preprocess ---
print("Loading and cleaning data...")
rank_df, matches_df, players_df, results_df = load_and_clean_data(DATA_DIR)

print("Building team features...")
team_features = build_team_features(rank_df, players_df, results_df, recent_n=5)
print(f"Team features created: {len(team_features)} teams")

# --- STEP 2: Prepare data and train ---
print("Preparing training dataset...")
train_df = prepare_training_data(results_df, team_features)
train_df = train_df.dropna()
print(f"Training samples: {train_df.shape}")

print("Training model...")
model, X_test, y_test = train_model(train_df, team_features)

# --- STEP 3: Evaluate with visualizations ---
print("Evaluating model performance...")
evaluate_model(model, X_test, y_test)

# --- STEP 4: Simulate team strengths for FIFA 2026 ---
print("Calculating model-based strength scores for FIFA 2026 teams...")

teams_48 = [
    "Canada", "Mexico", "United States",
    "Australia", "IR Iran", "Japan", "Jordan", "Qatar",
    "Saudi Arabia", "South Korea", "Uzbekistan",
    "Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay",
    "Algeria", "Cape Verde", "Egypt", "Ghana", "Ivory Coast",
    "Morocco", "Senegal", "South Africa", "Tunisia",
    "New Zealand",
    "England", "France", "Germany", "Spain", "Italy",
    "Portugal", "Netherlands", "Belgium", "Switzerland",
    "Poland", "Croatia", "Denmark", "Norway", "Sweden",
    "Scotland", "Ukraine", "Turkey", "Austria", "Czech Republic",
    "Hungary", "Serbia"
]
teams_48 = sorted(teams_48)

win_strength = {t: 0 for t in teams_48}

# Simulate all match combinations (round-robin style)
for t1, t2 in itertools.combinations(teams_48, 2):
    try:
        X = get_prediction_features(t1, t2, team_features)
        proba = model.predict_proba(X)[0]
        win_strength[t1] += proba[2]  # home win
        win_strength[t2] += proba[0]  # away win
    except Exception:
        continue

# Rank by total simulated strength
sorted_strength = sorted(win_strength.items(), key=lambda x: x[1], reverse=True)
top2 = sorted_strength[:2]

print("\nTop 2 strongest teams predicted by the model:")
for i, (team, score) in enumerate(top2, start=1):
    print(f"{i}. {team}  -  Strength Score: {score:.2f}")

# --- STEP 5: Save model and features ---
base_dir = Path(__file__).parent
with open(base_dir / "model.pkl", "wb") as f:
    pickle.dump(model, f)
with open(base_dir / "features.pkl", "wb") as f:
    pickle.dump(team_features, f)

print("\nModel and features saved successfully in the fifa_predictor folder.")
print("Training and evaluation complete.\n")

# --- STEP 6: Visualization: Top 10 strongest teams ---
top10 = sorted_strength[:10]
teams_top10 = [t for t, _ in top10]
scores_top10 = [s for _, s in top10]

plt.figure(figsize=(8, 5))
sns.barplot(x=scores_top10, y=teams_top10, palette="viridis")
plt.title("Top 10 Strongest Teams Based on Model Strength", fontsize=13, fontweight="bold")
plt.xlabel("Model Strength Score (higher = stronger overall)", fontsize=11)
plt.ylabel("Teams", fontsize=11)
plt.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.show()
