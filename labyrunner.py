import pygame
import sys
import json
import random
from collections import deque

MOVE_DELAY = 1000 #ms
BUTTON_DELAY = 300
TILE_SIZE = 50
PLAYER_SIZE = 30
WINDOW_SIZE = (650, 650)

class Player:
    def __init__(self):
        #Player / Shadow appearances
        self.image = pygame.surface.Surface((TILE_SIZE - 20, TILE_SIZE - 20))
        self.image.fill((255,0,0))
        self.pos = (6*TILE_SIZE + 10, 6*TILE_SIZE + 10)
        self.shade = pygame.surface.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.shade.fill((57, 0, 138))
        #Movement Variables
        self.moving = False
        self.last_move_time = 0
        self.steering = False
        self.selected = False
        self.selected_point = (0,0)
        self.point_centre = pygame.math.Vector2((6,6))
        self.last_button_time = 0
        self.last_steering_time = 0
        self.closest_points = {"N": (0,0), "S": (0,0), "W": (0,0), "E": (0,0)}
        self.move_counter = 0



    def movable(self, player_pos, shadow_pos, mode): #mode = "player" oder "opp"
        if mode == "player":
            player_koord = (player_pos - pygame.math.Vector2(10,10)) / TILE_SIZE
            shadow_koord = (shadow_pos - pygame.math.Vector2(10,10)) / TILE_SIZE
        else:
            player_koord = player_pos
            shadow_koord = shadow_pos
        #print(player_koord, shadow_koord)
        sx = int(shadow_koord.x)
        sy = int(shadow_koord.y)
        px = int(player_koord.x)
        py = int(player_koord.y)
        if sx < px and sx >= 0:
            if game.vert_list[py][px] == "#":
                return True
            else:
                return False
        elif sx > px and sx <= 13 :
            if game.vert_list[py][px+1] == "#":
                return True
            else:
                return False
        elif sy < py and sy >= 0:
            if game.hor_list[py][px] == "#":
                return True
            else:
                return False
        elif sy > py and sy <= 13:
            if game.hor_list[py+1][px] == "#":
                return True
            else:
                return False
        else:
            return False

    def search_closest_points(self, centre):
        cdn = 1000 #closest distance north
        cds = 1000 
        cdw = 1000
        cde = 1000
        for x,y in game.point_list:
            distance = centre.distance_to((x,y))
            if distance != 0:
                if centre.y > y and distance < cdn: #wenn nördlich und kleinster abstand
                    self.closest_points["N"] = (x,y)
                    cdn = distance
                if centre.y < y and distance < cds: #wenn südlich und kleinster abstand
                    self.closest_points["S"] = (x,y)
                    cds = distance
                if centre.x > x and distance < cdw: #wenn westlich und kleinster abstand
                    self.closest_points["W"] = (x,y)
                    cdw = distance
                if centre.x < x and distance < cde: #wenn östlich und kleinster abstand
                    self.closest_points["E"] = (x,y) 
                    cde = distance 

    def move(self):
        keys = pygame.key.get_pressed()
        if pygame.joystick.get_count() > 0:
            x_move = game.controller.get_axis(0)
            y_move = game.controller.get_axis(1)
        else:
            x_move = 0
            y_move = 0
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_UP] or (y_move < -0.1 and abs(y_move) > abs(x_move)):
            self.temp_pos = self.pos + pygame.math.Vector2((0,-TILE_SIZE))
            self.moving = True
        elif keys[pygame.K_DOWN] or (y_move > 0.1 and y_move > abs(x_move)):
            self.temp_pos = self.pos + pygame.math.Vector2((0,TILE_SIZE))
            self.moving = True
        elif keys[pygame.K_LEFT] or (x_move < -0.1 and abs(x_move) >= abs(y_move)):
            self.temp_pos = self.pos + pygame.math.Vector2((-TILE_SIZE,0))
            self.moving = True
        elif keys[pygame.K_RIGHT] or (x_move > 0.1 and x_move >= abs(y_move)):
            self.temp_pos = self.pos + pygame.math.Vector2((TILE_SIZE,0))
            self.moving = True
        else:
            self.moving = False
        if current_time - self.last_move_time >= MOVE_DELAY and self.moving and self.movable(self.pos, self.temp_pos, "player"):
            self.pos = self.temp_pos
            self.last_move_time = current_time
            self.moving = False
            self.move_counter += 1

    def control_walls(self):
        keys = pygame.key.get_pressed()
        if pygame.joystick.get_count() > 0:
            x_move = game.controller.get_axis(2)
            y_move = game.controller.get_axis(3)
            cb = game.controller.get_button(10)

        else:
            x_move = 0
            y_move = 0
            cb = False
        current_time = pygame.time.get_ticks()
        if not self.selected:
            self.search_closest_points(self.point_centre)
            temp_centre = (0,0)
            if keys[pygame.K_w] or (y_move < -0.1 and abs(y_move) > abs(x_move)):
                temp_centre = self.closest_points["N"]
            elif keys[pygame.K_s] or (y_move > 0.1 and y_move > abs(x_move)):
                temp_centre = self.closest_points["S"]
            elif keys[pygame.K_a] or (x_move < -0.1 and abs(x_move) >= abs(y_move)):
                temp_centre = self.closest_points["W"]
            elif keys[pygame.K_d] or (x_move > 0.1 and x_move >= abs(y_move)):
                temp_centre = self.closest_points["E"]

            if current_time - self.last_steering_time >= MOVE_DELAY and temp_centre != (0,0):
                if self.selected_point != (0,0):
                    game.point_list[self.selected_point] = (game.point_list[self.selected_point][0], 0)
                self.selected_point = temp_centre
                self.point_centre = pygame.math.Vector2(temp_centre)
                self.last_steering_time = current_time
                game.point_list[self.selected_point] = (game.point_list[self.selected_point][0], 1)

            if (cb or keys[pygame.K_SPACE]) and current_time - self.last_button_time >= BUTTON_DELAY and self.selected_point != (0,0):
                self.selected = True
                self.last_button_time = current_time

        else:
            x = self.selected_point[0]
            y = self.selected_point[1]
            if keys[pygame.K_w] or (y_move < -0.1 and abs(y_move) > abs(x_move)) or keys[pygame.K_s] or (y_move > 0.1 and y_move > abs(x_move)):
                if game.point_list[self.selected_point][0] == 1:
                    game.hor_list[y] = game.hor_list[y][0:x-1:1] + "##" + game.hor_list[y][x+1::1]
                    game.vert_list[y-1] = game.vert_list[y-1][0:x:1] + "m" + game.vert_list[y-1][x+1::1]
                    game.vert_list[y] = game.vert_list[y][0:x:1] + "m" + game.vert_list[y][x+1::1]
                    game.point_list[self.selected_point] = (0,1)
            elif keys[pygame.K_a] or (x_move < -0.1 and abs(x_move) >= abs(y_move)) or keys[pygame.K_d] or (x_move > 0.1 and x_move >= abs(y_move)):
                if game.point_list[self.selected_point][0] == 0:
                    game.hor_list[y] = game.hor_list[y][0:x-1:1] + "mm" + game.hor_list[y][x+1::1]
                    game.vert_list[y-1] = game.vert_list[y-1][0:x:1] + "#" + game.vert_list[y-1][x+1::1]
                    game.vert_list[y] = game.vert_list[y][0:x:1] + "#" + game.vert_list[y][x+1::1]
                    game.point_list[self.selected_point] = (1,1)

            if (cb or keys[pygame.K_SPACE]) and current_time - self.last_button_time >= BUTTON_DELAY:
                self.selected = False
                self.last_button_time = current_time
                self.move_counter += 1

class Opponents():
    def __init__(self):
        self.opp_positions = [[0,0],[0,0],[0,0]]
        #random opponent positions
        for i in range (3):
            for e in range (2):
                self.opp_positions[i][e] = random.randint(0,12)
        #Appearance
        self.opp_image = pygame.surface.Surface((TILE_SIZE - 30, TILE_SIZE - 30))
        self.opp_image.fill("gray")
        self.screen = game.screen #pygame.display.get_surface()
        self.shortest_paths = [[], [], []]
        self.last_move_time = 0

    def draw(self):
        for i in range (3):
            pos = ((self.opp_positions[i][0] * TILE_SIZE + 15), (self.opp_positions[i][1] * TILE_SIZE + 15))
            self.screen.blit(self.opp_image, pos)

    def move(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= MOVE_DELAY * 0.75:
            for i in range (3):
                self.opp_positions[i] = self.shortest_paths[i][0]
                self.shortest_paths[i].pop(0)
                self.last_move_time = current_time


class Game():
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        #open data.json
        with open('data/data.json', 'r') as file:
            self.data = json.load(file)

        # Check for connected controllers
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            print(f"Controller verbunden: {self.controller.get_name()}")

        #Environment
        pygame.display.set_caption("LabyRunner")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.running = True
        self.clock = pygame.time.Clock()
        
        #Orientation Variables
        self.vert_list = []
        self.hor_list = []
        self.point_list = {}
        self.make_hor_list()
        self.make_vert_list()
        self.make_point_list()
        self.finish_list = [[0,0], [0,12], [12,0], [12,12]]

    def make_vert_list(self):
        lines = self.data["grid"][1::2]
        for line in lines:
            str_line = "".join(list(line)[0::2])
            self.vert_list.append(str_line)

    def make_hor_list(self):
        lines = self.data["grid"][0::2]
        for line in lines:
            str_line = "".join(list(line)[1::2])
            self.hor_list.append(str_line)

    def make_point_list(self):
        lines = self.data["grid"][0::2]
        for line in lines:
            elems = list(line)[0::2]
            for i in range (len(elems)):
                x = i
                y = lines.index(line)
                if elems[i] == "p":
                    if self.hor_list[y][x-1] == "m" and self.hor_list[y][x] == "m":
                        self.point_list[(x,y)] = (1,0) #1 für horizontal, 0 für nicht ausgewählt
                    else:
                        self.point_list[(x,y)] = (0,0) #0 für vertikal
            
    def paint_walls(self):
        #horizontale Wände
        for u in range (len(self.hor_list)):
            line = self.hor_list[u]
            for i in range (len(line)):
                x = i
                y = u
                if line[i] == "w":
                    pygame.draw.line(self.screen, "white", (x * TILE_SIZE, y * TILE_SIZE), ((x+1) * TILE_SIZE, y * TILE_SIZE), width=5)
                elif line[i] == "m":
                    pygame.draw.line(self.screen, (210, 255, 0), (x * TILE_SIZE, y * TILE_SIZE), ((x+1) * TILE_SIZE, y * TILE_SIZE), width=5)
        #vertikale Wände
        for u in range(len(self.vert_list)):
            line = self.vert_list[u]
            for i in range (len(line)):
                x = i
                y = u
                if line[i] == "w":
                    pygame.draw.line(self.screen, "white", (x * TILE_SIZE, y * TILE_SIZE), (x * TILE_SIZE, (y+1) * TILE_SIZE), width=5)
                elif line[i] == "m":
                    pygame.draw.line(self.screen, (210, 255, 0), (x * TILE_SIZE, y * TILE_SIZE), (x * TILE_SIZE, (y+1) * TILE_SIZE), width=5)
        for v in self.finish_list:
            pygame.draw.rect(self.screen, "green", (v[0] * TILE_SIZE, v[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE), width=0)
        #punkte zeichnen
        for x,y in self.point_list:
            if self.point_list[(x,y)][1] == 0: #nicht ausgewählt
                pygame.draw.circle(self.screen, (26, 255, 0), (x * TILE_SIZE, y * TILE_SIZE), 5)
            else:
                pygame.draw.circle(self.screen, (200, 0, 0), (x * TILE_SIZE, y * TILE_SIZE), 5)

    def bfs(self, opp_num):    #bfs format: [([6,7 #pos], [[0,0],[0,1],[1,1],...#path), ...(#nächster Weg)]
        queue = deque([(self.opp.opp_positions[opp_num], [])])
        player_pos = [int((self.player.pos[0] - 10) // TILE_SIZE), int((self.player.pos[1] - 10) // TILE_SIZE)]
        visited = []
        while True:
            pos, path = queue.popleft()
            v = pygame.math.Vector2(pos)
            if pos not in visited:
                np = path
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if self.player.movable(v, v + (dx, dy), "opp") and [v.x + dx, v.y + dy] not in visited:
                        queue.append(([int(v.x) + dx, int(v.y) + dy], np + [pos]))
                    if pos == player_pos:
                        self.opp.shortest_paths[opp_num] = (np + [pos])[1:]
                        return
                visited.append(pos)
                         

            #else:
                #self.opp.shortest_paths[opp_num] = [self.opp.opp_positions[opp_num]]
                #break

    def update_opp(self):
        for i in range(3):
            self.bfs(i)
        #print(self.opp.shortest_paths)

    def run(self):
        #self.paint_walls()
        self.player = Player()
        self.opp = Opponents()
        self.update_opp()
        while self.running:
            self.screen.fill((0,0,100))
            self.player.control_walls()
            self.paint_walls()
            #pygame.draw.rect(self.screen, (125,75,45), self.wall)
            self.screen.blit(self.player.image, self.player.pos)
            self.player.move()
            player_pos = [(self.player.pos[0] - 10) / TILE_SIZE, (self.player.pos[1] - 10) / TILE_SIZE]
            if player_pos in self.finish_list:
                print("Du hast gewonnen.")
                running = False
                pygame.quit()
                sys.exit()
            if self.player.move_counter == 1:
                self.player.move_counter = 0
                self.update_opp()
            self.opp.move()
            if player_pos in self.opp.opp_positions:
                print("Du hast verloren.")
                running = False
                pygame.quit()
                sys.exit()
            self.opp.draw()
            if self.player.moving and self.player.movable(self.player.pos, self.player.temp_pos, "player"):
                self.screen.blit(self.player.shade, self.player.temp_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)

game = Game()
game.run()
