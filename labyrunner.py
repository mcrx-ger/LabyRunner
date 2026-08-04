import pygame
import sys
import json

MOVE_DELAY = 500
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
            print(f"Controller: {self.controller.get_name()}, axes: {self.controller.get_numaxes}, balls: {self.controller.get_numballs}")
        
        pygame.display.set_caption("LabyRunner")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.running = True
        self.clock = pygame.time.Clock()
        self.last_move_time = 0

        self.image = pygame.surface.Surface((TILE_SIZE - 20, TILE_SIZE - 20))
        #self.player_rect = self.image.get_rect()
        self.image.fill((255,0,0))
        self.pos = (6*TILE_SIZE + 10, 6*TILE_SIZE + 10) #pygame.math.Vector2(self.player_rect.center)
        self.shade = pygame.surface.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.shade.fill((57, 0, 138))
        self.direction = pygame.math.Vector2()
        self.moving = False

    def paint_walls(self):
        #horizontale Wände
        lines = self.data["grid"][0::2]
        for line in lines:
            elems = list(line)[1::2]
            for i in range (len(elems)):
                x = i
                y = lines.index(line)
                if elems[i] == "w":
                    pygame.draw.line(self.screen, "white", (x * TILE_SIZE, y * TILE_SIZE), ((x+1) * TILE_SIZE, y * TILE_SIZE), width=5)
                elif elems[i] == "m":
                    pygame.draw.line(self.screen, (210, 255, 0), (x * TILE_SIZE, y * TILE_SIZE), ((x+1) * TILE_SIZE, y * TILE_SIZE), width=5)
        #vertikale Wände
        lines = self.data["grid"][1::2]
        for line in lines:
            elems = list(line)[0::2]
            for i in range (len(elems)):
                x = i
                y = lines.index(line)
                if elems[i] == "w":
                    pygame.draw.line(self.screen, "white", (x * TILE_SIZE, y * TILE_SIZE), (x * TILE_SIZE, (y+1) * TILE_SIZE), width=5)
                elif elems[i] == "m":
                    pygame.draw.line(self.screen, (210, 255, 0), (x * TILE_SIZE, y * TILE_SIZE), (x * TILE_SIZE, (y+1) * TILE_SIZE), width=5)
        #zielquadrate zeichnen
        lines = self.data["grid"][0::2]
        for line in lines:
            elems = list(line)[0::2]
            for i in range (len(elems)):
                x = i
                y = lines.index(line)
                if elems[i] == "p":
                    pygame.draw.circle(self.screen, (26, 255, 0), (x * TILE_SIZE, y * TILE_SIZE), 5)


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
        if current_time - self.last_move_time >= MOVE_DELAY and self.moving:
            self.pos = self.temp_pos
            self.last_move_time = current_time
            self.moving = False

    def run(self):
        #self.paint_walls()
        while self.running:
            self.screen.fill((0,0,100))
            self.paint_walls()
            #pygame.draw.rect(self.screen, (125,75,45), self.wall)
            self.screen.blit(self.image, self.pos)

            self.move()
            if self.moving:
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
