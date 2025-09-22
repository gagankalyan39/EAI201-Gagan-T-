import turtle
import math

def pentagon():  #this is a function for a cleaning a pentagon shaped room 
    print("----------Pentagon Room Cleaning---------- \n")
    n=int(input("Enter Length of pentagon room side: \n"))
    vc= turtle.Turtle()
    vc.shape("classic")
    vc.hideturtle()
    vc.speed(0)
    wn= turtle.Screen()
    wn.bgcolor("Orange")
    vc.color("green","red")
    vc.setheading(288)
    vc.penup()
    vc.fd(100)
    vc.pendown()
    vc.setheading(72)
    vc.showturtle()
    vc.speed(3)
    i=0
    x=10
    num=(n/x)
    x=(x*num)/10
      
    while x<n:
      
        for j in range(6):
          vc.fd(n-x)
          vc.left(72)
        vc.left(45)
        vc.fd(n/10)
        vc.right(45)
        x=x+num
    vc.penup() 
    vc.setheading(305)
    vc.fd(n)
    vc.left(180)
  
  
  







def rectangle():  #this is a function which is used for both square and rectangle shaped rooms 
    direct=input("Enter Direction :- \n 1->from Right side \n 2-> From Left side \n")
    vc= turtle.Turtle()
    wn= turtle.Screen()
    l=int(input("Enter the length: "))
    b=int(input("Enter the breadth: "))
    if direct=="2":
      
      vc.penup()
      vc.setheading(90)
      vc.fd(l/2)
      vc.setheading(180)
      vc.fd(l/2)
      vc.setheading(0)
      vc.pendown()
      
      for i in range(3):
        vc.fd(l)
        vc.right(90)
        vc.fd(b/6)
        vc.right(90)
        vc.fd(l)
        vc.left(90)
        vc.fd(b/6)
        vc.left(90)
      for i in range(3):
        vc.fd(l)
        vc.left(90)
        vc.fd(b)
        vc.left(90)
      vc.fd(l)
      vc.setheading(0)

    elif direct=="1":
      vc.speed(0)
      vc.hideturtle()
      vc.penup()
      vc.setheading(0)
      vc.fd(l/2)
      vc.setheading(90)
      vc.fd(l/2)
      vc.setheading(180)
      vc.showturtle()
      vc.pendown()
  
      vc.speed(4)
      for i in range(3):
        vc.fd(l)
        vc.left(90)
        vc.fd(b/6)
        vc.left(90)
        vc.fd(l)
        vc.right(90)
        vc.fd(b/6)
        vc.right(90)
      for i in range(3):
        vc.fd(l)
        vc.right(90)
        vc.fd(b)
        vc.right(90)
      vc.fd(l)
      vc.setheading(180)  
    
    else:
        print("Please choose among 2")
        rectangle()
  
  







def circle(shape):   #this a circular movement of vacuum cleaner for a circular room
    a=int(input("Enter the Radius for the Circular Room:- "))
    wn= turtle.Screen()
    wn.bgcolor("orange")
    vacuum= turtle.Turtle()
    vacuum.shape("circle")
    vacuum.color("purple")
    
    b=-0.05
    angle =0
    vacuum.hideturtle()
    vacuum.penup()
    vacuum.fd(a)
    vacuum.speed(3)
    vacuum.showturtle()
    vacuum.pendown()
    vacuum.setheading(180)
    vacuum.fd(a)
    vacuum.setheading(360)
    
    while True:
        
        r = a + b * angle
        if r <= 0:  # stop when center is reached
            break
        x = r * math.cos(math.radians(angle))
        y = r * math.sin(math.radians(angle))
        vacuum.goto(x, y)
        angle += 5 
    vacuum.speed(1) 
    vacuum.fd(a)
        


def Direct(shape): #this is used for calling different functions according to their shapes 
    value=shape
    if shape=="2":
        circle(shape)
    
    elif shape=="1":
        rectangle()
        
    elif shape=="3":
            pentagon()
            
    else:
        print("Re Enter the option :")
        Direct()
        

def Shape(): #this is used for the room shape or the vacuum movement shapes 
    
    shape=input("Enter the shape of the room:\n 1-> Rectangle \n 2->Circle \n 3-> Pentagon \n")
    if shape=="1" or shape=="3" or shape=="4":
        Direct(shape)   #inputing for directions for a rectangle or a square 
        return shape
    elif shape=="2": #circle 
        print("Auto Cleaning from the dock")
        circle(shape) 
    else:
        print("Re enter the option")
        Shape()

def SOD():     #this is for the size of Dirt particles 
    dirtsize=input("Choose the size of Dirt \n 1->Large(>=2mm)  \n 2->Medium (<2mm)   \n 3->Small(<500microns ) \n")
    if dirtsize=="1" or dirtsize=="2" or  dirtsize=="3":
        Shape()
        return dirtsize
    else:
        print("Re Enter the option :")
        SOD()
          
          




def start():  
    vctype= input(" Floortype:\n 1-> Dry \n 2->Wet \n")  #this is a function used for input of which type of floor 
    if vctype== "1" or vctype == "2":
        SOD()
        return vctype
       
    else:
        print("Enter the Correct option Again")
        start()
        
        



print("Hello . Welcome to my Vacum Cleaner.......")
def vinput():
    vcinput=input("1-> Start \n 2-> Stop \n")
    if vcinput =="1":
        start()
        
    elif vcinput =="2":
        print("Machine has been stopped... Thank You")
    else:
        print("Please enter again")
        vinput()
        
  
 
vinput()    #start or stop 




#option2=start()     #Floortype
#option3= SOD()   #Size of Dirt 
#option3= Shape  Shape of the room 
#option3= Direct Starting Direction 
