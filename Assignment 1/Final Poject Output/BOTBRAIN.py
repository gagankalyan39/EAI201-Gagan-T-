#PART 1 CODE 



import collections
import heapq
import math

# ====================================================================
# 1. CAMPUS ENVIRONMENT MODELING (UPDATED)
# =====================================================================

# Graph representation of the campus where keys are buildings (nodes)
# and values are a list of tuples (neighbor, distance, speed_factor).
# Speed factor is a multiplier for walking speed. E.g., 0.8 for slower paths.
campus_graph = {
    'Entry Gate': [('Security Gate', 180, 1.0)],
    'Exit Gate': [('Security Gate', 180, 1.0), ('Hostel Building 1', 400, 1.0)],
    'Security Gate': [('Entry Gate', 180, 1.0), ('Exit Gate', 180, 1.0), ('Flag Post', 50, 1.0)],
    'Flag Post': [('Security Gate', 50, 1.0), ('Academic Block 1 Entrance', 210, 1.0)], # 90m + 120m combined
    
    # NEW INTERNAL NODES FOR ACADEMIC BLOCK 1
    'Academic Block 1 Entrance': [
        ('Flag Post', 210, 1.0), 
        ('Lawn Area', 140, 1.0), 
        ('Library', 0, 1.0), 
        ('Auditorium', 0, 1.0), 
        ('Admissions', 50, 1.0), 
        ('Registrar Office', 60, 1.0), 
        ('Cafeteria', 10, 1.0)
    ],
    # --- UPDATED: New direct connections from Auditorium ---
    'Library': [
        ('Academic Block 1 Entrance', 0, 1.0),
        ('Auditorium', 15, 1.0)  # NEW: Direct connection to Auditorium
    ],
    'Auditorium': [
        ('Academic Block 1 Entrance', 0, 1.0),
        ('Library', 15, 1.0),    # NEW: Direct connection to Library
        ('Cafeteria', 20, 1.0)   # NEW: Direct connection to Cafeteria
    ],
    'Admissions': [('Academic Block 1 Entrance', 50, 1.0)],
    'Registrar Office': [
        ('Academic Block 1 Entrance', 60, 1.0), 
        ('Finance Dept', 10, 1.0)
    ],
    'Finance Dept': [
        ('Registrar Office', 10, 1.0),
        ('Academic Block 1 Entrance', 70, 1.0) # Calculated distance
    ],
    'Cafeteria': [
        ('Academic Block 1 Entrance', 10, 1.0), 
        ('Academic Block 2', 50, 1.0),
        ('Auditorium', 20, 1.0)  # NEW: Direct connection to Auditorium
    ],

    # REMAINING EXTERNAL NODES
    'Lawn Area': [('Academic Block 1 Entrance', 140, 1.0), ('Academic Block 2', 140, 1.0)],
    'Academic Block 2': [('Lawn Area', 140, 1.0), ('Cafeteria', 50, 1.0), ('Food Court', 240, 1.0), ('Hostel Building 2', 50, 1.0)],
    'Hostel Building 2': [('Academic Block 2', 50, 1.0), ('Hostel Building 1', 240, 1.0), ('Food Court', 50, 1.0)],
    'Food Court': [('Academic Block 2', 240, 1.0), ('Cricket Ground', 40, 1.0), ('Hostel Building 1', 120, 1.0)], # 50m + 70m combined
    'Hostel Building 1': [('Hostel Building 2', 240, 1.0), ('Food Court', 120, 1.0), ('Exit Gate', 400, 1.0)],
    'Cricket Ground': [('Food Court', 40, 1.0)]
}

# Heuristic data for A* Search (coordinates for Euclidean distance).
# These are relative coordinates on an imaginary grid representing the map.
# --- UPDATED: Added new coordinates to improve A* accuracy ---
building_coords = {
    'Entry Gate': (0, 0),
    'Exit Gate': (360, 0),
    'Security Gate': (180, 0),
    'Flag Post': (180, 50),
    'Academic Block 1 Entrance': (180, 260),
    'Library': (170, 260), # Shifted slightly to reflect new connection
    'Auditorium': (180, 260), # Shifted slightly to be between Library and Cafeteria
    'Admissions': (180, 310),
    'Registrar Office': (180, 320),
    'Finance Dept': (190, 320),
    'Cafeteria': (190, 260), # Shifted slightly to reflect new connection
    'Lawn Area': (180, 400),
    'Academic Block 2': (180, 540),
    'Food Court': (420, 540),
    'Cricket Ground': (420, 580),
    'Hostel Building 1': (660, 700),
    'Hostel Building 2': (230, 600)
}

# Building Information (for display)
building_info = {
    'Entry Gate': "Main Entry Gate (A).",
    'Exit Gate': "Main Exit Gate (B).",
    'Security Gate': "Security Gate (C), central checkpoint.",
    'Flag Post': "Campus Flag Post (D).",
    'Academic Block 1 Entrance': (
        "Main Entrance to Academic Block 1. This building is multi-story with lifts on both sides. "
        "The following internal locations can be found here."
    ),
    'Library': "Located in Academic Block 1 on the right side. It has a direct connection to the Auditorium.",
    'Auditorium': "Located in Academic Block 1 on the underground (UG) floor. It has direct exits to both the Library and the Cafeteria.",
    'Admissions': "Located in Academic Block 1 on the 1st floor, 50m from the entrance.",
    'Registrar Office': "Located in Academic Block 1 on the 3rd floor, 60m from the entrance.",
    'Finance Dept': "Located in Academic Block 1 on the 3rd floor, 10m from the Registrar Office.",
    'Cafeteria': "Located in Academic Block 1 on the lower ground (LG) floor. This exit provides the internal connection to Academic Block 2 and the Auditorium.",
    'Academic Block 2': "Academic Block 2 is a central hub in the upper part of the campus. It is connected to Academic Block 1 via the Cafeteria exit.",
    'Lawn Area': "Open Lawn Area (E).",
    'Hostel Building 2': "Hostel Building 2 (F).",
    'Food Court': "Campus Food Court (G).",
    'Hostel Building 1': "Hostel Building 1 (H).",
    'Cricket Ground': "Cricket Ground (I).",
}

# Constants
WALKING_SPEED_MPS = 1.4  # meters per second (approx. 5 km/h)

def calculate_time(distance):
    """Calculates estimated walking time in minutes."""
    time_seconds = distance / WALKING_SPEED_MPS
    return round(time_seconds / 60, 2)

# ====================================================================
# 2. SEARCH ALGORITHM IMPLEMENTATIONS
# ====================================================================

def bfs(start, goal):
    """Breadth-First Search implementation."""
    print("Starting BFS...")
    queue = collections.deque([(start, [start], 0)])
    visited = {start}
    nodes_explored = 0

    while queue:
        nodes_explored += 1
        current_node, path, distance = queue.popleft()
        if current_node == goal:
            return path, distance, nodes_explored
        for neighbor, edge_dist, _ in campus_graph.get(current_node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                new_distance = distance + edge_dist
                queue.append((neighbor, new_path, new_distance))
    return None, 0, nodes_explored

def dfs(start, goal):
    """Depth-First Search implementation."""
    print("Starting DFS...")
    stack = [(start, [start], 0)]
    visited = set()
    nodes_explored = 0
    while stack:
        nodes_explored += 1
        current_node, path, distance = stack.pop()
        if current_node in visited:
            continue
        visited.add(current_node)
        if current_node == goal:
            return path, distance, nodes_explored
        for neighbor, edge_dist, _ in reversed(campus_graph.get(current_node, [])):
            if neighbor not in visited:
                new_path = path + [neighbor]
                new_distance = distance + edge_dist
                stack.append((neighbor, new_path, new_distance))
    return None, 0, nodes_explored

def ucs(start, goal):
    """Uniform Cost Search implementation."""
    print("Starting UCS...")
    priority_queue = [(0, start, [start])]
    visited_costs = {start: 0}
    nodes_explored = 0
    while priority_queue:
        nodes_explored += 1
        cost, current_node, path = heapq.heappop(priority_queue)
        if current_node == goal:
            return path, cost, nodes_explored
        for neighbor, edge_dist, _ in campus_graph.get(current_node, []):
            new_cost = cost + edge_dist
            if neighbor not in visited_costs or new_cost < visited_costs[neighbor]:
                visited_costs[neighbor] = new_cost
                new_path = path + [neighbor]
                heapq.heappush(priority_queue, (new_cost, neighbor, new_path))
    return None, 0, nodes_explored

def euclidean_distance(node1, node2):
    """Calculates the Euclidean distance heuristic."""
    if node1 not in building_coords or node2 not in building_coords:
        return 0
    x1, y1 = building_coords[node1]
    x2, y2 = building_coords[node2]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def a_star(start, goal):
    """A* Search implementation with Euclidean distance heuristic."""
    print("Starting A* Search...")
    priority_queue = [(0 + euclidean_distance(start, goal), 0, start, [start])]
    visited_costs = {start: 0}
    nodes_explored = 0
    while priority_queue:
        nodes_explored += 1
        f_cost, g_cost, current_node, path = heapq.heappop(priority_queue)
        if current_node == goal:
            return path, g_cost, nodes_explored
        for neighbor, edge_dist, _ in campus_graph.get(current_node, []):
            new_g_cost = g_cost + edge_dist
            if neighbor not in visited_costs or new_g_cost < visited_costs[neighbor]:
                visited_costs[neighbor] = new_g_cost
                new_f_cost = new_g_cost + euclidean_distance(neighbor, goal)
                new_path = path + [neighbor]
                heapq.heappush(priority_queue, (new_f_cost, new_g_cost, neighbor, new_path))
    return None, 0, nodes_explored

# Map of algorithm names to their functions
algorithms = {
    'BFS': bfs,
    'DFS': dfs,
    'UCS': ucs,
    'A*': a_star
}

# ====================================================================
# 3. BASIC QUERY PROCESSING AND INFORMATION SERVICES
# ====================================================================

def show_path(path, distance):
    """Displays the found path and its details."""
    if path:
        print("\n--- Route Found! ---")
        print("Path: " + " -> ".join(path))
        print(f"Total Distance: {round(distance, 2)} meters")
        print(f"Estimated Walking Time: {calculate_time(distance)} minutes")

        print("\n--- Directions ---")
        for i in range(len(path)):
            location = path[i]
            if i < len(path) - 1:
                next_location = path[i+1]
                edge = next((edge_dist for neighbor, edge_dist, _ in campus_graph.get(location, []) if neighbor == next_location), None)
                if edge is not None:
                    print(f"  > From {location}, walk {edge} meters to {next_location}.")
                else:
                    print(f"  > From {location}, proceed to {next_location}.")

            if location in building_info:
                print(f"    - Note about {location}: {building_info[location]}")
        print("\n----------------------")
    else:
        print("\n--- No path found ---")
        print("Sorry, no path could be found between the selected locations.")

def run_query_loop():
    """Main interactive loop for the user."""
    while True:
        print("\n--- Campus Navigation Bot ---")
        print("Available locations:")
        # Display all primary and sub-locations for user guidance
        all_locations = sorted(list(campus_graph.keys()))
        print(", ".join(all_locations))

        start_location = input("Enter your starting location (or 'exit' to quit): ").strip().title()
        if start_location.lower() == 'exit':
            break

        goal_location = input("Enter your destination: ").strip().title()

        if start_location not in campus_graph or goal_location not in campus_graph:
            print("Invalid location. Please choose from the available list.")
            continue

        print("\nAvailable algorithms: BFS, DFS, UCS, A*")
        algorithm_choice = input("Choose a search algorithm: ").strip().upper()

        if algorithm_choice not in algorithms:
            print("Invalid algorithm choice. Please select from the list.")
            continue

        print(f"\nSearching for a path from {start_location} to {goal_location} using {algorithm_choice}...")

        path_finder = algorithms[algorithm_choice]
        path, distance, nodes_explored = path_finder(start_location, goal_location)

        show_path(path, distance)
        print(f"Search completed. Nodes explored: {nodes_explored}")

# ====================================================================
# MAIN EXECUTION
# ====================================================================
if __name__ == "__main__":
    # --- NEW FEATURE: WELCOME MESSAGE FOR NEW STUDENTS ---
    print("=====================================================")
    print("       Welcome to Chanakya University!")
    print("=====================================================")
    print("This campus navigation bot is here to help you get")
    print("familiar with your new surroundings.")
    print("You can find the quickest path between any two locations.")
    print("-----------------------------------------------------")
    
    while True:
        # --- MODIFIED: More interesting input prompt ---
        action = input("\nWhat's your next move? Enter 'navigate' to get directions, or 'exit' to finish: ").strip().lower()
        # --- END OF MODIFIED SECTION ---

        if action == 'navigate':
            run_query_loop()
        elif action == 'exit':
            break
        else:
            print("Invalid command.")
