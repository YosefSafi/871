import random
import math
import heapq

WIDTH = 60
HEIGHT = 30
WALL = 1
FLOOR = 0
FOG = 2
FOV_RADIUS = 8

class GameState:
    def __init__(self):
        self.map = self.generate_map()
        self.player = {"x": 5, "y": 5, "hp": 20, "max_hp": 20}
        self.place_player()
        self.enemies = []
        self.spawn_enemies(15)
        self.logs = ["Welcome to the Labyrinth of Despair."]
        self.visible_map = [[FOG for _ in range(HEIGHT)] for _ in range(WIDTH)]
        self.update_fov()

    def generate_map(self):
        # 1. Random noise
        grid = [[random.choice([WALL, WALL, WALL, FLOOR, FLOOR, FLOOR]) for _ in range(HEIGHT)] for _ in range(WIDTH)]
        
        # 2. Cellular Automata
        for _ in range(5):
            new_grid = [[WALL for _ in range(HEIGHT)] for _ in range(WIDTH)]
            for x in range(1, WIDTH - 1):
                for y in range(1, HEIGHT - 1):
                    walls = sum([grid[x+i][y+j] == WALL for i in [-1,0,1] for j in [-1,0,1]])
                    if walls >= 5:
                        new_grid[x][y] = WALL
                    else:
                        new_grid[x][y] = FLOOR
            grid = new_grid

        # Add borders
        for x in range(WIDTH):
            grid[x][0] = WALL
            grid[x][HEIGHT-1] = WALL
        for y in range(HEIGHT):
            grid[0][y] = WALL
            grid[WIDTH-1][y] = WALL

        return grid

    def place_player(self):
        # Find a large open area for the player
        for x in range(5, WIDTH-5):
            for y in range(5, HEIGHT-5):
                if self.map[x][y] == FLOOR and self.map[x+1][y] == FLOOR and self.map[x][y+1] == FLOOR:
                    self.player["x"] = x
                    self.player["y"] = y
                    return

    def spawn_enemies(self, count):
        for _ in range(count):
            placed = False
            while not placed:
                x = random.randint(1, WIDTH-2)
                y = random.randint(1, HEIGHT-2)
                if self.map[x][y] == FLOOR and math.dist((x,y), (self.player["x"], self.player["y"])) > 15:
                    # Some have more HP
                    hp = random.choice([5, 5, 8, 12])
                    self.enemies.append({"x": x, "y": y, "hp": hp, "max_hp": hp, "type": "stalker"})
                    placed = True

    def log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 6:
            self.logs.pop(0)

    def calculate_fov(self):
        # Reset visibility
        self.visible_map = [[FOG for _ in range(HEIGHT)] for _ in range(WIDTH)]
        px, py = self.player["x"], self.player["y"]
        
        # Simple Raycasting
        for angle in range(0, 360, 2):
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            
            cx, cy = float(px), float(py)
            for i in range(FOV_RADIUS):
                tx, ty = int(round(cx)), int(round(cy))
                if tx < 0 or tx >= WIDTH or ty < 0 or ty >= HEIGHT:
                    break
                self.visible_map[tx][ty] = self.map[tx][ty]
                if self.map[tx][ty] == WALL:
                    break
                cx += dx
                cy += dy

    def update_fov(self):
        self.calculate_fov()

    def astar_path(self, start, goal):
        # A* algorithm for enemies
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                break

            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nxt = (current[0] + dx, current[1] + dy)
                if 0 <= nxt[0] < WIDTH and 0 <= nxt[1] < HEIGHT and self.map[nxt[0]][nxt[1]] == FLOOR:
                    new_cost = cost_so_far[current] + 1
                    if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                        cost_so_far[nxt] = new_cost
                        priority = new_cost + heuristic(goal, nxt)
                        heapq.heappush(frontier, (priority, nxt))
                        came_from[nxt] = current

        # Reconstruct path
        if goal not in came_from:
            return None # No path found
            
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def move_player(self, dx, dy):
        if self.player["hp"] <= 0: return

        nx, ny = self.player["x"] + dx, self.player["y"] + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and self.map[nx][ny] == FLOOR:
            # Check attack
            hit_enemy = None
            for e in self.enemies:
                if e["x"] == nx and e["y"] == ny:
                    hit_enemy = e
                    break
            
            if hit_enemy:
                damage = random.randint(3, 6)
                hit_enemy["hp"] -= damage
                self.log(f"You struck enemy for {damage} dmg! (HP: {hit_enemy['hp']}/{hit_enemy['max_hp']})")
                if hit_enemy["hp"] <= 0:
                    self.enemies.remove(hit_enemy)
                    self.log("[+] Enemy slain!")
                    self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + 2) # Heal on kill
            else:
                self.player["x"] = nx
                self.player["y"] = ny
        self.update_fov()

    def process_turn(self):
        if self.player["hp"] <= 0: return

        px, py = self.player["x"], self.player["y"]
        for e in self.enemies:
            # Only aggro if player is relatively close
            if math.dist((e["x"], e["y"]), (px, py)) < 12:
                # Use A* to find path
                path = self.astar_path((e["x"], e["y"]), (px, py))
                if path:
                    nxt = path[0] # Next step
                    if nxt == (px, py):
                        # Attack
                        dmg = random.randint(1, 3)
                        self.player["hp"] -= dmg
                        self.log(f"Enemy bites you for {dmg} dmg!")
                    else:
                        # Move, but avoid other enemies
                        collision = any([other["x"] == nxt[0] and other["y"] == nxt[1] for other in self.enemies])
                        if not collision:
                            e["x"] = nxt[0]
                            e["y"] = nxt[1]

        if self.player["hp"] <= 0:
            self.log(">>> YOU HAVE DIED in the Labyrinth. <<<")

    def get_state(self):
        # Only send visible enemies
        visible_enemies = [
            e for e in self.enemies 
            if self.visible_map[e["x"]][e["y"]] != FOG
        ]

        return {
            "player": self.player,
            "map": self.visible_map, # Send the obscured map!
            "enemies": visible_enemies,
            "logs": self.logs,
            "width": WIDTH,
            "height": HEIGHT
        }
