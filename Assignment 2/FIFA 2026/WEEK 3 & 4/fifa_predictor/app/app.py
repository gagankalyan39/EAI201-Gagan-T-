import os, sys, pickle, numpy as np
from flask import Flask, render_template, request

# fix path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
MODULES_DIR = os.path.join(BASE_DIR, "modules")
if MODULES_DIR not in sys.path:
    sys.path.append(MODULES_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from model_inference import get_prediction_features

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "features.pkl")
if not os.path.exists(MODEL_PATH) or not os.path.exists(FEATURES_PATH):
    raise FileNotFoundError("Run main_pipeline.py to create model.pkl and features.pkl")

MODEL = pickle.load(open(MODEL_PATH, "rb"))
TEAM_FEATURES = pickle.load(open(FEATURES_PATH, "rb"))

TEAMS = [
    "Canada","Mexico","United States",
    "Australia","IR Iran","Japan","Jordan","Qatar","Saudi Arabia","South Korea","Uzbekistan",
    "Argentina","Brazil","Colombia","Ecuador","Paraguay","Uruguay",
    "Algeria","Cape Verde","Egypt","Ghana","Ivory Coast","Morocco","Senegal","South Africa","Tunisia",
    "New Zealand",
    "England","France","Germany","Spain","Italy","Portugal","Netherlands","Belgium","Switzerland",
    "Poland","Croatia","Denmark","Norway","Sweden","Scotland","Ukraine","Turkey","Austria","Czech Republic","Hungary","Serbia"
]
TEAMS = sorted(TEAMS)
HOSTS = ["United States","Mexico","Canada"]

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html", teams=TEAMS, hosts=HOSTS)

@app.route('/predict', methods=['POST'])
def predict():
    team_a = request.form.get("team_a")
    team_b = request.form.get("team_b")
    host = request.form.get("host_country")
    if not team_a or not team_b or not host:
        return render_template("index.html", teams=TEAMS, hosts=HOSTS, error="Select teams and host.")
    if team_a == team_b:
        return render_template("index.html", teams=TEAMS, hosts=HOSTS, error="Teams must be different.")

    try:
        X = get_prediction_features(team_a, team_b, TEAM_FEATURES)
    except KeyError as e:
        return render_template("index.html", teams=TEAMS, hosts=HOSTS, error=str(e))

    # host advantage
    if host == team_a:
        X.iloc[0, :] += 0.07
    elif host == team_b:
        X.iloc[0, :] -= 0.07

    proba = MODEL.predict_proba(X)[0]
    # map probabilities: classes are [0,1,2] -> away, draw, home
    # find indices robustly
    classes = list(MODEL.classes_)
    def prob_for(label):
        return proba[classes.index(label)] if label in classes else 0.0

    prob_away = prob_for(0)
    prob_draw = prob_for(1)
    prob_home = prob_for(2)

    probabilities = {
        f"{team_a} Win": f"{prob_home*100:.2f}%",
        "Draw": f"{prob_draw*100:.2f}%",
        f"{team_b} Win": f"{prob_away*100:.2f}%"
    }

    # choose winner text
    idx = np.argmax([prob_home, prob_draw, prob_away])
    if idx == 0:
        result = f"{team_a} likely wins in {host}."
    elif idx == 1:
        result = f"The match between {team_a} and {team_b} in {host} may end in a draw."
    else:
        result = f"{team_b} likely wins in {host}."

    return render_template("index.html", teams=TEAMS, hosts=HOSTS, result=result, probabilities=probabilities, team_a=team_a, team_b=team_b, host_country=host)

if __name__ == "__main__":
    print("Server running at http://127.0.0.1:5000")
    app.run(debug=True)
