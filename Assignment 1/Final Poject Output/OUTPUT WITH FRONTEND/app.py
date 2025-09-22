import collections
import heapq
import math
from flask import Flask, jsonify, request, render_template

# ====================================================================
# 1. CAMPUS GEOMETRY AND DATA
# =====================================================================

# This graph defines all the locations and connections on the campus.
# Each key is a point, and its value is a list of its neighbors.
# The tuples are (destination_node, distance_in_meters, speed_factor).
campus_graph = {
    'Entry Gate': [('Security Gate', 200, 1.0)],
    'Exit Gate': [('Security Gate', 170, 1.0)],
    'Security Gate': [
        ('Entry Gate', 200, 1.0),
        ('Exit Gate', 170, 1.0),
        ('Flag Post', 60, 1.0)
    ],
    'Flag Post': [('Security Gate', 60, 1.0), ('Academic Block 1 Entrance', 220, 1.0)],
    
    # Internal nodes for Academic Block 1.
    'Academic Block 1 Entrance': [
        ('Flag Post', 220, 1.0),
        ('Lawn Area', 130, 1.0),
        ('Library', 5, 1.0),
        ('Auditorium', 10, 1.0),
        ('Admissions', 55, 1.0),
        ('Registrar Office', 70, 1.0),
        ('Cafeteria', 15, 1.0)
    ],
    'Library': [
        ('Academic Block 1 Entrance', 5, 1.0),
        ('Auditorium', 20, 1.0)
    ],
    'Auditorium': [
        ('Academic Block 1 Entrance', 10, 1.0),
        ('Library', 20, 1.0),
        ('Cafeteria', 25, 1.0)
    ],
    'Admissions': [('Academic Block 1 Entrance', 55, 1.0)],
    'Registrar Office': [
        ('Academic Block 1 Entrance', 70, 1.0),
        ('Finance Dept', 12, 1.0)
    ],
    'Finance Dept': [
        ('Registrar Office', 12, 1.0),
        ('Academic Block 1 Entrance', 80, 1.0)
    ],
    'Cafeteria': [
        ('Academic Block 1 Entrance', 15, 1.0),
        ('Academic Block 2', 60, 1.0),
        ('Auditorium', 25, 1.0)
    ],

    # The rest of the external campus locations.
    'Lawn Area': [('Academic Block 1 Entrance', 130, 1.0), ('Academic Block 2', 150, 1.0)],
    'Academic Block 2': [('Lawn Area', 150, 1.0), ('Cafeteria', 60, 1.0), ('Food Court', 250, 1.0), ('Hostel Building 2', 45, 1.0)],
    'Hostel Building 2': [('Academic Block 2', 45, 1.0), ('Hostel Building 1', 250, 1.0), ('Food Court', 55, 1.0)],
    'Food Court': [('Academic Block 2', 250, 1.0), ('Hostel Building 1', 130, 1.0)],
    'Hostel Building 1': [('Hostel Building 2', 250, 1.0), ('Food Court', 130, 1.0), ('Exit Gate', 420, 1.0)],
}

# Co-ordinates for A* search, now mirrored on the x-axis.
building_coords = {
    'Entry Gate': (0, -180),
    'Exit Gate': (-360, -180),
    'Security Gate': (-180, 0),
    'Flag Post': (-180, 50),
    'Academic Block 1 Entrance': (-180, 260),
    'Library': (-170, 260),
    'Auditorium': (-180, 260),
    'Admissions': (-180, 310),
    'Registrar Office': (-180, 320),
    'Finance Dept': (-190, 320),
    'Cafeteria': (-190, 260),
    'Lawn Area': (-180, 400),
    'Academic Block 2': (-180, 540),
    'Food Court': (-420, 540),
    'Hostel Building 1': (-660, 700),
    'Hostel Building 2': (-230, 600)
}

# Short descriptions for each location.
building_info = {
    'Entry Gate': "Main campus entry point, on the right.",
    'Exit Gate': "Main campus exit point, on the left.",
    'Security Gate': "The central security checkpoint for all campus traffic.",
    'Flag Post': "The campus flag post.",
    'Academic Block 1 Entrance': "Main entrance to Academic Block 1, which houses several internal departments.",
    'Library': "Located inside Academic Block 1 with easy access to the Auditorium.",
    'Auditorium': "Found on the lower ground floor of Academic Block 1.",
    'Admissions': "The Admissions office, located on the 1st floor of Academic Block 1.",
    'Registrar Office': "The Registrar's Office on the 3rd floor of Academic Block 1.",
    'Finance Dept': "The Finance Department, adjacent to the Registrar's Office.",
    'Cafeteria': "An on-campus cafeteria with connections to Academic Block 2 and the Auditorium.",
    'Academic Block 2': "A secondary academic hub in the northern part of the campus.",
    'Lawn Area': "A large open lawn area.",
    'Hostel Building 2': "One of the two main residential buildings.",
    'Food Court': "The main campus food court.",
    'Hostel Building 1': "One of the main residential buildings.",
}

# Average walking speed.
WALKING_SPEED_MPS = 1.35  # Slightly adjusted speed.

def calculate_time(distance):
    """Calculates estimated walking time in minutes based on distance."""
    time_seconds = distance / WALKING_SPEED_MPS
    return round(time_seconds / 60, 2)


# ====================================================================
# 2. PATHFINDING ALGORITHMS
# ====================================================================

def bfs(start, goal):
    """Breadth-First Search (BFS) explores the graph layer by layer."""
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
    """Depth-First Search (DFS) dives deep into a single path first."""
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
    """Uniform Cost Search (UCS) finds the path with the lowest total cost."""
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
    """Calculates a straight-line distance, used as a heuristic for A*."""
    if node1 not in building_coords or node2 not in building_coords:
        return 0
    x1, y1 = building_coords[node1]
    x2, y2 = building_coords[node2]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def a_star(start, goal):
    """A* Search combines cost with a heuristic for efficient pathfinding."""
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

algorithms = {
    'BFS': bfs, 'DFS': dfs, 'UCS': ucs, 'A*': a_star
}

# ====================================================================
# 3. FLASK APPLICATION AND API ENDPOINTS
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
    
    # Flip the y-coordinates for Leaflet's simple CRS
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
    print("          Campus Navigation System Backend           ")
    print("=====================================================")
    app.run(debug=True)
