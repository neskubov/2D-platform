import pygame
import random
from pygame.sprite import Sprite, Group

TILE_SIZE = 48
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Platform(Sprite):
    def __init__(self, x, y, width=TILE_SIZE, height=TILE_SIZE):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))


class Finish(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))


class Level:
    def __init__(self, level_data):
        self.platforms = Group()
        self.finish = None
        self.lives = 3
        self.start_pos = (100, 100)

        if isinstance(level_data, dict):
            self._load_from_dict(level_data)
        elif isinstance(level_data, list):
            self._load_from_list(level_data)
        else:
            raise ValueError("Unsupported level data type")

    def _load_from_dict(self, data):
        self.lives = data.get("lives", 3)
        self.start_pos = data.get("start_pos", (100, 100))

        if data.get("type") == "random":
            self._generate_random_level(data)
        else:
            self._load_designed_level(data.get("layout", []))

    def _load_from_list(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile == "P":
                    self.platforms.add(Platform(x, y))
                elif tile == "F":
                    self.finish = Finish(x, y)  # Исправлено: удалена лишняя скобка

    def _generate_random_level(self, data):
        platform_count = data.get("platform_count", 10)
        for _ in range(platform_count):
            x = random.randint(0, SCREEN_WIDTH - TILE_SIZE)
            y = random.randint(0, SCREEN_HEIGHT - TILE_SIZE)
            width = random.randint(TILE_SIZE, TILE_SIZE * 3)
            self.platforms.add(Platform(x, y, width, 20))

        self.platforms.add(Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        finish_x = random.randint(100, SCREEN_WIDTH - 100)
        self.finish = Finish(finish_x, SCREEN_HEIGHT - 100)

    def check_out_of_bounds(self, player_rect):
        if (player_rect.left < 0 or player_rect.right > SCREEN_WIDTH or
                player_rect.top < 0):
            self.lives -= 1
            return True
        return False

    def check_finish(self, player_rect):
        if self.finish and player_rect.colliderect(self.finish.rect):
            return True
        return False

    def draw(self, surface):
        self.platforms.draw(surface)
        if self.finish:
            surface.blit(self.finish.image, self.finish.rect)

        font = pygame.font.SysFont(None, 36)
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        surface.blit(lives_text, (10, 10))

    def reset(self):
        self.lives = 3