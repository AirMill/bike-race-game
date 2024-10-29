import pygame
import random
import sys

# Initialize Pygame and the mixer for audio
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 360  # Tall screen for road and sky
SCALE = 3  # Scale factor for pixelated effect
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
ROAD_COLOR = (50, 50, 50)
SKY_COLOR = (135, 206, 235)  # Sky blue

# Set up display
small_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
window = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
pygame.display.set_caption("Isometric Bike Racing Game with Zoom Effect")

# Load player bike sprite (make sure it's in the same folder as the script)
bike_image = pygame.image.load('bike.png').convert_alpha()

# Create a small "barrel" obstacle sprite (red pixel)
barrel_image = pygame.Surface((16, 16))  # Full-size red barrel, but it will start as tiny
barrel_image.fill(RED)

# Load the chiptune music
pygame.mixer.music.load('chiptune.mp3')  # Replace with your chiptune file
pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
pygame.mixer.music.play(-1)  # Play the music in a loop

# Function to draw the road, with the horizon at the center
def draw_road(screen):
    road_width_top = 20  # Narrow at the horizon
    road_width_bottom = 160  # Wider at the bottom of the screen
    road_height = SCREEN_HEIGHT // 2  # Horizon in the center

    for y in range(road_height, SCREEN_HEIGHT, 10):
        road_ratio = (y - road_height) / (SCREEN_HEIGHT - road_height)
        road_top = int(road_width_top + road_ratio * (road_width_bottom - road_width_top))
        pygame.draw.polygon(screen, ROAD_COLOR, [
            (SCREEN_WIDTH // 2 - road_top, y),  # Left edge of the road
            (SCREEN_WIDTH // 2 + road_top, y),  # Right edge of the road
            (SCREEN_WIDTH // 2 + road_top + 10, y + 10),  # Expands as you go down
            (SCREEN_WIDTH // 2 - road_top - 10, y + 10)
        ])

# Classes
class Player:
    def __init__(self):
        self.image = bike_image
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 40
        self.speed = 4

    def move_left(self):
        # Move the player horizontally
        if self.x > SCREEN_WIDTH // 4:
            self.x -= self.speed

    def move_right(self):
        # Move the player horizontally
        if self.x < 3 * SCREEN_WIDTH // 4 - self.image.get_width():
            self.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self):
        self.original_image = barrel_image  # Full-size red barrel
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2  # Start at the horizon
        self.speed = 3
        self.size = 1  # Start tiny, grow larger
        self.image = pygame.transform.scale(self.original_image, (self.size, self.size))  # Scale initially to tiny
        self.road_position = random.uniform(-0.5, 0.5)  # Random position on the road

    def update(self):
        # Move down and scale according to the road perspective
        self.y += self.speed
        if self.y > SCREEN_HEIGHT // 2:
            # Scale factor increases as the obstacle approaches the bottom of the screen
            road_distance_from_horizon = (self.y - SCREEN_HEIGHT // 2) / (SCREEN_HEIGHT // 2)
            self.size = int(1 + road_distance_from_horizon * 15)  # Grow from 1 to full size (16x16)
            self.image = pygame.transform.scale(self.original_image, (self.size, self.size))  # Adjust size dynamically
            # Adjust x position according to road perspective
            road_width_top = 20
            road_width_bottom = 160
            road_ratio = (self.y - SCREEN_HEIGHT // 2) / (SCREEN_HEIGHT // 2)
            road_top = road_width_top + road_ratio * (road_width_bottom - road_width_top)
            self.x = int(SCREEN_WIDTH // 2 + self.road_position * road_top)

    def draw(self, screen):
        # Adjust the position based on the new size to center the scaled image
        screen.blit(self.image, (self.x - self.size // 2, self.y - self.size // 2))

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + self.size

    def collision(self, player):
        # Simple bounding box collision detection
        player_rect = pygame.Rect(player.x, player.y, player.image.get_width(), player.image.get_height())
        obstacle_rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        return player_rect.colliderect(obstacle_rect)

# Game Loop
def game_loop():
    player = Player()
    obstacles = []
    clock = pygame.time.Clock()
    game_over = False

    while not game_over:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_left()
        if keys[pygame.K_RIGHT]:
            player.move_right()

        # Spawn new obstacles
        if random.randint(0, 100) < 3:  # Randomly spawn barrels
            obstacles.append(Obstacle())

        # Update obstacles
        for obstacle in obstacles:
            obstacle.update()

        # Check for collisions and remove off-screen obstacles
        for obstacle in obstacles[:]:
            if obstacle.collision(player):
                game_over = True
            if obstacle.is_off_screen():
                obstacles.remove(obstacle)

        # Drawing
        small_screen.fill(SKY_COLOR)  # Fill the top part with blue (sky)
        draw_road(small_screen)  # Draw isometric road starting from horizon
        player.draw(small_screen)  # Draw player

        for obstacle in obstacles:
            obstacle.draw(small_screen)  # Draw obstacles with zoom effect

        # Scale up and draw on the window
        scaled_screen = pygame.transform.scale(small_screen, (SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
        window.blit(scaled_screen, (0, 0))
        pygame.display.flip()

        # Frame rate control
        clock.tick(FPS)

    # Game over screen
    print("Game Over!")
    pygame.quit()
    sys.exit()

# Run the game
game_loop()
