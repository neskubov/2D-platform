import pygame

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
ENEMY_SPEED = 3

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D-платформер")
clock = pygame.time.Clock()

class Hero:
    pass

class Enemy:
    pass

class Platform:
    pass

class Graund:
    pass

class Coin:
    pass

class Spike:
    pass

class Game:
    pass


if __name__ == "__main__":
    game = Game()
 
