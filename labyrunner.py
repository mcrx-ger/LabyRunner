import pygame
import sys

MOVE_DELAY = 500
TILE_SIZE = 16
WINDOW_SIZE = (800, 800)

class Game():
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        # Check for connected controllers
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            print(f"Controller: {self.controller.get_name()}")
        
        pygame.display.set_caption("LabyRunner")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.running = True
        self.clock = pygame.time.Clock()
        self.last_move_time = 0

        self.image = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
        self.player_rect = self.image.get_rect()
        self.image.fill((255,0,0))
        self.pos = (25*TILE_SIZE, 25*TILE_SIZE) #pygame.math.Vector2(self.player_rect.center)
        self.shade = pygame.surface.Surface((TILE_SIZE, TILE_SIZE))
        self.shade.fill((160,160,160))
        self.direction = pygame.math.Vector2()
        self.moving = False

        #self.wall = pygame.Rect(3*TILE_SIZE, 5*TILE_SIZE, 7*TILE_SIZE, TILE_SIZE)

    def move(self):
        keys = pygame.key.get_pressed()
        x_move = self.controller.get_axis(0)
        y_move = self.controller.get_axis(1)
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
        while self.running:
            self.screen.fill((0,0,100))
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
