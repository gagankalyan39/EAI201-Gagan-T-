import os,pandas as pd,matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix
out_dir='lab3_outputs'; os.makedirs(out_dir,exist_ok=True)
iris=load_iris(as_frame=True); df=iris.frame.copy(); df['is_setosa']=(df['target']==0).astype(int)
df.to_csv(os.path.join(out_dir,'iris_setosa.csv'),index=False)
X=df[iris.feature_names]; y=df['is_setosa']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.3,random_state=42)
m=LogisticRegression(max_iter=200).fit(Xtr,ytr)
yp=m.predict(Xte)
acc=accuracy_score(yte,yp); cm=confusion_matrix(yte,yp)
print('Accuracy:',round(acc,4)); print('Confusion Matrix:\n',cm)
plt.scatter(Xte.iloc[:,2],Xte.iloc[:,3],c=yp,cmap='viridis'); plt.xlabel('Petal length'); plt.ylabel('Petal width')
plt.title('Lab3 Iris Petal (predicted classes)'); plt.savefig(os.path.join(out_dir,'plot.png'),dpi=200); plt.close()
