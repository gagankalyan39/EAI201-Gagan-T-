import os,pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix
import matplotlib.pyplot as plt, seaborn as sns
out_dir='lab6_outputs'; os.makedirs(out_dir,exist_ok=True)
t=pd.DataFrame([{'PassengerId':1,'Survived':0,'Pclass':3,'Sex':'male','Age':22,'SibSp':1,'Parch':0,'Fare':7.25,'Embarked':'S'},{'PassengerId':2,'Survived':1,'Pclass':1,'Sex':'female','Age':38,'SibSp':1,'Parch':0,'Fare':71.2833,'Embarked':'C'},{'PassengerId':3,'Survived':1,'Pclass':3,'Sex':'female','Age':26,'SibSp':0,'Parch':0,'Fare':7.925,'Embarked':'S'},{'PassengerId':4,'Survived':1,'Pclass':1,'Sex':'female','Age':35,'SibSp':1,'Parch':0,'Fare':53.1,'Embarked':'S'},{'PassengerId':5,'Survived':0,'Pclass':3,'Sex':'male','Age':35,'SibSp':0,'Parch':0,'Fare':8.05,'Embarked':'S'}])
t.to_csv(os.path.join(out_dir,'titanic.csv'),index=False)
t['FamilySize']=t['SibSp']+t['Parch']+1; t['Sex_num']=(t['Sex']=='male').astype(int)
t=pd.get_dummies(t,columns=['Embarked'],drop_first=True)
X=t[['Pclass','Age','Fare','FamilySize','Sex_num']]; y=t['Survived']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.4,random_state=42)
m=LogisticRegression(max_iter=200).fit(Xtr,ytr); yp=m.predict(Xte)
acc=accuracy_score(yte,yp); cm=confusion_matrix(yte,yp)
print('Accuracy:',round(acc,4)); print('Confusion Matrix:\n',cm)
sns.heatmap(cm,annot=True,fmt='d',cbar=False,xticklabels=['Died','Survived'],yticklabels=['Died','Survived'])
plt.title('Lab6 Confusion Matrix'); plt.xlabel('Predicted'); plt.ylabel('Actual'); plt.savefig(os.path.join(out_dir,'plot.png'),dpi=200); plt.close()
