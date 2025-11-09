import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split,cross_val_score,KFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
iris=load_iris(as_frame=True); X=iris.frame[iris.feature_names]; y=iris.frame['target']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.3,random_state=42)
rf=RandomForestClassifier(n_estimators=100,random_state=42); log=LogisticRegression(max_iter=300)
rf.fit(Xtr,ytr); log.fit(Xtr,ytr)
acc_rf=accuracy_score(yte,rf.predict(Xte)); acc_log=accuracy_score(yte,log.predict(Xte))
cv=KFold(n_splits=5,shuffle=True,random_state=42)
rf_cv=cross_val_score(rf,X,y,cv=cv); log_cv=cross_val_score(log,X,y,cv=cv)
print('RF Accuracy:',round(acc_rf,4)); print('Logistic Accuracy:',round(acc_log,4))
print('RF CV Mean:',round(rf_cv.mean(),4)); print('Logistic CV Mean:',round(log_cv.mean(),4))
