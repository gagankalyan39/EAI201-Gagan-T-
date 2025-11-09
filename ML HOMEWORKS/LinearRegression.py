import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt

def main(out_dir="lab1_outputs"):
    os.makedirs(out_dir, exist_ok=True)
    np.random.seed(42)
    n = 200
    boston_like = pd.DataFrame({
        'CRIM': np.abs(np.random.normal(3, 8, n)),
        'ZN': np.clip(np.random.normal(12, 20, n), 0, 100),
        'INDUS': np.abs(np.random.normal(10, 6, n)),
        'CHAS': np.random.binomial(1, 0.07, n),
        'NOX': np.clip(np.random.normal(0.5, 0.1, n), 0.3, 0.9),
        'RM': np.clip(np.random.normal(6, 0.7, n), 3, 9),
        'AGE': np.clip(np.random.normal(68, 25, n), 1, 100),
        'DIS': np.abs(np.random.normal(4, 2, n)),
        'RAD': np.random.randint(1, 25, n),
        'TAX': np.random.randint(150, 700, n),
        'PTRATIO': np.clip(np.random.normal(18, 2.5, n), 10, 30),
        'B': np.clip(np.random.normal(350, 50, n), 50, 400),
        'LSTAT': np.clip(np.random.normal(12, 7, n), 0.1, 40)
    })
    boston_like['PRICE'] = (3.5 * boston_like['RM']) - (0.4 * boston_like['LSTAT']) + np.random.normal(0, 3, n) + 10
    csv_path = os.path.join(out_dir, "boston_like.csv")
    boston_like.to_csv(csv_path, index=False)
    X = boston_like.drop('PRICE', axis=1)
    y = boston_like['PRICE']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    print("R²:", round(r2, 4))
    print("RMSE:", round(rmse, 4))
    plt.scatter(y_test, y_pred)
    plt.xlabel("Actual Price")
    plt.ylabel("Predicted Price")
    plt.title("Actual vs Predicted")
    plt.savefig(os.path.join(out_dir, "plot.png"))
    plt.close()

if __name__ == "__main__":
    main()
