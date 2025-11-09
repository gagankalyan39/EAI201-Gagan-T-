import os,numpy as np,pandas as pd,matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score,mean_squared_error
out_dir="lab1_outputs"
os.makedirs(out_dir,exist_ok=True)
np.random.seed(42)
n=200
df=pd.DataFrame({'CRIM':np.abs(np.random.normal(3,8,n)),'ZN':np.clip(np.random.normal(12,20,n),0,100),'INDUS':np.abs(np.random.normal(10,6,n)),'CHAS':np.random.binomial(1,0.07,n),'NOX':np.clip(np.random.normal(0.5,0.1,n),0.3,0.9),'RM':np.clip(np.random.normal(6,0.7,n),3,9),'AGE':np.clip(np.random.normal(68,25,n),1,100),'DIS':np.abs(np.random.normal(4,2,n)),'RAD':np.random.randint(1,25,n),'TAX':np.random.randint(150,700,n),'PTRATIO':np.clip(np.random.normal(18,2.5,n),10,30),'B':np.clip(np.random.normal(350,50,n),50,400),'LSTAT':np.clip(np.random.normal(12,7,n),0.1,40)})
df['PRICE']=(3.5*df['RM'])-(0.4*df['LSTAT'])+np.random.normal(0,3,n)+10
df.to_csv(os.path.join(out_dir,'boston_like.csv'),index=False)
X=df.drop('PRICE',axis=1); y=df['PRICE']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42)
m=LinearRegression().fit(Xtr,ytr)
yp=m.predict(Xte)
r2=r2_score(yte,yp); rmse=mean_squared_error(yte,yp)**0.5
print('R²:',round(r2,4)); print('RMSE:',round(rmse,4))
plt.scatter(yte,yp); plt.xlabel('Actual'); plt.ylabel('Predicted'); plt.title('Lab1 Actual vs Predicted')
plt.grid(); plt.savefig(os.path.join(out_dir,'plot.png'),dpi=200); plt.close()
