import pygame
import os
import sys
import random

# --- Инициализация ---
pygame.init()

# --- Настройки ---
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Физика
gravity = 0.5
jump_power = -10
player_speed = 5

# Ограничения
MAX_JUMP_HEIGHT = 90
MAX_HORIZONTAL_DISTANCE = 200
MIN_VERTICAL_PLATFORM_GAP = 60

# Экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Платформер: Все монетки доступны!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

def resource_path(relative_path):
    """ Возвращает абсолютный путь к ресурсу, работает для .exe и скрипта. """
    try:
        # Если программа запущена из .exe
        base_path = sys._MEIPASS
    except AttributeError:
        # Если программа запущена из исходного кода
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Звук
sound_enabled = False
try:
    pygame.mixer.init()
    jump_sound = pygame.mixer.Sound(resource_path("sounds/jump.wav"))
    coin_sound = pygame.mixer.Sound(resource_path("sounds/coin.wav"))
    hurt_sound = pygame.mixer.Sound(resource_path("sounds/hurt.wav"))
    game_over_sound = pygame.mixer.Sound(resource_path("sounds/game_over.wav"))
    sound_enabled = True
except:
    print("Звуки не загружены")

# --- Загрузка изображений ---
def load_image(path, fallback_size):
    try:
        return pygame.transform.scale(pygame.image.load(resource_path(path)).convert_alpha(), fallback_size)
    except FileNotFoundError:
        print(f"Не удалось загрузить {path}")
        return pygame.Surface(fallback_size, pygame.SRCALPHA)

# --- Обработать проблему с отсутствием изображений ---
try:
    BACKGROUND_IMG = load_image("images/background.png", (WIDTH, HEIGHT))
    PLAYER_NORMAL_IMG = load_image("images/cat_basic.png", (60, 60))
    PLAYER_BURNED_IMG = load_image("images/cat_burned_f3.png", (60, 60))
    COIN_IMG = load_image("images/coin.png", (20, 20))
    FIREBALL_IMG = load_image("images/fireball.png", (30, 30))
except Exception as e:
    print(f"Ошибка при загрузке изображений: {e}")
    pygame.quit()
    sys.exit()

PLAYER_MASK = pygame.mask.from_surface(PLAYER_NORMAL_IMG)
COIN_MASK = pygame.mask.from_surface(COIN_IMG)
FIREBALL_MASK = pygame.mask.from_surface(FIREBALL_IMG)

# --- Классы ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PLAYER_NORMAL_IMG
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = PLAYER_MASK
        self.vel_y = 0
        self.on_ground = False
        self.burned = False
        self.burned_time = 0
        self.platform_dx = 0  # Добавлено из второй версии

    def update(self, keys):
        # Проверяем, если игрок "сгорел", и прошло больше 2 секунд, сбрасываем состояние
        if self.burned and pygame.time.get_ticks() - self.burned_time >= 2000:
            self.image = PLAYER_NORMAL_IMG
            self.mask = pygame.mask.from_surface(self.image)
            self.burned = False

        dx = 0
        if keys[pygame.K_a]:
            dx = -player_speed
        if keys[pygame.K_d]:
            dx = player_speed

        # Добавляем силу тяжести
        self.vel_y += gravity
        dy = self.vel_y
        self.on_ground = False

        # Проверка столкновений с платформами
        future_rect = self.rect.move(0, dy)
        for platform in platform_group:
            if platform.rect.colliderect(future_rect):
                # Игрок падает сверху на платформу
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.top + 10:
                    dy = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.on_ground = True

        # Обновляем позицию игрока
        self.rect.x += dx
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y += dy
        self.rect.y = min(HEIGHT - self.rect.height, self.rect.y)

    def jump(self):
        if self.on_ground:
            self.vel_y = jump_power
            if sound_enabled: jump_sound.play()

    def take_hit(self):
        if not self.burned:
            self.image = PLAYER_BURNED_IMG
            self.mask = pygame.mask.from_surface(self.image)
            self.burned = True
            self.burned_time = pygame.time.get_ticks()
            if sound_enabled: hurt_sound.play()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = COIN_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = COIN_MASK

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = FIREBALL_IMG
        self.rect = self.image.get_rect(center=(x, 0))
        self.mask = FIREBALL_MASK
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# --- Генерация уровней ---
def can_reach(prev_platform, new_platform):
    dx = abs(new_platform.rect.centerx - prev_platform.rect.centerx)
    dy = prev_platform.rect.top - new_platform.rect.top  # сравнение по верхним границам
    return dx <= MAX_HORIZONTAL_DISTANCE and MIN_VERTICAL_PLATFORM_GAP <= dy <= MAX_JUMP_HEIGHT

#<<<<<<< HEAD
def coin_is_reachable(platform, coin):
    sim_steps = 60
    time_step = 1 / FPS
    start_x = platform.rect.centerx
    start_y = platform.rect.top
    dx = coin.rect.centerx - start_x
    vx = dx / sim_steps
    vy = jump_power
    x = start_x
    y = start_y
#=======

# # Логика проверок
#
# def coin_is_reachable(platform, coin):
#     dy = platform.rect.top - coin.rect.centery
#     dx = abs(coin.rect.centerx - platform.rect.centerx)
#
#     return 0 <= dy <= MAX_JUMP_HEIGHT and dx <= MAX_HORIZONTAL_DISTANCE
#>>>>>>> Skynet_name

    for _ in range(sim_steps):
        x += vx
        y += vy
        vy += gravity
        px = int(coin.rect.x - x)
        py = int(coin.rect.y - y)
        player_mask = pygame.mask.Mask(PLAYER_NORMAL_IMG.get_size(), True)
        if player_mask.overlap(COIN_MASK, (px, py)):
            return True
    return False

def generate_random_level(level_num):
    platforms = []
    coins = []
    start_platform = Platform(0, HEIGHT - 40, WIDTH, 40)
    platforms.append(start_platform)
    last_platform = start_platform
    total_platforms = 3 + level_num * 2

    for _ in range(total_platforms):
        for _ in range(10):
            w = random.randint(80, 150)
            h = 20
            y = random.randint(max(60, last_platform.rect.top - MAX_JUMP_HEIGHT),
                               max(80, last_platform.rect.top - MIN_VERTICAL_PLATFORM_GAP))
            x = random.randint(
                max(0, last_platform.rect.centerx - MAX_HORIZONTAL_DISTANCE),
                min(WIDTH - w, last_platform.rect.centerx + MAX_HORIZONTAL_DISTANCE))
            new_platform = Platform(x, y, w, h)
            if can_reach(last_platform, new_platform):
                coin = Coin(x + w // 2, max(30, y - 30))
                if coin_is_reachable(new_platform, coin):
                    platforms.append(new_platform)
                    coins.append(coin)
                    last_platform = new_platform
                    break

    return {"platforms": platforms, "coins": coins, "fireball_interval": max(1000, 5000 - level_num * 400)}

# --- Переменные игры ---
NUM_LEVELS = 10
levels = [generate_random_level(i) for i in range(NUM_LEVELS)]
current_level = 0
score = 0
lives = 3
paused = False

player = Player(100, 500)
player_group = pygame.sprite.Group(player)
platform_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

last_fireball_time = pygame.time.get_ticks()

def load_level(i):
    platform_group.empty()
    coin_group.empty()
    fireball_group.empty()
    for p in levels[i]["platforms"]:
        platform_group.add(p)
    for c in levels[i]["coins"]:
        coin_group.add(c)

def show_level(i):
    screen.fill(SKY_BLUE)
    txt = font.render(f"Уровень {i + 1}", True, BLACK)
    screen.blit(txt, (WIDTH // 2 - 60, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)

def show_game_over():
    if sound_enabled: game_over_sound.play()
    screen.fill(BLACK)
    screen.blit(font.render("Game Over", True, WHITE), (WIDTH // 2 - 60, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)

load_level(current_level)
show_level(current_level)

# --- Главный цикл ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            elif event.key == pygame.K_ESCAPE:
                paused = not paused

    if not paused:
        keys = pygame.key.get_pressed()
        player.update(keys)
        fireball_group.update()
        platform_group.update()

        for coin in pygame.sprite.spritecollide(player, coin_group, True, pygame.sprite.collide_mask):
            score += 10
            if sound_enabled: coin_sound.play()

        now = pygame.time.get_ticks()
        if now - last_fireball_time > levels[current_level]["fireball_interval"]:
            fireball_group.add(Fireball(random.randint(0, WIDTH - 30)))
            last_fireball_time = now

        for fireball in fireball_group:
            if pygame.sprite.collide_mask(player, fireball):
                lives -= 1
                player.take_hit()
                player.rect.topleft = (100, 500)
                if lives <= 0:
                    show_game_over()
                    running = False

        if not coin_group:
            if current_level < NUM_LEVELS - 1:
                current_level += 1
                load_level(current_level)
                show_level(current_level)
                player.rect.topleft = (100, 500)
                player.vel_y = 0
            else:
                screen.fill(SKY_BLUE)
                screen.blit(font.render("🎉 Победа!", True, BLACK), (WIDTH // 2 - 100, HEIGHT // 2))
                pygame.display.flip()
                pygame.time.delay(3000)
                running = False

    screen.blit(BACKGROUND_IMG, (0, 0))
    platform_group.draw(screen)
    coin_group.draw(screen)
    fireball_group.draw(screen)
    player_group.draw(screen)
    screen.blit(font.render(f"Счёт: {score}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Жизни: {lives}", True, BLACK), (10, 40))
    pygame.display.flip()

pygame.quit()
sys.exit()
