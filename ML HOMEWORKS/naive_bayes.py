import os,pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score,confusion_matrix
import matplotlib.pyplot as plt, seaborn as sns
out_dir='lab5_outputs'; os.makedirs(out_dir,exist_ok=True)
sms=pd.DataFrame({'label':['ham','spam','ham','spam','spam','ham','spam','ham','spam','ham'],'message':['Hey, are we meeting today?',"Congratulations! You've won a free ticket. Call now!",'Can you send the notes?','Free entry in 2 a weekly competition to win cash!','URGENT! Your account has been compromised. Reply now.',"Let's have lunch tomorrow.",'Win money now, claim your prize!','Please review the attached file.','You have been selected for a reward. Click the link.','Are you coming to the party?']})
sms.to_csv(os.path.join(out_dir,'sms.csv'),index=False)
X=CountVectorizer().fit_transform(sms['message']); y=(sms['label']=='spam').astype(int)
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.3,random_state=42)
m=MultinomialNB().fit(Xtr,ytr); yp=m.predict(Xte)
acc=accuracy_score(yte,yp); cm=confusion_matrix(yte,yp)
print('Accuracy:',round(acc,4)); print('Confusion Matrix:\n',cm)
sns.heatmap(cm,annot=True,fmt='d',cbar=False,xticklabels=['Ham','Spam'],yticklabels=['Ham','Spam'])
plt.title('Lab5 Confusion Matrix'); plt.xlabel('Predicted'); plt.ylabel('Actual'); plt.savefig(os.path.join(out_dir,'plot.png'),dpi=200); plt.close()
