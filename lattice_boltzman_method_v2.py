import pygame
import numpy as np
import random

# Parameters
GRID_SIZE = (100, 100)  # Size of the grid
CELL_SIZE = 10  # Size of a single cell
FPS = 30  # Frames per second
NUM_PARTICLES = 500  # Number of particles to generate

BACKGROUND_COLOR = (0, 0, 0)  # Background color
PARTICLE_COLOR = (255, 255, 255)  # Particle color
WALL_COLOR = (200, 0, 0)  # Wall color

WALL_POSITION = GRID_SIZE[0] // 4  # Wall position on the X-axis
WALL_HOLE_START = GRID_SIZE[1] // 2 - 5  # Start of the hole in the wall
WALL_HOLE_END = GRID_SIZE[1] // 2 + 5  # End of the hole in the wall

# Directions for D2Q8 (8 directions: right, left, up, down, and diagonals)
velocities = [(1, 0), (-1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]  # right, left, down, up, and diagonals
clock = pygame.time.Clock()

# Class for the Lattice Boltzmann model
class LatticeBoltzmann:
    def __init__(self):
        # Initialize distribution functions
        self.f = np.zeros((GRID_SIZE[0], GRID_SIZE[1], 8))  # 8 for D2Q8 (8 directions)
        self.particles = []  # List of particle positions and their velocities
        self.initialize()
        self.tau = 0.6  # Relaxation time

    def initialize(self):
        # Generate a set number of particles
        for _ in range(NUM_PARTICLES):
            x = random.randint(0, GRID_SIZE[0] // 4 - 1)  # Only in the left region for particles
            y = random.randint(0, GRID_SIZE[1] - 1)  # Random vertical position
            direction = random.choice(range(8))  # Random initial velocity direction
            self.particles.append((x, y, direction))  # Store position and velocity direction

            # Set initial conditions for particles
            self.f[x, y, direction] = 1.0

    def calculate_equilibrium(self, rho, velocity):
        """Calculate the equilibrium distribution for each direction."""
        c = 1  # Lattice speed (assuming it is 1 here)
        eq = np.zeros(8)

        for i in range(8):
            # Directions
            vx, vy = velocities[i]
            # Dot product of velocity and lattice velocity
            uv = velocity[0] * vx + velocity[1] * vy
            usqr = velocity[0] ** 2 + velocity[1] ** 2  # magnitude of velocity squared

            # Equilibrium distribution function
            eq[i] = (rho / 8) * (1 + 3 * uv / c + 9 * uv ** 2 / (2 * c ** 2) - 3 * usqr / (2 * c ** 2))

        return eq

    def collision(self):
        # Calculate equilibrium and update distribution functions
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                rho = np.sum(self.f[x, y])  # Total density
                velocity = np.array([0.0, 0.0])

                for i, (vx, vy) in enumerate(velocities):
                    velocity += np.array([vx, vy]) * self.f[x, y, i]

                if rho != 0:
                    velocity /= rho

                eq = self.calculate_equilibrium(rho, velocity)

                for i in range(8):
                    self.f[x, y, i] = self.f[x, y, i] - (self.f[x, y, i] - eq[i]) / self.tau

    def streaming(self):
        # Stream the distribution functions to neighboring cells
        new_f = np.zeros_like(self.f)
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                for i, (vx, vy) in enumerate(velocities):
                    nx, ny = (x + vx) % GRID_SIZE[0], (y + vy) % GRID_SIZE[1]  # Periodic boundary
                    if not (x == WALL_POSITION and WALL_HOLE_START <= y < WALL_HOLE_END):
                        new_f[nx, ny, i] = self.f[x, y, i]
        self.f = new_f

    def handle_particle_collisions(self):
        """Detect and handle collisions between particles."""
        position_dict = {}
        new_particles = []

        for x, y, direction in self.particles:
            # Use position as a key to detect collisions
            if (x, y) not in position_dict:
                position_dict[(x, y)] = []
            position_dict[(x, y)].append(direction)

        for (x, y), directions in position_dict.items():
            if len(directions) > 1:
                # Collision detected, redistribute velocities
                total_density = len(directions)
                new_directions = random.sample(range(8), total_density)

                for new_direction in new_directions:
                    new_particles.append((x, y, new_direction))
            else:
                # No collision, retain original direction
                new_particles.append((x, y, directions[0]))

        self.particles = new_particles

    def update_particles(self):
        # Move particles according to their velocity and handle collisions with the wall and boundaries
        new_particles = []
        for x, y, direction in self.particles:
            vx, vy = velocities[direction]
            nx, ny = x + vx, y + vy

            # Check boundary collisions
            if nx < 0 or nx >= GRID_SIZE[0]:
                direction = (direction + 1) % 8 if vx > 0 else (direction - 1) % 8
                nx = max(0, min(GRID_SIZE[0] - 1, nx))
            if ny < 0 or ny >= GRID_SIZE[1]:
                direction = (direction + 1) % 8 if vy > 0 else (direction - 1) % 8
                ny = max(0, min(GRID_SIZE[1] - 1, ny))

            # Wall collision
            if nx == WALL_POSITION and not (WALL_HOLE_START <= ny < WALL_HOLE_END):
                direction = (direction + 1) % 8
                nx, ny = x, y

            new_particles.append((nx, ny, direction))

        self.particles = new_particles

    def update(self):
        self.collision()
        self.streaming()
        self.update_particles()
        self.handle_particle_collisions()


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE))
pygame.display.set_caption('Lattice Boltzmann Simulation with Particle Collisions')

# Create an instance of the LatticeBoltzmann class
lb_model = LatticeBoltzmann()

# Function to draw the wall
def draw_wall(screen):
    for y in range(GRID_SIZE[1]):
        if WALL_HOLE_START <= y <= WALL_HOLE_END:
            continue
        x = WALL_POSITION
        pygame.draw.rect(screen, WALL_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Main loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_wall(screen)
    lb_model.update()

    for x, y, _ in lb_model.particles:
        pygame.draw.circle(screen, PARTICLE_COLOR,
                           (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2),
                           CELL_SIZE // 4)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
