import pygame
import random
import math
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_RADIUS = 15
ENEMY_SIZE = 30
HEALTH_INCREASE = 200
MAX_HEALTH = 1000
DASH_SPEED = 10
FOLLOW_SPEED = 1  # Speed at which enemies follow the player
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Initialize the screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Windowkill")
clock = pygame.time.Clock()

# Font for text
font = pygame.font.SysFont('Arial', 24)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_RADIUS * 2, PLAYER_RADIUS * 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.health = MAX_HEALTH
        self.dashing = False
        self.direction = pygame.Vector2(0, 0)

    def update(self):
        # Move the player with WASD
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_d]:
            self.rect.x += 5
        if keys[pygame.K_w]:
            self.rect.y -= 5
        if keys[pygame.K_s]:
            self.rect.y += 5

        # Dash functionality (if desired)
        if keys[pygame.K_SPACE]:
            if not self.dashing:
                self.dashing = True
                self.rect.x += self.direction.x * DASH_SPEED
                self.rect.y += self.direction.y * DASH_SPEED
        else:
            self.dashing = False

    def shoot(self, direction):
        self.direction = direction

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.player = player

    def update(self):
        # Move toward the player (simple AI)
        direction_to_player = pygame.Vector2(self.player.rect.centerx - self.rect.centerx, self.player.rect.centery - self.rect.centery)
        distance = direction_to_player.length()

        # Normalize the direction to prevent diagonal movement being faster
        if distance != 0:
            direction_to_player.normalize_ip()

        # Move the enemy towards the player
        self.rect.x += direction_to_player.x * FOLLOW_SPEED
        self.rect.y += direction_to_player.y * FOLLOW_SPEED

        # Check for collision with the player
        if self.rect.colliderect(self.player.rect):
            self.player.health -= 10  # Decrease health when colliding with an enemy
            # Move the enemy back after collision (simple bounce effect)
            self.rect.x -= direction_to_player.x * 5
            self.rect.y -= direction_to_player.y * 5

# Blue Dot class for health
class BlueDot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    def update(self):
        pass

# Function to spawn enemies randomly every 5 seconds
def spawn_enemy():
    new_enemy = Enemy(player)
    all_sprites.add(new_enemy)
    enemies.add(new_enemy)

# Initialize player, enemies, and blue dots
player = Player()
all_sprites = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
blue_dots = pygame.sprite.Group()

# Spawn enemies and blue dots
for _ in range(5):
    enemy = Enemy(player)
    all_sprites.add(enemy)
    enemies.add(enemy)

for _ in range(3):
    blue_dot = BlueDot()
    all_sprites.add(blue_dot)
    blue_dots.add(blue_dot)

# Game loop
running = True
border_expansion = 0  # To control how much the border expands when shooting
last_enemy_spawn_time = time.time()
while running:
    clock.tick(FPS)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update game objects
    all_sprites.update()

    # Check for collisions between player and blue dots
    collected_dots = pygame.sprite.spritecollide(player, blue_dots, True)
    for dot in collected_dots:
        player.health = min(MAX_HEALTH, player.health + HEALTH_INCREASE)

    # Check if player is out of the box
    if player.rect.left < 0 or player.rect.right > WIDTH or player.rect.top < 0 or player.rect.bottom > HEIGHT:
        # Health decreases when player is outside the box
        player.health -= 5  # Customize the penalty rate if needed

    # Shooting kills enemies
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                enemy.kill()  # Kill enemy when shot

    # Check for enemy collisions and kill one of them
    for enemy1 in enemies:
        for enemy2 in enemies:
            if enemy1 != enemy2 and enemy1.rect.colliderect(enemy2.rect):
                enemy1.kill()  # Kill one enemy when they collide
                break  # Exit the inner loop after killing one enemy

    # Spawn new enemies every 5 seconds
    if time.time() - last_enemy_spawn_time >= 5:
        spawn_enemy()
        last_enemy_spawn_time = time.time()

    # Fill screen with black
    screen.fill(BLACK)

    # Draw the box boundary (which expands when shooting)
    pygame.draw.rect(screen, WHITE, (border_expansion, border_expansion, WIDTH - border_expansion * 2, HEIGHT - border_expansion * 2), 2)

    # Draw all sprites
    all_sprites.draw(screen)

    # Draw health box in top-left corner
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 25))
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, 200 * (player.health / MAX_HEALTH), 25))

    # Display game over message if health is below 0
    if player.health <= 0:
        game_over_text = font.render("game over. press ENTER to restart", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

    # Update display
    pygame.display.flip()

    # Check if player pressed ENTER to restart the game
    if player.health <= 0:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            player.health = MAX_HEALTH
            player.rect.center = (WIDTH // 2, HEIGHT // 2)
            for enemy in enemies:
                enemy.kill()  # Remove all current enemies
            for _ in range(5):  # Spawn new enemies after restarting
                spawn_enemy()
            for dot in blue_dots:
                dot.rect.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))

# Quit pygame
pygame.quit()