import pygame
import numpy as np


GRID_SIZE = (100, 100)
CELL_SIZE = 10
FPS = 30


BACKGROUND_COLOR = (0, 0, 0)
PARTICLE_COLOR = (255, 255, 255)
WALL_COLOR = (200, 0, 0)


WALL_POSITION = GRID_SIZE[0] // 4  # Ściana w 1/4 szerokości planszy
WALL_HOLE_START = GRID_SIZE[1] // 2 - 5  # Początek otworu
WALL_HOLE_END = GRID_SIZE[1] // 2 + 5  # Koniec otworu


DIRECTIONS = {
    0: (-1, 0),  # L
    1: (0, -1),  # U
    2: (1, 0),   # R
    3: (0, 1),   # D
    4: (-1, -1), # LU
    5: (1, -1),  # RU
    6: (-1, 1),  # LD
    7: (1, 1)    # RD
}



def initialize_grid(grid_size, num_particles):
    """Tworzy siatkę z cząstkami, ustawionymi w losowych pozycjach po lewej stronie, zgodnie z liczbą cząsteczek."""
    grid = np.zeros((grid_size[0], grid_size[1], 8), dtype=int)

    count = 0
    while count < num_particles:
        x = np.random.randint(0, WALL_POSITION)
        y = np.random.randint(0, grid_size[1])
        direction = np.random.randint(0, 8)

        if np.sum(grid[x, y]) == 0:
            grid[x, y, direction] = 1
            count += 1

    return grid



    """Rysuje siatkę na ekranie."""
def draw_grid(screen, grid):
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            cx, cy = x * CELL_SIZE, y * CELL_SIZE
            for direction in range(8):
                if grid[x, y, direction] == 1:
                    pygame.draw.circle(screen, PARTICLE_COLOR, (cx + CELL_SIZE // 2, cy + CELL_SIZE // 2), 2)



    """Rysuje pionową ścianę z otworem."""
def draw_wall(screen):
    for y in range(GRID_SIZE[1]):
        if WALL_HOLE_START <= y <= WALL_HOLE_END:
            continue
        x = WALL_POSITION
        pygame.draw.rect(screen, WALL_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))



    """Aktualizuje stan siatki (ruch cząsteczek)."""
def update_grid(grid):
    new_grid = np.zeros_like(grid)

    # Streaming
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            for direction in range(8):
                if grid[x, y, direction] == 1:
                    dx, dy = DIRECTIONS[direction]
                    new_x, new_y = x + dx, y + dy

                    if 0 <= new_x < grid.shape[0] and 0 <= new_y < grid.shape[1]:
                        if not is_wall(new_x, new_y):
                            if np.sum(new_grid[new_x, new_y]) == 0:
                                new_grid[new_x, new_y, direction] = 1
                            else:
                                # Zderzenie z inną cząsteczką
                                new_direction = (direction + 4) % 8
                                new_grid[x, y, new_direction] = 1
                                for other_direction in range(8):
                                    if new_grid[new_x, new_y, other_direction] == 1:
                                        new_grid[new_x, new_y, (other_direction + 4) % 8] = 1
                                        new_grid[new_x, new_y, other_direction] = 0
                        else:
                            if direction in [0, 2]:  # L, R
                                new_grid[x, y, (direction + 2) % 4] = 1
                            elif direction in [1, 3]:  # U, D
                                new_grid[x, y, (direction + 2) % 4] = 1
                            elif direction in [4, 5]:   # LU, RU
                                new_grid[x, y, (direction + 2) % 8] = 1
                            elif direction in [6, 7]:  # LD, RD
                                new_grid[x, y, (direction + 2) % 8] = 1
                    else:
                        if direction in [0, 2]:  # L, R
                            new_grid[x, y, (direction + 2) % 4] = 1
                        elif direction in [1, 3]:  # U, D
                            new_grid[x, y, (direction + 2) % 4] = 1
                        elif direction in [4, 5]:  # LU, RU
                            new_grid[x, y, (direction + 2) % 8] = 1
                        elif direction in [6, 7]:  # LD, RD
                            new_grid[x, y, (direction + 2) % 8] = 1

    return new_grid




    """Sprawdza, czy na pozycji (x, y) jest ściana."""
def is_wall(x, y):
    if x == 0 or x == GRID_SIZE[0] - 1 or y == 0 or y == GRID_SIZE[1] - 1:
        return True

    if x == WALL_POSITION and not (WALL_HOLE_START <= y <= WALL_HOLE_END):
        return True
    return False



def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE))
    pygame.display.set_caption("Gaz Siatkowy - Lattice Gas Automata")
    clock = pygame.time.Clock()

    num_particles = 2000

    grid = initialize_grid(GRID_SIZE, num_particles)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)

        draw_wall(screen)

        draw_grid(screen, grid)

        grid = update_grid(grid)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

