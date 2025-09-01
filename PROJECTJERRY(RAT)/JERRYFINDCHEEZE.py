import random 
import collections
import time 



def gencheeze():
    pipes=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']
    cheeze=random.choice(pipes)
    return cheeze

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

def bfs_find_cheese(graph, start, end):
    """
    Finds the shortest path from start to end using Breadth-First Search (BFS).
    """
    queue = collections.deque([[start]])  # store paths, not just nodes
    visited = {start}  # keep track of visited nodes

    while queue:
        path = queue.popleft()     # take the first path
        current_node = path[-1]    # last node in the path

        # check if cheese is found
        if current_node == end:
            return path

        # explore neighbors
        for neighbor in graph.get(current_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return None  # no path exists
    
    
    

print(f"Hello Welcome. Can You help Jerry find cheeze in the shortest path ........")
jerry="1"
for i in range(10):
    print( "Searching for cheeze",i*10,"%")
    time.sleep(0.5)
print("Cheeze found....")
cheeze=gencheeze()
print(cheeze)
path_found = bfs_find_cheese(ways, jerry, cheeze)

if path_found:
    print("The rat found the cheese! Path found:", " -> ".join(path_found))
else:
    print("The rat could not find the cheese.")


PROJECT JERRY COMPLETED ONE
