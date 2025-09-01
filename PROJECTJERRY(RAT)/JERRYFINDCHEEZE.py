import random 
import collections

pipes=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']

def gencheeze():
    cheeze=random.choice(pipes)
    return cheeze

def paths():
    ways={
        '1':['2','3'],
        '2':['1','4','5'],
        '3':['1','6','7'],
        '4':['2','8','9'],
        '5':['2','10','11'],
        '6':['3','12','13'],
        '7':['3','14','15'],
        '8':['4'],
        '9':['4'],
        '10':['5'],
        '11':['5','16','17'],
        '12':['6','18','19'],
        '13':['6'],
        '14':['7','20'],
        '15':['7'],
        '16':['11'],
        '17':['11'],
        '18':['12'],
        '19':['12'],
        '20':['14'],
    }
    
    
    

print(f"Hello Welcome. Can You help Jerry find cheeze in the shortest path ........\n{pipes}")
for i in range(10):
    print( "Searching for cheeze",i*10,"%")
print("Cheeze found....")



cheeze=gencheeze()
print(cheeze)
