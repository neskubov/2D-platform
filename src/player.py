import pygame
import os
import sys


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Загрузка изображения
        try:
            base_path = os.path.dirname(__file__)
            image_path = os.path.join(base_path, '..', 'assets', 'images', 'player.png')
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))
        except:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 0))
            print("Предупреждение: player.png не найден, используется заглушка")

        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.jump_power = -15

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def update(self, keys, platforms):
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_d]:
            self.rect.x += 5

        self.vel_y += 0.5
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def reset_position(self, x, y):
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.on_ground = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.level = Level([
            "                          ",
            "                          ",
            "        PPPPPPP           ",
            "                          ",
            "    PPPP                  ",
            "                 PPPP     ",
            "PPPPPPPPPPPPPPPPPPPPPPPPPP"
        ])
        self.player = Player(*self.level.start_pos)
        self.game_active = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Выход по ESC
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE and self.player.on_ground:
                    self.player.jump()
                if event.key == pygame.K_r:
                    self.level.reset()
                    self.player.reset_position(*self.level.start_pos)
                    self.game_active = True

    def run(self):
        while True:
            self.handle_events()

            if self.game_active:
                keys = pygame.key.get_pressed()
                self.player.update(keys, self.level.platforms)

                if self.level.check_out_of_bounds(self.player.rect):
                    if self.level.lives <= 0:
                        self.game_active = False
                    else:
                        self.player.reset_position(*self.level.start_pos)

                if self.level.check_finish(self.player.rect):
                    print("Уровень пройден!")
                    self.game_active = False

                self.screen.fill((0, 0, 0))
                self.level.draw(self.screen)
                self.player.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()