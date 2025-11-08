
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import numpy as np

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Away","Draw","Home"], yticklabels=["Away","Draw","Home"])
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

    # ROC for home-win class (2)
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)
        # roc using one-vs-rest for class 2
        try:
            fpr, tpr, _ = roc_curve((y_test==2).astype(int), y_proba[:, 2])
            roc_auc = auc(fpr, tpr)
            plt.figure(); plt.plot(fpr,tpr,label=f"AUC={roc_auc:.2f}"); plt.plot([0,1],[0,1],'--'); plt.title("ROC (Home win)"); plt.legend(); plt.show()
        except Exception:
            pass

    # feature importance if available (underlying estimator)
    try:
        # calibrated wrapper -> estimator_
        est = model.base_estimator if hasattr(model, "base_estimator") else getattr(model, "estimator", None)
        if est is None and hasattr(model, "estimators_"):
            est = model
        if hasattr(est, "feature_importances_"):
            imp = est.feature_importances_
            cols = X_test.columns
            order = np.argsort(imp)[::-1]
            plt.figure(figsize=(6,4))
            sns.barplot(x=imp[order], y=cols[order]); plt.title("Feature Importance"); plt.show()
    except Exception:
        pass
