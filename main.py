import pygame
import sys
import os
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Параметры
gravity = 0.5
jump_power = -10
player_speed = 5
fireball_interval = 5000  # миллисекунд

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Платформер")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Звук
pygame.mixer.init()
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
coin_sound = pygame.mixer.Sound("sounds/coin.wav")
hurt_sound = pygame.mixer.Sound("sounds/hurt.wav")
game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")

# Загрузка изображений
PLAYER_NORMAL_IMG = pygame.transform.scale(pygame.image.load("images/cat_basic.png").convert_alpha(), (60, 60))
PLAYER_BURNED_IMG = pygame.transform.scale(pygame.image.load("images/cat_burned_f3.png").convert_alpha(), (60, 60))
COIN_IMG = pygame.transform.scale(pygame.image.load("images/coin.png").convert_alpha(), (20, 20))
FIREBALL_IMG = pygame.transform.scale(pygame.image.load("images/fireball.png").convert_alpha(), (30, 30))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PLAYER_NORMAL_IMG
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.burned = False
        self.burned_time = 0
        self.platform_dx = 0

    def update(self, keys):
        if self.burned and pygame.time.get_ticks() - self.burned_time >= 2000:
            self.image = PLAYER_NORMAL_IMG
            self.burned = False

        dx = 0
        if keys[pygame.K_a]:
            dx = -player_speed
        if keys[pygame.K_d]:
            dx = player_speed

        self.vel_y += gravity
        dy = self.vel_y

        self.on_ground = False
        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y > 0:
                    dy = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.on_ground = True
                    self.platform_dx = platform.speed if platform.moving else 0

        self.rect.x += dx + (self.platform_dx if self.on_ground else 0)
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y += dy
        self.rect.y = min(HEIGHT - self.rect.height, self.rect.y)

    def jump(self):
        if self.on_ground:
            self.vel_y = jump_power
            jump_sound.play()
            self.platform_dx = 0

    def take_hit(self):
        if not self.burned:
            self.image = PLAYER_BURNED_IMG
            self.burned = True
            self.burned_time = pygame.time.get_ticks()
            hurt_sound.play()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, moving=False, speed=0):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.moving = moving
        self.speed = speed
        self.direction = 1

    def update(self):
        if self.moving:
            self.rect.x += self.speed * self.direction
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = COIN_IMG
        self.rect = self.image.get_rect(center=(x, y))

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = FIREBALL_IMG
        self.rect = self.image.get_rect(center=(x, 0))
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Уровни
levels = [
    {
        "platforms": [
            Platform(0, HEIGHT - 40, WIDTH, 40),
            Platform(200, 450, 120, 20),
            Platform(400, 350, 120, 20, moving=True, speed=2),
            Platform(600, 250, 120, 20)
        ],
        "coins": [
            Coin(220, 430), Coin(620, 230)
        ]
    }
]

current_level = 0

player = Player(100, 500)
player_group = pygame.sprite.Group(player)
platform_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score = 0
lives = 3
paused = False
last_fireball_time = pygame.time.get_ticks()

def load_level(index):
    platform_group.empty()
    coin_group.empty()
    fireball_group.empty()
    for p in levels[index]["platforms"]:
        platform_group.add(p)
    for c in levels[index]["coins"]:
        coin_group.add(c)

load_level(current_level)

def draw_ui():
    screen.blit(font.render(f"Счёт: {score}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Жизни: {lives}", True, BLACK), (10, 40))
    if paused:
        screen.blit(font.render("Пауза", True, BLACK), (WIDTH//2 - 40, HEIGHT//2))

def show_game_over():
    screen.fill(BLACK)
    text = font.render("Game Over", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 60, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)

# Главный цикл игры
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_ESCAPE:
                paused = not paused

    if not paused:
        keys = pygame.key.get_pressed()
        player.update(keys)

        platform_group.update()
        fireball_group.update()

        for coin in pygame.sprite.spritecollide(player, coin_group, True):
            score += 10
            coin_sound.play()

        if pygame.time.get_ticks() - last_fireball_time > fireball_interval:
            x_pos = random.randint(0, WIDTH - 30)
            fireball_group.add(Fireball(x_pos))
            last_fireball_time = pygame.time.get_ticks()

        if pygame.sprite.spritecollide(player, fireball_group, True):
            if lives > 0:
                lives -= 1
                player.take_hit()
                player.rect.topleft = (100, 500)
            if lives <= 0:
                lives = 0
                game_over_sound.play()
                show_game_over()
                running = False

    screen.fill(SKY_BLUE)
    platform_group.draw(screen)
    coin_group.draw(screen)
    fireball_group.draw(screen)
    player_group.draw(screen)

    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()
