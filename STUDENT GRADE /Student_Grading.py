numsubj = int(input("Enter number of subjects: "))  #Input for Number of Subjects

total = 0 #Initializing total as 0

# INPUT OF MARKS FROM USER
for i in range(numsubj):
    marks = int(input(f"Enter marks for subject {i+1}: "))
    total =total + marks
avg = total / numsubj #Taking Average of all Subjects...  


def output(grade):  # Printing the Result if its <=100
    print("Congratulations!!!!")
    print("Result:-")
    print("Total Marks:-", total)
    print("avg Marks:-", avg)
    print("Grade:-", grade)
    print("Thank You")

#GRADING ACCORDING TO MARKS
def calc(avg):
    if avg<=100:     
        print("--------------------")
        if avg >=95:
            grade="A+"
            output(grade)         #Calling output Function If the marks are <=100
        elif avg >= 90:
            grade = "A"
            output(grade)
        elif avg >= 85:
            grade = "B+"
            output(grade)
        elif avg >= 80:
            grade = "B"
            output(grade)
        elif avg >= 75:
            grade = "C+"
            output(grade)
        elif avg >= 70:
            grade = "C"
            output(grade)
        elif avg>=50:
            grade="D"
            output(grade)
        else:
            grade = "F"
            output(grade)
    else:
        print("Please Enter Valid Subject Marks!!!!..") #If avg marks> 100 No grading is Given ...
calc(avg)  #Calling the Function To Start the Program 
#Thank You
