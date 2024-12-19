import pygame
import numpy as np

# Parameters
GRID_SIZE = (100, 100)  # Size of the grid
CELL_SIZE = 10  # Size of a single cell
FPS = 30  # Frames per second

BACKGROUND_COLOR = (0, 0, 0)  # Background color
WALL_COLOR = (200, 0, 0)  # Wall color

WALL_POSITION = GRID_SIZE[0] // 4  # Wall position on the X-axis
WALL_HOLE_START = GRID_SIZE[1] // 2 - 5  # Start of the hole in the wall
WALL_HOLE_END = GRID_SIZE[1] // 2 + 5  # End of the hole in the wall

# Directions for D2Q8 (8 directions: right, left, up, down, and diagonals)
velocities = [(1, 0), (-1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]  # directions
opposite_direction = lambda i: (i + 4) % 8  # Opposite direction index

clock = pygame.time.Clock()

# Class for the Lattice Boltzmann model
class LatticeBoltzmann:
    def __init__(self):
        self.f_in = np.zeros((GRID_SIZE[0], GRID_SIZE[1], 8))  # Input distribution
        self.f_out = np.zeros_like(self.f_in)  # Output distribution
        self.rho = np.zeros((GRID_SIZE[0], GRID_SIZE[1]))  # Density (concentration)
        self.initialize()
        self.tau = 0.6  # Relaxation time

    def initialize(self):
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                self.rho[x, y] = 1.0 if x < GRID_SIZE[0] // 4 else 0.0
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                velocity = np.array([0, 0])
                eq = self.calculate_equilibrium(self.rho[x, y], velocity)
                self.f_in[x, y] = eq

    def calculate_equilibrium(self, rho, velocity):
        """Calculate the equilibrium distribution for each direction."""
        c = 1  # Lattice speed (assuming it is 1 here)
        eq = np.zeros(8)

        # Limit prędkości (usqr) do sensownej wartości
        usqr = min(velocity[0] ** 2 + velocity[1] ** 2, 100.0)  # Ustawienie limitu wartości prędkości

        for i in range(8):
            vx, vy = velocities[i]
            uv = velocity[0] * vx + velocity[1] * vy
            uv = max(min(uv, 1.0), -1.0)  # Ograniczenie dot. prędkości (uv) do zakresu od -1 do 1

            eq[i] = (rho / 8) * (1 + 3 * uv / c + 9 * uv ** 2 / (2 * c ** 2) - 3 * usqr / (2 * c ** 2))

        return eq

    def collision(self):
        """Perform collision step to compute new distributions."""
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                rho = np.sum(self.f_in[x, y])  # Calculate density

                # Unikaj dzielenia przez zbyt małe wartości rho
                if rho < 1e-6:  # Zbyt mała gęstość może powodować problemy
                    rho = 1e-6  # Ustaw minimalną wartość dla rho

                velocity = np.array([0.0, 0.0])
                for i, (vx, vy) in enumerate(velocities):
                    velocity += np.array([vx, vy]) * self.f_in[x, y, i]

                # Normalizacja prędkości przez rho (gęstość)
                if rho > 0:
                    velocity /= rho
                velocity = np.clip(velocity, -5.0, 5.0)  # Ograniczenie wartości prędkości do rozsądnego zakresu

                eq = self.calculate_equilibrium(rho, velocity)
                self.f_out[x, y] = self.f_in[x, y] - (self.f_in[x, y] - eq) / self.tau
                self.rho[x, y] = rho  # Zaktualizuj gęstość dla wizualizacji

    def streaming(self):
        """Perform streaming step, including reflection at walls."""
        new_f = np.zeros_like(self.f_in)
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                for i, (vx, vy) in enumerate(velocities):
                    nx, ny = x + vx, y + vy
                    # Boundary conditions: reflection at walls
                    if nx == WALL_POSITION and not (WALL_HOLE_START <= ny < WALL_HOLE_END):
                        new_f[x, y, i] = self.f_out[x, y, opposite_direction(i)]
                    else:
                        if 0 <= nx < GRID_SIZE[0] and 0 <= ny < GRID_SIZE[1]:
                            new_f[nx, ny, i] = self.f_out[x, y, i]
        self.f_in = new_f

    def update(self):
        self.collision()
        self.streaming()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE))
pygame.display.set_caption('Lattice Boltzmann Simulation - density')

# Create an instance of the LatticeBoltzmann class
lb_model = LatticeBoltzmann()

# Function to draw the wall
def draw_wall(screen):
    for y in range(GRID_SIZE[1]):
        if WALL_HOLE_START <= y < WALL_HOLE_END:
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

    # Visualize density using intensity of the color
    max_rho = np.max(lb_model.rho)
    if max_rho > 0:
        for x in range(GRID_SIZE[0]):
            for y in range(GRID_SIZE[1]):
                intensity = int(255 * lb_model.rho[x, y] / max_rho)
                intensity = max(0, min(255, intensity))  # Ensure intensity is within [0, 255]
                pygame.draw.rect(screen, (intensity, intensity, intensity),
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
