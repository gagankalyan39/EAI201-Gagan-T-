import os,pandas as pd,numpy as np,matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
out_dir='lab2_outputs'; os.makedirs(out_dir,exist_ok=True)
df=pd.DataFrame({'Area_sqft':[1200,1400,1600,1700,1850],'Rooms':[3,4,3,5,4],'Distance_km':[5,3,8,2,4],'Age_years':[10,3,20,15,7],'Price_Lacs':[120,150,130,180,170]})
df.to_csv(os.path.join(out_dir,'house_price.csv'),index=False)
X=df[['Area_sqft','Rooms','Distance_km','Age_years']]; y=df['Price_Lacs']
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42)
m=LinearRegression().fit(Xtr,ytr)
yp=m.predict(Xte)
rmse=mean_squared_error(yte,yp)**0.5
print('RMSE:',round(rmse,4)); print('Actual:',list(yte)); print('Predicted:',list(np.round(yp,2)))
plt.scatter(yte,yp); plt.xlabel('Actual (₹ Lacs)'); plt.ylabel('Predicted (₹ Lacs)')
plt.title('Lab2 Actual vs Predicted'); plt.grid(); plt.savefig(os.path.join(out_dir,'plot.png'),dpi=200); plt.close()
