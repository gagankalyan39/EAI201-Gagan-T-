import heapq
import math

class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.n = len(maze)
        self.m = len(maze[0])
        self.start_pos = None
        self.goal_pos = None

        # Locate S and G in the grid
        for r in range(self.n):
            for c in range(self.m):
                if maze[r][c] == "S":
                    self.start_pos = (r, c)
                elif maze[r][c] == "G":
                    self.goal_pos = (r, c)

        if not self.start_pos or not self.goal_pos:
            raise ValueError("Maze must contain 'S' and 'G'")

    def estimate(self, node, method="manhattan"):
        x1, y1 = node
        x2, y2 = self.goal_pos
        if method == "manhattan":
            return abs(x1 - x2) + abs(y1 - y2)
        elif method == "euclidean":
            return math.hypot(x1 - x2, y1 - y2)
        elif method == "diagonal":
            return max(abs(x1 - x2), abs(y1 - y2))
        else:
            raise ValueError("Unknown heuristic")

    def neighbors(self, node):
        r, c = node
        moves = [(1,0), (-1,0), (0,1), (0,-1)]
        result = []
        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.n and 0 <= nc < self.m and self.maze[nr][nc] != "1":
                result.append((nr, nc))
        return result

    def greedy(self, method="manhattan"):
        pq = [(0, self.start_pos)]
        parent = {}
        seen = {self.start_pos}
        explored = 0

        while pq:
            _, cur = heapq.heappop(pq)
            explored += 1

            if cur == self.goal_pos:
                return self.rebuild(parent), explored

            for nxt in self.neighbors(cur):
                if nxt not in seen:
                    seen.add(nxt)
                    parent[nxt] = cur
                    heapq.heappush(pq, (self.estimate(nxt, method), nxt))

        return None, explored

    def a_star(self, method="manhattan"):
        pq = [(0, self.start_pos)]
        parent = {}
        g = {self.start_pos: 0}
        f = {self.start_pos: self.estimate(self.start_pos, method)}
        explored = 0

        while pq:
            _, cur = heapq.heappop(pq)
            explored += 1

            if cur == self.goal_pos:
                return self.rebuild(parent), explored

            for nxt in self.neighbors(cur):
                tentative = g[cur] + 1
                if nxt not in g or tentative < g[nxt]:
                    parent[nxt] = cur
                    g[nxt] = tentative
                    f[nxt] = tentative + self.estimate(nxt, method)
                    heapq.heappush(pq, (f[nxt], nxt))

        return None, explored

    def rebuild(self, parent):
        node = self.goal_pos
        path = [node]
        while node != self.start_pos:
            node = parent[node]
            path.append(node)
        return list(reversed(path))

    def report(self, algo, method, path, explored):
        length = len(path) - 1 if path else "N/A"
        print(f"{algo} with {method} heuristic:")
        print(f"  Path length: {length}")
        print(f"  Nodes explored: {explored}")
        if path:
            print(f"  Path: {path}")
        else:
            print("  No path found")
        print()

maze = [
    ['S','0','1','0','0','0'],
    ['0','1','0','1','1','0'],
    ['0','0','0','0','1','0'],
    ['1','1','0','1','0','0'],
    ['0','0','0','1','0','1'],
    ['0','1','0','0','G','0']
]
print("The Maze = ")
for row in maze:
    print(" ".join(row))

solver = MazeSolver(maze)

heuristics = ["manhattan", "euclidean", "diagonal"]

for h in heuristics:
    p, e = solver.greedy(h)
    solver.report("Greedy Best-First", h, p, e)

for h in heuristics:
    p, e = solver.a_star(h)
    solver.report("A*", h, p, e)
