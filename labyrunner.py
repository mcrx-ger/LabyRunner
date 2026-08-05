import pygame
import sys
import json

MOVE_DELAY = 1000 #ms
BUTTON_DELAY = 500
TILE_SIZE = 50
PLAYER_SIZE = 30
WINDOW_SIZE = (650, 650)

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
        
        pygame.display.set_caption("LabyRunner")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.running = True
        self.clock = pygame.time.Clock()
        self.last_move_time = 0
        self.last_button_time = 0

        self.image = pygame.surface.Surface((TILE_SIZE - 20, TILE_SIZE - 20))
        #self.player_rect = self.image.get_rect()
        self.image.fill((255,0,0))
        self.pos = (6*TILE_SIZE + 10, 6*TILE_SIZE + 10)
        self.shade = pygame.surface.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.shade.fill((57, 0, 138))
        #self.direction = pygame.math.Vector2()
        self.moving = False

        self.steering = False
        self.selected = False
        self.selected_point = (0,0)
        self.point_centre = pygame.math.Vector2((6,6))
        self.last_steering_time = 0

        self.vert_list = []
        self.hor_list = []
        self.point_list = {}
        self.closest_points = {"N": (0,0), "S": (0,0), "W": (0,0), "E": (0,0)}
        self.make_hor_list()
        self.make_vert_list()
        self.make_point_list()

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
        #zielquadrate zeichnen
        #punkte zeichnen
        for x,y in self.point_list:
            if self.point_list[(x,y)][1] == 0: #nicht ausgewählt
                pygame.draw.circle(self.screen, (26, 255, 0), (x * TILE_SIZE, y * TILE_SIZE), 5)
            else:
                pygame.draw.circle(self.screen, (200, 0, 0), (x * TILE_SIZE, y * TILE_SIZE), 5)

    def movable(self, player_pos, shadow_pos):
        player_koord = (player_pos - pygame.math.Vector2(10,10)) / TILE_SIZE
        shadow_koord = (shadow_pos - pygame.math.Vector2(10,10)) / TILE_SIZE
        #print(player_koord, shadow_koord)
        sx = int(shadow_koord.x)
        sy = int(shadow_koord.y)
        px = int(player_koord.x)
        py = int(player_koord.y)
        if sx < px and sx >= 0:
            if self.vert_list[py][px] == "#":
                return True
            else:
                return False
        elif sx > px and sx <= 13 :
            if self.vert_list[py][px+1] == "#":
                return True
            else:
                return False
        elif sy < py and sy >= 0:
            if self.hor_list[py][px] == "#":
                return True
            else:
                return False
        elif sy > py and sy <= 13:
            if self.hor_list[py+1][px] == "#":
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
        for x,y in self.point_list:
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
            x_move = self.controller.get_axis(0)
            y_move = self.controller.get_axis(1)
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
        if current_time - self.last_move_time >= MOVE_DELAY and self.moving and self.movable(self.pos, self.temp_pos):
            self.pos = self.temp_pos
            self.last_move_time = current_time
            self.moving = False

    def control_walls(self):
        keys = pygame.key.get_pressed()
        if pygame.joystick.get_count() > 0:
            x_move = self.controller.get_axis(2)
            y_move = self.controller.get_axis(3)
            cb = self.controller.get_button(10)

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
                    self.point_list[self.selected_point] = (self.point_list[self.selected_point][0], 0)
                self.selected_point = temp_centre
                self.point_centre = pygame.math.Vector2(temp_centre)
                self.last_steering_time = current_time
                self.point_list[self.selected_point] = (self.point_list[self.selected_point][0], 1)

            if (cb or keys[pygame.K_SPACE]) and current_time - self.last_button_time >= BUTTON_DELAY:
                self.selected = True
                self.last_button_time = current_time

        else:
            x = self.selected_point[0]
            y = self.selected_point[1]
            if keys[pygame.K_w] or (y_move < -0.1 and abs(y_move) > abs(x_move)) or keys[pygame.K_s] or (y_move > 0.1 and y_move > abs(x_move)):
                if self.point_list[self.selected_point][0] == 1:
                    self.hor_list[y] = self.hor_list[y][0:x-1:1] + "##" + self.hor_list[y][x+1::1]
                    self.vert_list[y-1] = self.vert_list[y-1][0:x:1] + "m" + self.vert_list[y-1][x+1::1]
                    self.vert_list[y] = self.vert_list[y][0:x:1] + "m" + self.vert_list[y][x+1::1]
                    self.point_list[self.selected_point] = (0,1)
            elif keys[pygame.K_a] or (x_move < -0.1 and abs(x_move) >= abs(y_move)) or keys[pygame.K_d] or (x_move > 0.1 and x_move >= abs(y_move)):
                if self.point_list[self.selected_point][0] == 0:
                    self.hor_list[y] = self.hor_list[y][0:x-1:1] + "mm" + self.hor_list[y][x+1::1]
                    self.vert_list[y-1] = self.vert_list[y-1][0:x:1] + "#" + self.vert_list[y-1][x+1::1]
                    self.vert_list[y] = self.vert_list[y][0:x:1] + "#" + self.vert_list[y][x+1::1]
                    self.point_list[self.selected_point] = (1,1)

            if (cb or keys[pygame.K_SPACE]) and current_time - self.last_button_time >= BUTTON_DELAY:
                self.selected = False
                self.last_button_time = current_time
            

    def run(self):
        #self.paint_walls()
        while self.running:
            self.screen.fill((0,0,100))
            self.control_walls()
            self.paint_walls()
            #pygame.draw.rect(self.screen, (125,75,45), self.wall)
            self.screen.blit(self.image, self.pos)

            self.move()
            if self.moving and self.movable(self.pos, self.temp_pos):
                self.screen.blit(self.shade, self.temp_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            self.clock.tick(60)

game = Game()
game.run()
