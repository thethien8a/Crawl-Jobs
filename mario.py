import pygame
import sys
import math

# Khởi tạo pygame
pygame.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario - Enhanced")
clock = pygame.time.Clock()

# Màu sắc
SKY_BLUE = (92, 148, 252)
SKY_GRADIENT_TOP = (92, 148, 252)
SKY_GRADIENT_BOTTOM = (156, 200, 252)
GREEN = (34, 139, 34)
GRASS_GREEN = (124, 252, 0)
DARK_GREEN = (0, 100, 0)
RED = (228, 52, 52)
DARK_RED = (180, 40, 40)
BROWN = (139, 69, 19)
BRICK_BROWN = (200, 100, 50)
BRICK_DARK = (150, 75, 35)
YELLOW = (255, 215, 0)
GOLD = (255, 200, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKIN_COLOR = (255, 200, 150)
BLUE = (0, 0, 200)
CLOUD_WHITE = (255, 255, 255)
CLOUD_SHADOW = (230, 230, 250)

# Frame counter cho animation
frame_count = 0

# Mario class
class Mario:
    def __init__(self):
        self.width = 30
        self.height = 40
        self.x = 100
        self.y = HEIGHT - 60 - self.height
        self.vel_y = 0
        self.vel_x = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        self.score = 0
        self.facing_right = True
        self.walk_frame = 0

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Di chuyển trái/phải
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.facing_right = False
            self.walk_frame += 0.3
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            self.facing_right = True
            self.walk_frame += 0.3
        else:
            self.vel_x = 0
            self.walk_frame = 0

        # Nhảy
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        # Áp dụng trọng lực
        self.vel_y += self.gravity
        self.y += self.vel_y
        self.x += self.vel_x

        # Giới hạn màn hình
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

        # Chạm đất
        ground_y = HEIGHT - 60 - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.vel_y = 0
            self.on_ground = True

    def draw(self):
        x = int(self.x)
        y = int(self.y)
        
        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 50), (x + 2, y + 38, 26, 6))
        
        if self.facing_right:
            self._draw_mario(x, y, 1)
        else:
            self._draw_mario(x, y, -1)
    
    def _draw_mario(self, x, y, direction):
        # Nếu quay trái, offset x
        if direction == -1:
            x = x + self.width
        
        # Mũ đỏ
        pygame.draw.ellipse(screen, RED, (x + direction * 3, y + 2, direction * 24, 12))
        pygame.draw.rect(screen, RED, (x + direction * 5, y + 5, direction * 20, 10))
        # Visor mũ
        pygame.draw.rect(screen, DARK_RED, (x + direction * 2, y + 10, direction * 26, 4))
        
        # Mặt
        pygame.draw.ellipse(screen, SKIN_COLOR, (x + direction * 5, y + 12, direction * 20, 14))
        # Mắt
        pygame.draw.circle(screen, BLACK, (x + direction * 18, y + 17), 2)
        # Mũi
        pygame.draw.ellipse(screen, SKIN_COLOR, (x + direction * 20, y + 19, direction * 6, 5))
        # Ria
        pygame.draw.arc(screen, BROWN, (x + direction * 14, y + 21, direction * 12, 6), 3.14, 6.28, 2)
        
        # Thân áo đỏ
        pygame.draw.rect(screen, RED, (x + direction * 3, y + 25, direction * 24, 12))
        # Nút vàng
        pygame.draw.circle(screen, GOLD, (x + direction * 15, y + 30), 2)
        
        # Quần xanh
        pygame.draw.rect(screen, BLUE, (x + direction * 5, y + 33, direction * 20, 4))
        
        # Chân - animation đi bộ
        leg_offset = int(math.sin(self.walk_frame) * 3) if self.vel_x != 0 and self.on_ground else 0
        # Chân trái
        pygame.draw.rect(screen, BLUE, (x + direction * 5, y + 35, direction * 8, 5 + leg_offset))
        pygame.draw.rect(screen, BROWN, (x + direction * 4, y + 38 + leg_offset, direction * 10, 4))
        # Chân phải
        pygame.draw.rect(screen, BLUE, (x + direction * 17, y + 35, direction * 8, 5 - leg_offset))
        pygame.draw.rect(screen, BROWN, (x + direction * 16, y + 38 - leg_offset, direction * 10, 4))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Coin class với animation
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.animation_offset = x * 0.1  # Mỗi coin có phase khác nhau
        self.collect_animation = 0
        self.float_offset = 0

    def update(self):
        global frame_count
        # Floating animation
        self.float_offset = math.sin(frame_count * 0.1 + self.animation_offset) * 3

    def draw(self):
        global frame_count
        if not self.collected:
            y_pos = int(self.y + self.float_offset)
            
            # Hiệu ứng xoay (thay đổi width)
            scale = abs(math.sin(frame_count * 0.08 + self.animation_offset))
            width = int(self.radius * 2 * max(0.3, scale))
            
            # Vẽ coin với hiệu ứng 3D
            # Bóng
            pygame.draw.ellipse(screen, (150, 120, 0), 
                              (self.x - width // 2, y_pos - self.radius + 2, width, self.radius * 2))
            # Coin chính
            pygame.draw.ellipse(screen, GOLD, 
                              (self.x - width // 2, y_pos - self.radius, width, self.radius * 2))
            # Highlight
            if width > 8:
                pygame.draw.ellipse(screen, YELLOW, 
                                  (self.x - width // 4, y_pos - self.radius // 2, width // 2, self.radius))
            # Sparkle
            if int(frame_count + self.animation_offset) % 30 < 5:
                pygame.draw.circle(screen, WHITE, (self.x + 5, y_pos - 5), 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

# Platform class với texture gạch đẹp
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.brick_size = 20

    def draw(self):
        # Vẽ từng viên gạch
        for i in range(0, self.rect.width, self.brick_size):
            brick_x = self.rect.x + i
            brick_width = min(self.brick_size, self.rect.width - i)
            
            # Gạch chính
            pygame.draw.rect(screen, BRICK_BROWN, 
                           (brick_x, self.rect.y, brick_width - 1, self.rect.height - 1))
            # Highlight trên
            pygame.draw.line(screen, (230, 150, 100), 
                           (brick_x, self.rect.y), 
                           (brick_x + brick_width - 2, self.rect.y), 2)
            # Highlight trái
            pygame.draw.line(screen, (230, 150, 100), 
                           (brick_x, self.rect.y), 
                           (brick_x, self.rect.y + self.rect.height - 2), 2)
            # Shadow phải
            pygame.draw.line(screen, BRICK_DARK, 
                           (brick_x + brick_width - 2, self.rect.y), 
                           (brick_x + brick_width - 2, self.rect.y + self.rect.height), 2)
            # Shadow dưới
            pygame.draw.line(screen, BRICK_DARK, 
                           (brick_x, self.rect.y + self.rect.height - 2), 
                           (brick_x + brick_width, self.rect.y + self.rect.height - 2), 2)


# Cloud class
class Cloud:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = 0.2

    def update(self):
        self.x -= self.speed
        if self.x < -100:
            self.x = WIDTH + 50

    def draw(self):
        # Vẽ mây với nhiều hình tròn
        pygame.draw.ellipse(screen, CLOUD_WHITE, (self.x, self.y, self.size * 2, self.size))
        pygame.draw.ellipse(screen, CLOUD_WHITE, (self.x + self.size * 0.5, self.y - self.size * 0.3, self.size * 1.5, self.size))
        pygame.draw.ellipse(screen, CLOUD_WHITE, (self.x + self.size, self.y, self.size * 1.5, self.size * 0.8))


# Bush class
class Bush:
    def __init__(self, x, size):
        self.x = x
        self.y = HEIGHT - 60
        self.size = size

    def draw(self):
        # Vẽ bụi cây với nhiều hình tròn
        pygame.draw.ellipse(screen, GREEN, (self.x, self.y - self.size * 0.6, self.size, self.size * 0.8))
        pygame.draw.ellipse(screen, GREEN, (self.x + self.size * 0.4, self.y - self.size * 0.8, self.size * 0.8, self.size))
        pygame.draw.ellipse(screen, GREEN, (self.x + self.size * 0.8, self.y - self.size * 0.5, self.size * 0.7, self.size * 0.7))
        # Highlight
        pygame.draw.ellipse(screen, GRASS_GREEN, (self.x + self.size * 0.5, self.y - self.size * 0.7, self.size * 0.4, self.size * 0.5))

# Tạo đối tượng game
mario = Mario()

# Tạo platforms
platforms = [
    Platform(200, 280, 100, 20),
    Platform(400, 220, 100, 20),
    Platform(550, 160, 100, 20),
    Platform(100, 200, 80, 20),
]

# Tạo coins
coins = [
    Coin(250, 255),
    Coin(450, 195),
    Coin(600, 135),
    Coin(150, 315),
    Coin(700, 315),
    Coin(140, 175),
]

# Tạo clouds
clouds = [
    Cloud(100, 50, 40),
    Cloud(300, 80, 50),
    Cloud(550, 40, 35),
    Cloud(750, 70, 45),
]

# Tạo bushes
bushes = [
    Bush(50, 40),
    Bush(350, 30),
    Bush(600, 50),
]

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 28)

def check_platform_collision():
    mario.on_ground = False
    mario_rect = mario.get_rect()
    
    # Kiểm tra va chạm với mặt đất
    if mario.y >= HEIGHT - 60 - mario.height:
        mario.on_ground = True
        return
    
    # Kiểm tra va chạm với platforms
    for platform in platforms:
        if mario_rect.colliderect(platform.rect):
            # Nếu đang rơi xuống và chân Mario ở trên platform
            if mario.vel_y > 0 and mario.y + mario.height - mario.vel_y <= platform.rect.top + 5:
                mario.y = platform.rect.top - mario.height
                mario.vel_y = 0
                mario.on_ground = True

def check_coin_collision():
    mario_rect = mario.get_rect()
    for coin in coins:
        if not coin.collected and mario_rect.colliderect(coin.get_rect()):
            coin.collected = True
            mario.score += 100


def draw_background():
    # Gradient sky
    for y in range(HEIGHT - 60):
        ratio = y / (HEIGHT - 60)
        r = int(SKY_GRADIENT_TOP[0] + (SKY_GRADIENT_BOTTOM[0] - SKY_GRADIENT_TOP[0]) * ratio)
        g = int(SKY_GRADIENT_TOP[1] + (SKY_GRADIENT_BOTTOM[1] - SKY_GRADIENT_TOP[1]) * ratio)
        b = int(SKY_GRADIENT_TOP[2] + (SKY_GRADIENT_BOTTOM[2] - SKY_GRADIENT_TOP[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))


def draw_ground():
    # Đất chính
    pygame.draw.rect(screen, BROWN, (0, HEIGHT - 60, WIDTH, 60))
    
    # Lớp cỏ trên
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 60, WIDTH, 8))
    pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - 60, WIDTH, 4))
    
    # Pattern đất
    for x in range(0, WIDTH, 40):
        pygame.draw.rect(screen, (120, 60, 15), (x, HEIGHT - 50, 35, 8))
        pygame.draw.rect(screen, (100, 50, 10), (x + 20, HEIGHT - 35, 35, 8))
        pygame.draw.rect(screen, (120, 60, 15), (x, HEIGHT - 20, 35, 8))


# Game loop
running = True
while running:
    frame_count += 1
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Cập nhật
    mario.update()
    check_platform_collision()
    check_coin_collision()
    
    # Update clouds
    for cloud in clouds:
        cloud.update()
    
    # Update coins animation
    for coin in coins:
        coin.update()

    # Vẽ background với gradient
    draw_background()
    
    # Vẽ clouds (phía sau)
    for cloud in clouds:
        cloud.draw()
    
    # Vẽ bushes
    for bush in bushes:
        bush.draw()
    
    # Vẽ mặt đất
    draw_ground()

    # Vẽ platforms
    for platform in platforms:
        platform.draw()

    # Vẽ coins
    for coin in coins:
        coin.draw()

    # Vẽ Mario
    mario.draw()

    # UI Panel
    pygame.draw.rect(screen, (0, 0, 0, 128), (5, 5, 150, 35), border_radius=5)
    pygame.draw.rect(screen, GOLD, (5, 5, 150, 35), 2, border_radius=5)
    
    # Vẽ điểm số
    score_text = font.render(f"★ {mario.score}", True, GOLD)
    screen.blit(score_text, (15, 12))

    # Hướng dẫn
    help_text = title_font.render("← → ↑ or WASD | SPACE: Jump", True, WHITE)
    screen.blit(help_text, (WIDTH - 300, 12))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
