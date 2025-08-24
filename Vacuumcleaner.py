


def MoveTurtle():
    print("This is still pending")



def Direct():
    direction =input("Enter the Direction to be followed \n 1-> Straight \n 2-> Back \n 3-> Left \n 4->Right \n ")
    if direction =="1" or direction =="2" or direction=="3" or direction =="4":
        MoveTurtle()
        return direction
    else:
        print("Re Enter the option :")
        Direct()
        

def Shape():
    
    shape=input("Enter the shape of the room:\n 1-> Rectangle \n 2->Circle \n 3-> Pentagon ")
    if shape=="1" or shape=="2" or shape=="3" or shape=="4":
        Direct()
        return shape
    else:
        print("Re enter the option")
        Shape()

def SOD():
    dirtsize=input("Choose the size of Dirt \n 1->Large(>=2mm)  \n 2->Medium (<2mm)   \n 3->Small(<500microns ) \n")
    if dirtsize=="1" or dirtsize=="2" or  dirtsize=="3":
        Shape()
        return dirtsize
    else:
        print("Re Enter the option :")
        SOD()
          
          




def start():  
    vctype= input(" Floortype:\n 1-> Dry \n 2->Wet \n")
    if vctype== "1" or vctype == "2":
        SOD()
        return vctype
       
    else:
        print("Enter the Correct option Again")
        start()
        
        



print("Hello . Welcome to my Vacum Cleaner.......")
def vinput():
    vcinput=input("1-> Start \n 2-> Stop \n")
    return vcinput #returning whether the machine should start or stop
  
 
option1= vinput()    #start or stop 


if option1 =="1":
    start()
elif option =="2":
    print("Machine has been stopped... Thank You")
else:
    print("Please enter again")
    vinput()

#option2=start()     #Floortype
#option3= SOD()   #Size of Dirt 
#option3= Shape  Shape of the room 
#option3= Direct Starting Direction 
