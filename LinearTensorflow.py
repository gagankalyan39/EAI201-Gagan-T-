import tensorflow as tf
x_act=[]
y_act=[]
print("Enter the four x values:- ")
for i in range(4):
  print(f"Enter element {i+1}")
  element=input()
  x_act.append(element)
print(x_act)
print("Enter the four y values:- ")
for i in range(4):
  print(f"Enter element {i+1}\n")
  element=input()
  y_act.append(element)
print(y_act)

m=tf.Variable(1)
c=tf.Variable(0)

def predict(x):
  y=m*x+c
  return y
print(predict())




