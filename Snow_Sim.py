import pygame
import random
import sys
import noise  # Perlin noise for 3D wind
import math

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Snowfall with Wind Field")

# Constants
NUM_SNOWFLAKES = 4000
Z_NEAR, Z_FAR = 1, 10  # Depth range
SCALE = 0.01
TIME_SCALE = 0.002
MAX_WIND_NOISE = 1.5

#Definine initial custome field
def inital_field_x(x,y):
    return abs(5-x)/abs(x)

def inital_field_y(x,y):
    return abs(5-y)/abs(y)



# Perspective scaling
def project(x, y, z):
    scale = 1 / z  # Perspective: closer = bigger
    px = x
    py = y
    return int(px), int(py), scale

# Snowflake class with depth
class Snowflake:
    def __init__(self):
        self.reset(HEIGHT)

    def reset(self, y_start):
        self.x = random.uniform(1e-1, WIDTH)
        self.y = random.uniform(1e-1, y_start)
        self.z = random.uniform(Z_NEAR, Z_FAR)
        self.base_speed = 0.5 + (Z_FAR - self.z) * 0.3  # Nearer falls faster

    def fall(self, wind_field, t):
        wind_x, wind_y, wind_z = wind_field(self.x, self.y, self.z, t)
        self.x += wind_x * (1 / self.z)
        self.y += (self.base_speed + wind_y) * (1 / self.z)
        self.z += wind_z * 0.01  # Slow z motion (e.g., drifting closer/farther)

        # Wrap around when out of screen or depth range
        if self.y > HEIGHT or self.z < Z_NEAR or self.z > Z_FAR:
            self.reset(5e-1)

    def draw(self, surface):
        px, py, scale = project(self.x, self.y, self.z)
        radius = max(1, int(3 * scale))
        alpha = min(255, int(255 * scale))

        # Use a semi-transparent surface for depth
        snowflake_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(snowflake_surface, (255, 255, 255, alpha), (radius, radius), radius)
        surface.blit(snowflake_surface, (px - radius, py - radius))

# 3D Wind field using Perlin noise
def wind_field(x, y, z, t):
    nx, ny, nz = x * SCALE, y * SCALE, z * SCALE
    nt = t * TIME_SCALE

    angle_xy = noise.pnoise3(nx, ny, nt) * math.pi * 2
    angle_z = noise.pnoise3(ny, nz, nt + 100) * math.pi

    wind_x = math.cos(angle_xy) * MAX_WIND_NOISE +  inital_field_x(x,y)
    wind_y = math.sin(angle_xy) * MAX_WIND_NOISE +  inital_field_y(x,y)
    wind_z = math.sin(angle_z) * 0.5  # Small drift in z

    return wind_x, wind_y, wind_z

# Create snowflakes
snowflakes = [Snowflake() for _ in range(NUM_SNOWFLAKES)]

# Main loop
clock = pygame.time.Clock()
running = True
t = 0

while running:
    screen.fill((15, 15, 30))  # Deep background
    t += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for flake in sorted(snowflakes, key=lambda f: f.z, reverse=True):  # Draw near last
        flake.fall(wind_field, t)
        flake.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
