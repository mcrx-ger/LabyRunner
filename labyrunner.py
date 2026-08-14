import pygame
import sys
import json
import random
from collections import deque
import math

MOVE_DELAY = 1000 #ms
BUTTON_DELAY = 500
RADAR_DELAY = 5000
TILE_SIZE = 50
PLAYER_SIZE = 30
WINDOW_SIZE = 650

class Player:
    def __init__(self):
        #Player / Shadow appearances
        #self.image = pygame.image.load("data/images/player.png")
        self.image = pygame.surface.Surface((PLAYER_SIZE, PLAYER_SIZE))
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

    def search_closest_point(self, vec_centre, x_c, y_c):
        vec_controller = pygame.math.Vector2(x_c, y_c)
        point_acc_list = {}
        max_dist = 0
        max_acc = (0,0)

        for x_p,y_p in game.point_list:
            if (x_p,y_p) != self.selected_point:
                vec_point = pygame.math.Vector2(x_p, y_p) - vec_centre
                f = vec_point.dot(vec_controller) / (vec_point.length() * vec_controller.length())
                deg = math.degrees(math.acos(round(f, 8)))
                deg_acc = (180 - deg) / 180
                distance = vec_point.length()
                point_acc_list[(x_p, y_p)] = [deg_acc, distance]
                if distance > max_dist:
                    max_dist = distance

        for x_p,y_p in game.point_list:
            if (x_p,y_p) != self.selected_point:
                deg_acc, distance = point_acc_list[(x_p, y_p)]
                p_acc = 0.67 * deg_acc + 0.33 * ((max_dist - distance) / max_dist)
                point_acc_list[(x_p, y_p)] = p_acc

                if max_acc == (0,0):
                    max_acc = (x_p, y_p)
                elif p_acc > point_acc_list[max_acc]:
                    max_acc = (x_p, y_p)


        return max_acc

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
            temp_centre = (0,0)
            if abs(y_move) > 0.1 or abs(x_move) > 0.5:
                temp_centre = self.search_closest_point(self.point_centre, x_move, y_move)
            elif keys[pygame.K_w]:
                temp_centre = self.search_closest_point(self.point_centre, 0, -1)
            elif keys[pygame.K_s]:
                temp_centre = self.search_closest_point(self.point_centre, 0, 1)
            elif keys[pygame.K_a]:
                temp_centre = self.search_closest_point(self.point_centre, -1, 0)
            elif keys[pygame.K_d]:
                temp_centre = self.search_closest_point(self.point_centre, 1, 0)

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
                    self.move_counter += 1
            elif keys[pygame.K_a] or (x_move < -0.1 and abs(x_move) >= abs(y_move)) or keys[pygame.K_d] or (x_move > 0.1 and x_move >= abs(y_move)):
                if game.point_list[self.selected_point][0] == 0:
                    game.hor_list[y] = game.hor_list[y][0:x-1:1] + "mm" + game.hor_list[y][x+1::1]
                    game.vert_list[y-1] = game.vert_list[y-1][0:x:1] + "#" + game.vert_list[y-1][x+1::1]
                    game.vert_list[y] = game.vert_list[y][0:x:1] + "#" + game.vert_list[y][x+1::1]
                    game.point_list[self.selected_point] = (1,1)
                    self.move_counter += 1

            if (cb or keys[pygame.K_SPACE]) and current_time - self.last_button_time >= BUTTON_DELAY:
                self.selected = False
                self.last_button_time = current_time

class Opponents():
    def __init__(self, delay_i):
        self.opp_positions = [[0,0],[0,0],[0,0]]
        #random opponent positions
        centre = pygame.math.Vector2(6,6)
        for i in range (3):
            dist = 0
            while dist < 5:
                for e in range(2): self.opp_positions[i][e] = random.randint(0,12)
                dist = centre.distance_to(tuple(self.opp_positions[i]))
        #Appearance
        self.opp_image = pygame.surface.Surface((TILE_SIZE - 30, TILE_SIZE - 30))
        #self.opp_image = pygame.image.load("data/images/enemy.png")
        self.opp_image.fill((160,160,160))
        self.screen = game.screen #pygame.display.get_surface()
        self.shortest_paths = [[], [], []]
        self.last_move_time = 0
        self.delay_list = [MOVE_DELAY * 1, MOVE_DELAY * 0.7, MOVE_DELAY * 0.5]
        self.move_delay = self.delay_list[delay_i]

    def draw(self, i):
        pos = ((self.opp_positions[i][0] * TILE_SIZE + 15), (self.opp_positions[i][1] * TILE_SIZE + 15))
        self.screen.blit(self.opp_image, pos)

    def move(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time >= self.move_delay:
            for i in range (3):
                if self.opp_positions[i] == self.shortest_paths[i][0]:
                    self.opp_positions[i] = self.shortest_paths[i][0]
                    self.last_move_time = current_time
                else:
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
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self.running = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("comicsansms", 24)
        self.font_fat = pygame.font.SysFont("bahnschrift", 75, bold=True)
        self.text_labyrunner = self.font_fat.render("LABYRUNNER", True, "yellow")
        self.text_instruction = self.font.render("Press SPACE to play, -> / <- to change difficulty \nCtrl + R to reset stats", True, "white")

        #World
        #collision_sheet1 = pygame.image.load("data/images/collision.png").convert_alpha()
        collision_sheet2 = pygame.image.load("data/images/collision2.png").convert_alpha()
        collision_sheet2.set_colorkey("white")
        self.collision_frames = [
            #pygame.transform.scale(collision_sheet1.subsurface(pygame.Rect(i*30, 0, 30, 30)), (30, 30))
            pygame.transform.scale(collision_sheet2.subsurface(pygame.Rect(i*90, 0, 90, 90)), (90, 90))
            for i in range(32)
        ]
        self.coll_frame_num = 0
        self.last_coll_time = 0
        self.finish_x = 0
        self.finish_y = 0
        self.finish_angle = 0
        self.scale_factor = 1
        
        #Orientation Variables
        self.vert_list = []
        self.hor_list = []
        self.point_list = {}
        self.make_hor_list()
        self.make_vert_list()
        self.make_point_list()
        self.finish_list = [[0,0], [0,12], [12,0], [12,12]]
        self.difficulty_list = ["EASY", "HARD", "WARRIOR"]

        self.mode = "start"
        self.difficulty = 0
        self.last_difficulty_time = 0
        self.wintypes = ["wins-easy", "wins-hard", "wins-warrior"]
        self.gametypes = ["game-counter-easy", "game-counter-hard", "game-counter-warrior"]

    def reset(self):
        self.get_stats()
        self.vert_list = []
        self.hor_list = []
        self.point_list = {}
        self.make_hor_list()
        self.make_vert_list()
        self.make_point_list()
        self.coll_frame_num = 0
        self.finish_x = 0
        self.finish_y = 0
        self.finish_angle = 0
        self.scale_factor = 1

    def update_stats(self):
        with open("data/stats.json", 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)

    def get_stats(self):
        with open('data/stats.json', 'r') as file:
            self.stats = json.load(file)

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

    def play_collision(self, current_time):
        for i in range(3): self.opp.draw(i)
        self.paint_walls()
        #self.screen.blit(self.collision_frames[self.coll_frame_num], self.player.pos)
        self.screen.blit(self.collision_frames[self.coll_frame_num], self.player.pos - (30,30))
        if current_time - self.last_coll_time > 20:
            if self.coll_frame_num < 31:
                self.coll_frame_num += 1
                self.last_coll_time = current_time
                return False
            else:
                return True

    def play_finish(self):
        new_width = int(self.player_final_surface.get_width() * self.scale_factor)
        new_height = int(self.player_final_surface.get_height() * self.scale_factor)
        scaled_surface = pygame.transform.scale(self.player_final_surface, (new_width, new_height))
        rotated_surface = pygame.transform.rotate(scaled_surface, self.finish_angle)
        rect = rotated_surface.get_rect(center= self.player.pos + (15, 15))
        for i in range(3): self.opp.draw(i)
        self.paint_walls()
        self.screen.blit(rotated_surface, rect)
        self.finish_angle += 5
        self.scale_factor -= 0.008
        if self.scale_factor <= 0:
            return True
        else:
            return False


    def show_final_screen(self):

        def paint_final_screen(screen, rect_size, color):
            for y in range (len(screen)):
                for x in range (len(screen[0])):
                    if screen[y][x] == "#": pygame.draw.rect(self.screen, color, (x * rect_size, y * rect_size, rect_size, rect_size), width=0, border_radius=0)
            
        if self.winmode:
            screen = self.data["screen_won"]
            rect_size = 650 / 19
            color = "green"
        else:
            screen = self.data["screen_lost"]
            rect_size = 650 / 25
            color = "red"

        paint_final_screen(screen, rect_size, color)


    def bfs(self, opp_num):    #bfs format: [([6,7 #pos], [[0,0],[0,1],[1,1],...#path), ...(#nächster Weg)]
        queue = deque([(self.opp.opp_positions[opp_num], [])])
        player_pos = [int((self.player.pos[0] - 10) // TILE_SIZE), int((self.player.pos[1] - 10) // TILE_SIZE)]
        visited = []
        while len(queue) > 0:
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

        self.opp.shortest_paths[opp_num][0] = self.opp.opp_positions[opp_num]


    def minmax_value(self, player_pos, opp_positions): #player_pos: [x,y], opp_positions: [[x,y],[x,y],[x,y]]
        """provides the value for the minmax algorithm"""
        i_p, i_o = 0,0
        queue = [("o", opp_positions[i]) for i in range(len(opp_positions))] + [("p", player_pos)]
        #Format: [("o", [x,y]), ("p", [x,y]), (...), ...]
        visited = [] #Format: [[x,y],[x,y],...]
        fields_p, fields_o, exits_p, exits_o = 0,0,0,0
        while len(queue) > 0:
            coords_to_search = []
            if i_p * MOVE_DELAY <= i_o * self.opp.move_delay: 
                for i in range(len(queue)): #alle Spielerkoordinaten raussuchen
                    if queue[i][0] == "p":
                        coords_to_search.append(queue[i])
                for n in range(len(coords_to_search)):
                    queue.pop(queue.index(coords_to_search[n]))
                i_p += 1

            else:
                for i in range(len(queue)): #alle Botkoordinaten raussuchen
                    if queue[i][0] == "o":
                        coords_to_search.append(queue[i])
                for n in range(len(coords_to_search)):
                    queue.pop(queue.index(coords_to_search[n]))
                i_o += 1

            for k in range(len(coords_to_search)):
                coords = coords_to_search[k][1]
                mode = coords_to_search[k][0]
                if coords not in visited:
                    visited.append(coords)
                    if mode == "o":
                        if coords in self.finish_list:
                            exits_o += 1
                        fields_o += 1
                    if mode == "p":
                        if coords in self.finish_list:
                            exits_p += 1
                        fields_p += 1
                    v = pygame.math.Vector2(coords)
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if self.player.movable(v, v + (dx, dy), "opp") and [v.x + dx, v.y + dy] not in visited:
                            queue.append((mode, [v.x + dx, v.y + dy]))
                coords_to_search.pop(k)
        minmax_value = (fields_p / (fields_p + fields_o)) + (exits_p / (exits_p + exits_o))
        return minmax_value




    def update_opp(self):
        for i in range(3):
            self.bfs(i)
        #print(self.opp.shortest_paths)
    
    def update_radar(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_radar_time >= RADAR_DELAY:
            mp = (self.player.pos[0] + 15), (self.player.pos[1] + 15) # Mittelpunkt
            entry = [mp, current_time, 0] # MP, Zeit, Radius
            self.radar_list.append(entry)
            self.last_radar_time = current_time
        if len(self.radar_list) > 0:
            #print(self.radar_list)
            for i in range (len(self.radar_list)): #jeden Radar im Radius updaten
                if i >= len(self.radar_list): break
                if current_time > self.radar_list[i][1]:
                    if self.radar_list[i][2] > 13 * TILE_SIZE:
                        self.radar_list.pop(i)
                        continue
                    else:
                        self.radar_list[i][2] += (13 * TILE_SIZE / (1 * RADAR_DELAY / 1000)) / 60
                        self.radar_list[i][1] = current_time
                for n in range (3): #prüfen ob Opps getroffen werden
                    opp_x = self.opp.opp_positions[n][0]
                    opp_y = self.opp.opp_positions[n][1] 
                    mp = self.radar_list[i][0]
                    dist = pygame.math.Vector2(mp).distance_to((opp_x * TILE_SIZE + 25, opp_y * TILE_SIZE +  25))
                    if abs(dist -  self.radar_list[i][2]) < 0.5 * TILE_SIZE:
                        self.opp.draw(n)
                pygame.draw.circle(self.screen, "red", mp, self.radar_list[i][2], 5)
                

    def run(self):
        self.get_stats()
        while self.running:
            self.screen.fill((0,0,100))
            current_time = pygame.time.get_ticks()

            if self.mode == "start":
                rating = 0
                for i in range(len(self.wintypes)):
                    if self.stats[self.gametypes[i]] == 0:
                        winrate = 0
                    else: 
                        winrate = self.stats[self.wintypes[i]] / self.stats[self.gametypes[i]] * 100
                    rating += (i+1) / 6 * winrate
                rating = round(rating, 1)

                highscore = self.stats["highscore"]
                text_wr = self.font.render(f"RATING: {rating}%", True, "white")
                text_pr = self.font.render(f"PERSONAL BEST: {highscore}s", True, "white")
                text_difc = self.font.render(f"DIFFICULTY: {self.difficulty_list[self.difficulty]}", True, "white")

                self.screen.blit(self.text_labyrunner, (WINDOW_SIZE * 0.075, WINDOW_SIZE * 0.1))
                self.screen.blit(text_wr, (WINDOW_SIZE * 0.2, WINDOW_SIZE * 0.5))
                self.screen.blit(text_pr, (WINDOW_SIZE * 0.2, WINDOW_SIZE * 0.6))
                self.screen.blit(text_difc, (WINDOW_SIZE * 0.2, WINDOW_SIZE * 0.7))
                self.screen.blit(self.text_instruction, (WINDOW_SIZE * 0.1, WINDOW_SIZE * 0.85))
                

                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] or (pygame.joystick.get_count() > 0 and game.controller.get_button(10)):
                    self.mode = "game"
                    self.game_time = current_time

                    self.player = Player()
                    self.opp = Opponents(self.difficulty)
                    self.update_opp()
                    self.radar_list = []
                    self.last_radar_time = current_time - 5000

                if keys[pygame.K_r] and keys[pygame.K_LCTRL]:
                    self.stats["highscore"] = 10000
                    for i in range (len(self.gametypes)):
                        self.stats[self.gametypes[i]] = 0
                        self.stats[self.wintypes[i]] = 0
                    self.update_stats()


                if current_time - self.last_difficulty_time > 250:
                    if keys[pygame.K_RIGHT] or (pygame.joystick.get_count() > 0 and game.controller.get_button(1)):
                        self.difficulty = (self.difficulty + 1) % 3
                        self.last_difficulty_time = current_time

                    elif keys[pygame.K_LEFT] or (pygame.joystick.get_count() > 0 and game.controller.get_button(2)):
                        self.difficulty = (self.difficulty - 1) % 3
                        self.last_difficulty_time = current_time
            
            elif self.mode == "game":
                self.player.control_walls()
                self.paint_walls()
                self.screen.blit(self.player.image, self.player.pos)
                self.player.move()
                player_pos = [(self.player.pos[0] - 10) / TILE_SIZE, (self.player.pos[1] - 10) / TILE_SIZE]
                if player_pos in self.finish_list:
                    self.winmode = True
                    self.mode = "win"
                    self.player_final_surface = pygame.Surface((30,30), pygame.SRCALPHA)
                    self.player_final_surface.fill("green")
                    pygame.draw.rect(self.player_final_surface, (255,0,0), (0,0,30,30))
                    continue
                if self.player.move_counter > 0:
                    self.player.move_counter = 0
                    self.update_opp()
                self.opp.move()
                self.update_radar()
                if player_pos in self.opp.opp_positions:
                    self.winmode = False
                    self.mode = "collision"
                    continue

                if self.player.moving and self.player.movable(self.player.pos, self.player.temp_pos, "player"):
                    self.screen.blit(self.player.shade, self.player.temp_pos)

            elif self.mode == "collision":
                if self.play_collision(current_time):
                    self.mode = "end"
                    end_time = pygame.time.get_ticks()

            elif self.mode == "win":
                if self.play_finish():
                    self.mode = "end"
                    end_time = pygame.time.get_ticks()

            else:
                self.show_final_screen()
                if current_time - end_time > 2500:
                    self.mode = "start"
                    self.stats[self.gametypes[self.difficulty]] += 1
                    if self.winmode:
                        self.stats[self.wintypes[self.difficulty]] += 1
                        time = round((current_time - self.game_time) / 1000, 1)
                        if time < self.stats["highscore"]:
                            self.stats["highscore"] = time
                            self.game_time = current_time

                    self.update_stats()
                    self.reset()
                    


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)
game = Game()
game.run()
