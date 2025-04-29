import pygame
from level import Level
from player import Player


class Game:
    def __init__(self):  # Теперь конструктор не принимает параметров
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()

        # Инициализация уровня и игрока
        level_data = [
            "                          ",
            "                          ",
            "        PPPPPPP           ",
            "                          ",
            "    PPPP                  ",
            "                 PPPP     ",
            "PPPPPPPPPPPPPPPPPPPPPPPPPP"
        ]
        self.level = Level(level_data)
        self.player = Player(*self.level.start_pos)
        self.game_active = True

    def load_next_level(self):
        # Здесь можно реализовать загрузку следующего уровня
        pass

    def handle_collisions(self):
        if self.level.check_out_of_bounds(self.player.rect):
            if self.level.lives <= 0:
                print("Game Over! Press R to restart")
                self.game_active = False
            else:
                self.player.reset_position(*self.level.start_pos)

        if self.level.check_finish(self.player.rect):
            self.load_next_level()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.player.on_ground:
                        self.player.jump()  # Теперь этот метод существует
                    if event.key == pygame.K_r:
                        self.level.reset()
                        self.player.reset_position(*self.level.start_pos)
                        self.game_active = True
            # ... остальной код ...

            if self.game_active:
                self.player.update(pygame.key.get_pressed(), self.level.platforms)
                self.handle_collisions()

                self.screen.fill((0, 0, 0))
                self.level.draw(self.screen)
                self.player.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()