# app.py

import collections
import heapq
import math
from flask import Flask, jsonify, request, render_template

# ====================================================================
# 1. CAMPUS ENVIRONMENT MODELING
# =====================================================================

# Our main campus map. Each spot (key) links to other places (value)
# The value is a list of tuples: (neighbour, distance in meters, speed_factor)
campus_graph = {
    # Entry Gate is only for entering. One way traffic, you know.
    'Entry Gate': [('Security Gate', 180, 1.0)],

    # Exit Gate is only for exiting. No entry from here.
    'Exit Gate': [('Security Gate', 180, 1.0)],

    # Security Gate is the main checkpoint. Sab kuch yahi se control hota hai.
    'Security Gate': [
        ('Entry Gate', 180, 1.0),
        ('Exit Gate', 180, 1.0),
        ('Flag Post', 50, 1.0)
    ],
    'Flag Post': [('Security Gate', 50, 1.0), ('Academic Block 1 Entrance', 210, 1.0)],

    # NEW INTERNAL NODES FOR ACADEMIC BLOCK 1
    # Academic Block 1 - our main hub. So many places inside this one building!
    'Academic Block 1 Entrance': [
        ('Flag Post', 210, 1.0),
        ('Lawn Area', 140, 1.0),
        # Distances are 0 because they are inside the same building.
        ('Library', 0, 1.0),
        ('Auditorium', 0, 1.0),
        ('Admissions', 50, 1.0),
        ('Registrar Office', 60, 1.0),
        ('Cafeteria', 10, 1.0)
    ],
    # Direct connect to Auditorium for quick access. Super convenient!
    'Library': [
        ('Academic Block 1 Entrance', 0, 1.0),
        ('Auditorium', 15, 1.0)
    ],
    'Auditorium': [
        ('Academic Block 1 Entrance', 0, 1.0),
        ('Library', 15, 1.0),
        ('Cafeteria', 20, 1.0)
    ],
    'Admissions': [('Academic Block 1 Entrance', 50, 1.0)],
    'Registrar Office': [
        ('Academic Block 1 Entrance', 60, 1.0),
        ('Finance Dept', 10, 1.0)
    ],
    'Finance Dept': [
        ('Registrar Office', 10, 1.0),
        ('Academic Block 1 Entrance', 70, 1.0)
    ],
    'Cafeteria': [
        ('Academic Block 1 Entrance', 10, 1.0),
        ('Academic Block 2', 50, 1.0),
        ('Auditorium', 20, 1.0)
    ],

    # REMAINING EXTERNAL NODES
    # Remaining locations outside the main block.
    'Lawn Area': [('Academic Block 1 Entrance', 140, 1.0), ('Academic Block 2', 140, 1.0)],
    'Academic Block 2': [('Lawn Area', 140, 1.0), ('Cafeteria', 50, 1.0), ('Food Court', 240, 1.0), ('Hostel Building 2', 50, 1.0)],
    'Hostel Building 2': [('Academic Block 2', 50, 1.0), ('Hostel Building 1', 240, 1.0), ('Food Court', 50, 1.0)],
    'Food Court': [('Academic Block 2', 240, 1.0), ('Hostel Building 1', 120, 1.0)],
    # Hostel to Exit Gate because everyone must exit from there.
    'Hostel Building 1': [('Hostel Building 2', 240, 1.0), ('Food Court', 120, 1.0), ('Exit Gate', 400, 1.0)],
}

# Co-ordinates for our A* search.
building_coords = {
    'Entry Gate': (0, -180),
    'Exit Gate': (360, -180),
    'Security Gate': (180, 0),
    'Flag Post': (180, 50),
    'Academic Block 1 Entrance': (180, 260),
    'Library': (170, 260),
    'Auditorium': (180, 260),
    'Admissions': (180, 310),
    'Registrar Office': (180, 320),
    'Finance Dept': (190, 320),
    'Cafeteria': (190, 260),
    'Lawn Area': (180, 400),
    'Academic Block 2': (180, 540),
    'Food Court': (420, 540),
    'Hostel Building 1': (660, 700),
    'Hostel Building 2': (230, 600)
}

# A small dictionary with notes on each building.
building_info = {
    'Entry Gate': "Main Entry Gate (A), on the right side of the main road.",
    'Exit Gate': "Main Exit Gate (B), on the left side of the main road.",
    'Security Gate': "Security Gate (C), the central checkpoint for all entry and exit from the campus.",
    'Flag Post': "Campus Flag Post (D).",
    'Academic Block 1 Entrance': "Main Entrance to Academic Block 1. This building is multi-story with lifts on both sides. The following internal locations can be found here.",
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
}

# This is our walking speed, 1.4 meters per second. Thoda fast-fast chalenge.
WALKING_SPEED_MPS = 1.4

def calculate_time(distance):
    """Calculates walking time in minutes. Simple calculation, nothing too fancy."""
    time_seconds = distance / WALKING_SPEED_MPS
    return round(time_seconds / 60, 2)


# 2. SEARCH ALGORITHM IMPLEMENTATIONS


def bfs(start, goal):
    """BFS: breadth-first search. It's like exploring layer by layer, starting from the closest nodes."""
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
    """DFS: depth-first search. It goes deep into one path first, like a narrow lane."""
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
        for neighbor, edge_dist, _ in reversed(campus_graph.get(current_node, [])):
            if neighbor not in visited:
                new_path = path + [neighbor]
                new_distance = distance + edge_dist
                stack.append((neighbor, new_path, new_distance))
    return None, 0, nodes_explored

def ucs(start, goal):
    """UCS: Uniform Cost Search. Finds the cheapest path. Not about distance, but total cost."""
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
    """This is our A* heuristic. It estimates distance in a straight line, like a bird's flight path.
    Helps A* to be super smart."""
    if node1 not in building_coords or node2 not in building_coords:
        return 0
    x1, y1 = building_coords[node1]
    x2, y2 = building_coords[node2]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def a_star(start, goal):
    """A* Search: The best one! It combines path cost and heuristic to find the fastest way. Like a smart student."""
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

# A simple dictionary to map algorithm names to functions.
algorithms = {
    'BFS': bfs,
    'DFS': dfs,
    'UCS': ucs,
    'A*': a_star
}

# ====================================================================
# 3. WEB APP ROUTES AND API ENDPOINTS
# ====================================================================

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/navigate', methods=['POST'])
def api_navigate():
    data = request.json
    start_location = data.get('start')
    goal_location = data.get('goal')
    algorithm = data.get('algorithm')

    if not all([start_location, goal_location, algorithm]):
        return jsonify({"error": "Missing parameters"}), 400

    path_finder = algorithms.get(algorithm)
    if not path_finder:
        return jsonify({"error": "Invalid algorithm"}), 400

    path, distance, nodes_explored = path_finder(start_location, goal_location)

    if not path:
        return jsonify({"error": "No path found"}), 404

    path_coords = [building_coords[loc] for loc in path if loc in building_coords]
    
    # We will flip the y-coordinates for Leaflet's simple CRS
    flipped_coords = [(x, -y) for x, y in path_coords]

    directions = []
    for i in range(len(path) - 1):
        location = path[i]
        next_location = path[i+1]
        edge = next((edge_dist for neighbor, edge_dist, _ in campus_graph.get(location, []) if neighbor == next_location), None)
        if edge is not None:
            directions.append(f"From {location}, walk {edge} meters to {next_location}.")
        else:
            directions.append(f"From {location}, proceed to {next_location}.")

    return jsonify({
        "path": path,
        "path_coords": flipped_coords,
        "distance": round(distance, 2),
        "time": calculate_time(distance),
        "nodes_explored": nodes_explored,
        "directions": directions
    })

@app.route('/api/buildings')
def api_buildings():
    buildings = []
    for name, coords in building_coords.items():
        buildings.append({
            "name": name,
            "coords": [coords[0], -coords[1]],
            "info": building_info.get(name, "No info available.")
        })
    return jsonify(buildings)

if __name__ == "__main__":
    print("=====================================================")
    print("       Welcome to Chanakya University! 🎓")
    print("=====================================================")
    print("This server provides the backend for the campus navigation bot.")
    print("Open your browser and navigate to http://127.0.0.1:5000")
    print("-----------------------------------------------------")
    app.run(debug=True)
