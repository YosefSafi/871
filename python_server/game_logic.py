import random
import math

WIDTH = 60
HEIGHT = 30
WALL = 1
FLOOR = 0

class GameState:
    def __init__(self):
        self.map = self.generate_map()
        self.player = {"x": 5, "y": 5, "hp": 20, "max_hp": 20}
        self.place_player()
        self.enemies = []
        self.spawn_enemies(10)
        self.logs = ["Welcome to the Labyrinth of Despair."]

    def generate_map(self):
        # 1. Random noise
        grid = [[random.choice([WALL, WALL, WALL, FLOOR, FLOOR]) for _ in range(HEIGHT)] for _ in range(WIDTH)]
        
        # 2. Cellular Automata rules
        for _ in range(4):
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
        for x in range(1, WIDTH):
            for y in range(1, HEIGHT):
                if self.map[x][y] == FLOOR:
                    self.player["x"] = x
                    self.player["y"] = y
                    return

    def spawn_enemies(self, count):
        for _ in range(count):
            placed = False
            while not placed:
                x = random.randint(1, WIDTH-2)
                y = random.randint(1, HEIGHT-2)
                # Don't spawn on walls or too close to player
                if self.map[x][y] == FLOOR and abs(x - self.player["x"]) > 10 and abs(y - self.player["y"]) > 10:
                    self.enemies.append({"x": x, "y": y, "hp": 5, "type": "stalker"})
                    placed = True

    def log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 5:
            self.logs.pop(0)

    def move_player(self, dx, dy):
        nx, ny = self.player["x"] + dx, self.player["y"] + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and self.map[nx][ny] == FLOOR:
            # Check for enemy
            hit_enemy = None
            for e in self.enemies:
                if e["x"] == nx and e["y"] == ny:
                    hit_enemy = e
                    break
            
            if hit_enemy:
                hit_enemy["hp"] -= 2
                self.log(f"You hit the enemy! Enemy HP: {hit_enemy['hp']}")
                if hit_enemy["hp"] <= 0:
                    self.enemies.remove(hit_enemy)
                    self.log("Enemy defeated!")
            else:
                self.player["x"] = nx
                self.player["y"] = ny

    def process_turn(self):
        # Extremely basic greedy pathfinding for Swarming
        px, py = self.player["x"], self.player["y"]
        for e in self.enemies:
            dx = 1 if px > e["x"] else -1 if px < e["x"] else 0
            dy = 1 if py > e["y"] else -1 if py < e["y"] else 0
            
            nx, ny = e["x"] + dx, e["y"] + dy
            
            # If adjacent to player, attack instead of move
            if nx == px and ny == py:
                self.player["hp"] -= 1
                self.log("Enemy hit you! HP -1.")
            elif 0 <= nx < WIDTH and 0 <= ny < HEIGHT and self.map[nx][ny] == FLOOR:
                # Basic collision avoidance with other enemies
                collision = any([other["x"] == nx and other["y"] == ny for other in self.enemies])
                if not collision:
                    e["x"] = nx
                    e["y"] = ny
        
        if self.player["hp"] <= 0:
            self.log("YOU DIED.")

    def get_state(self):
        return {
            "player": self.player,
            "map": self.map,
            "enemies": self.enemies,
            "logs": self.logs,
            "width": WIDTH,
            "height": HEIGHT
        }
