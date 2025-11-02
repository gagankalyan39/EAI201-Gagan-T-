# FIFA 2026 WORLD CUP PREDICTION MODEL - COMPLETE PIPELINE

# STEP 0: Install Required Libraries
!pip install -q kaggle requests beautifulsoup4 pandas numpy scikit-learn xgboost

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib

print("All libraries installed successfully!")

# STEP 1: Setup Kaggle API (Required for downloading datasets)
"""
IMPORTANT: Before running this cell, upload your kaggle.json file:
1. Go to Kaggle.com -> Account -> API -> Create New Token
2. Download kaggle.json
3. Upload it using the file icon in Colab's left sidebar
"""
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

print("Kaggle API configured!")

# WEEK 1: DATA ACQUISITION & FEATURE ENGINEERING

# 1.1: Download Match History (df_matches)
print("\nWEEK 1: DATA ACQUISITION & FEATURE ENGINEERING")
print("\nDownloading international match results (1872-2025)...")
!kaggle datasets download -d martj42/international-football-results-from-1872-to-2017
!unzip -q international-football-results-from-1872-to-2017.zip

# Load matches
df_matches = pd.read_csv('results.csv')
print(f"Loaded {len(df_matches):,} international matches")
print(df_matches.head())

# 1.2: Download FIFA Rankings (df_ranks)
print("\nDownloading FIFA world rankings (1992-2024)...")
!kaggle datasets download -d cashncarry/fifaworldranking
!unzip -q fifaworldranking.zip

# Load rankings
df_ranks = pd.read_csv('fifa_ranking-2024-07-19.csv')
print(f"Loaded {len(df_ranks):,} FIFA ranking records")
print(df_ranks.head())

# 1.3: Scrape Transfermarkt Player Data (df_player_data)
print("\nScraping Transfermarkt for player data...")

class TransfermarktScraper:
    """
    Scrapes player age and caps from Transfermarkt squad pages
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.transfermarkt.com"
        
    def get_team_squad_data(self, team_name, team_id, season='2024'):
        """
        Scrape squad data for a specific team
        """
        url = f"{self.base_url}/{team_name}/startseite/verein/{team_id}/saison_id/{season}"
        
        try:
            time.sleep(5)  # Respectful delay to avoid overwhelming server
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch {team_name}: Status {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            player_rows = soup.find_all('tr', class_=['odd', 'even'])
            
            ages = []
            caps = []
            
            for row in player_rows:
                # Extract age
                age_cell = row.find('td', class_='zentriert')
                if age_cell:
                    age_text = age_cell.get_text(strip=True)
                    try:
                        ages.append(int(age_text))
                    except ValueError:
                        pass
                
                # Extract caps (international appearances)
                caps_cell = row.find('td', {'class': 'zentriert'})
                if caps_cell:
                    caps_text = caps_cell.get_text(strip=True)
                    try:
                        caps.append(int(caps_text))
                    except ValueError:
                        pass
            
            if ages:
                return {
                    'team': team_name.replace('-', ' ').title(),
                    'avg_age': np.mean(ages),
                    'avg_caps': np.mean(caps) if caps else 0,
                    'squad_size': len(ages)
                }
            else:
                print(f"No player data found for {team_name}")
                return None
                
        except Exception as e:
            print(f"Error scraping {team_name}: {str(e)}")
            return None

TEAMS_TO_SCRAPE = [
    ('brazil', '3439'), ('argentina', '3437'), ('france', '3376'),
    ('england', '3299'), ('spain', '3375'), ('germany', '3262'),
    ('portugal', '3300'), ('netherlands', '3379'), ('belgium', '3382'),
    ('italy', '3376'), ('croatia', '3556'), ('uruguay', '3449'),
    ('denmark', '3436'), ('switzerland', '3384'), ('mexico', '6303'),
    ('united-states', '3505'), ('colombia', '3816'), ('japan', '3435'),
    ('iran', '3582'), ('south-korea', '3589'), ('australia', '3433'),
    ('morocco', '3575'), ('senegal', '3382'), ('poland', '3442'),
    ('wales', '3864'), ('canada', '3505'), ('ecuador', '3816'),
    ('saudi-arabia', '3554'), ('ghana', '3436'), ('cameroon', '3434'),
    ('serbia', '3438'), ('tunisia', '3670'),
]

# Initialize scraper
scraper = TransfermarktScraper()

# Scrape all teams
player_data_list = []

print(f"Scraping {len(TEAMS_TO_SCRAPE)} national team squads...")
for team_name, team_id in TEAMS_TO_SCRAPE:
    print(f"  -> {team_name}...", end=" ")
    team_data = scraper.get_team_squad_data(team_name, team_id)
    if team_data:
        player_data_list.append(team_data)
        print(f" (Avg Age: {team_data['avg_age']:.1f}, Avg Caps: {team_data['avg_caps']:.1f})")
    else:
        print(" [Failed]")

# Create player data DataFrame
df_player_data = pd.DataFrame(player_data_list)
print(f"\nSuccessfully scraped {len(df_player_data)} teams")
print(df_player_data.head())

# Save scraped data
df_player_data.to_csv('player_squad_data.csv', index=False)
print("Saved to 'player_squad_data.csv'")

# STEP 2: DATA CLEANING & STANDARDIZATION
print("\nSTEP 2: DATA CLEANING & STANDARDIZATION")

# 2.1: Standardize Team Names
TEAM_NAME_MAP = {
    'USA': 'United States', 'United States': 'United States',
    'Korea Republic': 'South Korea', 'South Korea': 'South Korea',
    'Iran': 'Iran', 'IR Iran': 'Iran',
    'England': 'England', 'Wales': 'Wales', 'Scotland': 'Scotland',
}

def standardize_team_name(name):
    """Standardize team names across datasets"""
    return TEAM_NAME_MAP.get(name, name)

# Apply standardization
df_matches['home_team'] = df_matches['home_team'].apply(standardize_team_name)
df_matches['away_team'] = df_matches['away_team'].apply(standardize_team_name)
df_ranks['country_full'] = df_ranks['country_full'].apply(standardize_team_name)
df_player_data['team'] = df_player_data['team'].apply(standardize_team_name)

print("Team names standardized")

# 2.2: Convert Dates
df_matches['date'] = pd.to_datetime(df_matches['date'])
df_ranks['rank_date'] = pd.to_datetime(df_ranks['rank_date'])

print("Dates converted to datetime format")

# 2.3: Filter Recent Matches (2000-2025)
df_matches = df_matches[df_matches['date'] >= '2000-01-01'].copy()
print(f"Filtered to {len(df_matches):,} matches since 2000")

# STEP 3: ADVANCED FEATURE ENGINEERING
print("\nSTEP 3: ADVANCED FEATURE ENGINEERING")

# 3.1: Merge FIFA Rankings
def get_team_rank_at_date(team, match_date, df_ranks):
    """Get the most recent FIFA rank before the match date"""
    team_ranks = df_ranks[
        (df_ranks['country_full'] == team) & 
        (df_ranks['rank_date'] <= match_date)
    ].sort_values('rank_date', ascending=False)
    
    if len(team_ranks) > 0:
        return team_ranks.iloc[0]['total_points']
    return np.nan

# Add ranking points for home and away teams
print("Merging FIFA rankings...")
df_matches['home_rank_points'] = df_matches.apply(
    lambda row: get_team_rank_at_date(row['home_team'], row['date'], df_ranks),
    axis=1
)

df_matches['away_rank_points'] = df_matches.apply(
    lambda row: get_team_rank_at_date(row['away_team'], row['date'], df_ranks),
    axis=1
)

print("FIFA rankings merged")

# 3.2: Merge Player Data (Age & Experience)
print("Merging player squad data...")

# Create lookup dictionaries
age_dict = dict(zip(df_player_data['team'], df_player_data['avg_age']))
caps_dict = dict(zip(df_player_data['team'], df_player_data['avg_caps']))

# Add to matches
df_matches['home_avg_age'] = df_matches['home_team'].map(age_dict)
df_matches['away_avg_age'] = df_matches['away_team'].map(age_dict)
df_matches['home_avg_caps'] = df_matches['home_team'].map(caps_dict)
df_matches['away_avg_caps'] = df_matches['away_team'].map(caps_dict)

print("Player data merged")

# 3.3: Calculate Differential Features
df_matches['ranking_diff'] = df_matches['home_rank_points'] - df_matches['away_rank_points']
df_matches['age_diff'] = df_matches['home_avg_age'] - df_matches['away_avg_age']
df_matches['experience_diff'] = df_matches['home_avg_caps'] - df_matches['away_avg_caps']

print("Differential features calculated")

# 3.4: Calculate Rolling Form (Win Rate)
print("Calculating rolling form features...")

def calculate_rolling_form(df, window=5):
    """Calculate rolling win rate for each team"""
    form_dict = {}
    
    for team in df['home_team'].unique():
        # Get all matches for this team
        team_matches = df[
            (df['home_team'] == team) | (df['away_team'] == team)
        ].sort_values('date')
        
        # Determine wins
        team_wins = []
        for _, match in team_matches.iterrows():
            if match['home_team'] == team:
                win = 1 if match['home_score'] > match['away_score'] else 0
            else:
                win = 1 if match['away_score'] > match['home_score'] else 0
            team_wins.append(win)
        
        # Calculate rolling average
        if len(team_wins) >= window:
            rolling_form = pd.Series(team_wins).rolling(window=window, min_periods=1).mean()
            form_dict[team] = rolling_form.iloc[-1]
        else:
            form_dict[team] = np.mean(team_wins) if team_wins else 0.5
    
    return form_dict

form_dict = calculate_rolling_form(df_matches)

df_matches['home_form'] = df_matches['home_team'].map(form_dict)
df_matches['away_form'] = df_matches['away_team'].map(form_dict)
df_matches['form_diff'] = df_matches['home_form'] - df_matches['away_form']

print("Rolling form features calculated")

# 3.5: Define Target Variable
# Binary classification: 1 = Home Win/Draw, 0 = Away Win
df_matches['target'] = (df_matches['home_score'] >= df_matches['away_score']).astype(int)

print("Target variable defined")

# 3.6: Create Final Feature Set
# Select only complete cases
feature_cols = [
    'ranking_diff', 'age_diff', 'experience_diff', 'form_diff',
    'home_rank_points', 'away_rank_points'
]

df_final = df_matches[feature_cols + ['target']].dropna()

print(f"\nFinal dataset ready: {len(df_final):,} matches with complete features")
print(f"\nFeature columns: {feature_cols}")
print(f"\nTarget distribution:\n{df_final['target'].value_counts(normalize=True)}")

# Save processed data
df_final.to_csv('ml_ready_dataset.csv', index=False)
print("\nSaved to 'ml_ready_dataset.csv'")

# WEEK 2: MODEL TRAINING & TUNING
print("\nWEEK 2: MODEL TRAINING & HYPERPARAMETER TUNING")

# STEP 1: Prepare Train/Validation/Test Split
X = df_final[feature_cols]
y = df_final['target']

# Split: 70% train, 15% validation, 15% test
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp  # 0.176 of 85% ~= 15%
)

print(f"\nData split complete:")
print(f"   Training set: {len(X_train):,} samples")
print(f"   Validation set: {len(X_val):,} samples")
print(f"   Test set: {len(X_test):,} samples")

# STEP 2: Train Baseline Model (Logistic Regression)
print("\nBASELINE MODEL: Logistic Regression")

lr_model = LogisticRegression(random_state=42, max_iter=1000)
lr_model.fit(X_train, y_train)

# Evaluate on validation set
lr_val_pred = lr_model.predict(X_val)
lr_val_acc = accuracy_score(y_val, lr_val_pred)

print(f"\nLogistic Regression trained")
print(f"Validation Accuracy: {lr_val_acc:.4f}")

# STEP 3: Train Advanced Model (Random Forest)
print("\nADVANCED MODEL: Random Forest")

rf_model = RandomForestClassifier(random_state=42, n_estimators=100)
rf_model.fit(X_train, y_train)

# Evaluate on validation set
rf_val_pred = rf_model.predict(X_val)
rf_val_acc = accuracy_score(y_val, rf_val_pred)

print(f"\nRandom Forest trained")
print(f"Validation Accuracy: {rf_val_acc:.4f}")

# STEP 4: Hyperparameter Tuning (GridSearch)
print("\nHYPERPARAMETER TUNING: Random Forest Grid Search")

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

print("\nSearching optimal parameters...")
print(f"Total combinations to test: {np.prod([len(v) for v in param_grid.values()])}")

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=3,
    scoring='accuracy',
    n_jobs=-1,
    verbose=0 # Set verbose to 0 to minimize output during search
)

grid_search.fit(X_train, y_train)

print(f"\nGrid search complete!")
print(f"\nBest parameters: {grid_search.best_params_}")
print(f"Best CV score: {grid_search.best_score_:.4f}")

# STEP 5: Train XGBoost Model
print("\nADVANCED MODEL: XGBoost")

xgb_model = xgb.XGBClassifier(
    random_state=42,
    n_estimators=200,
    max_depth=10,
    learning_rate=0.1,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train)

# Evaluate on validation set
xgb_val_pred = xgb_model.predict(X_val)
xgb_val_acc = accuracy_score(y_val, xgb_val_pred)

print(f"\nXGBoost trained")
print(f"Validation Accuracy: {xgb_val_acc:.4f}")

# STEP 6: Model Comparison & Selection
print("\nMODEL COMPARISON (Validation Set)")

results = pd.DataFrame({
    'Model': ['Logistic Regression', 'Random Forest', 'RF Tuned', 'XGBoost'],
    'Validation Accuracy': [
        lr_val_acc,
        rf_val_acc,
        grid_search.best_score_,
        xgb_val_acc
    ]
})

print("\n" + results.to_string(index=False))

# Select best model
best_model_name = results.loc[results['Validation Accuracy'].idxmax(), 'Model']
best_accuracy = results['Validation Accuracy'].max()

print(f"\nBest model: {best_model_name} (Accuracy: {best_accuracy:.4f})")

# Use the tuned Random Forest as final model
final_model = grid_search.best_estimator_

# STEP 7: Feature Importance
print("\nFEATURE IMPORTANCE")

feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': final_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n" + feature_importance.to_string(index=False))

# FINAL: Save Model for Week 3 Evaluation
joblib.dump(final_model, 'final_model.pkl')
joblib.dump((X_test, y_test), 'test_data.pkl')

print("\nWEEK 1 & WEEK 2 COMPLETE!")
print("\nSaved files:")
print("   * player_squad_data.csv - Scraped player data")
print("   * ml_ready_dataset.csv - Processed feature set")
print("   * final_model.pkl - Best trained model")
print("   * test_data.pkl - Reserved test set for Week 3")
print("\nReady for Week 3: Model Evaluation on Test Set")
