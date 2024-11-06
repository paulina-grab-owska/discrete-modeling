import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# stan początkowy
def init_grid(pattern="glider"):
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    if pattern == "glider":
        # glider
        grid[1, 2] = grid[2, 3] = grid[2, 2] = grid[3, 3] = grid[3, 1] = 1
    elif pattern == "oscillator":
        # oscylator
        grid[GRID_SIZE//2, GRID_SIZE//2-1:GRID_SIZE//2+2] = 1
    elif pattern == "random":
        # random
        grid = np.random.choice([0, 1], (GRID_SIZE, GRID_SIZE), p=[0.8, 0.2])
    elif pattern == "still":
        # neizmienny blok
        grid[1, 2] = grid[2, 3] = grid[2, 1] = grid[3, 3] = grid[3, 1] = grid[4, 2]= 1
    elif pattern == "żabka":
        grid[GRID_SIZE//2-1, GRID_SIZE//2-1:GRID_SIZE//2+2] = 1
        grid[GRID_SIZE//2, GRID_SIZE//2-2:GRID_SIZE//2+1] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2-1:GRID_SIZE//2+2] = 1
    elif pattern == "blinker":
        grid[GRID_SIZE//2, GRID_SIZE//2-4:GRID_SIZE//2+5] = 1
        grid[GRID_SIZE//2-1, GRID_SIZE//2-5] = 1
        grid[GRID_SIZE//2-1, GRID_SIZE//2+4] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2-5] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2+4] = 1
    elif pattern == "chaos":
        grid[GRID_SIZE//2, GRID_SIZE//2] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2] = 1
        grid[GRID_SIZE//2+2, GRID_SIZE//2] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2+1] = 1
        grid[GRID_SIZE//2+2, GRID_SIZE//2-1] = 1
    elif pattern == "glider_gun" :
        grid[GRID_SIZE//2-3, GRID_SIZE//2-4] = 1
        grid[GRID_SIZE//2-3, GRID_SIZE//2-3] = 1
        grid[GRID_SIZE//2-2, GRID_SIZE//2-4] = 1
        grid[GRID_SIZE//2-2, GRID_SIZE//2-3] = 1
        grid[GRID_SIZE//2-1, GRID_SIZE//2-6] = 1
        grid[GRID_SIZE//2-1, GRID_SIZE//2-5] = 1
        grid[GRID_SIZE//2-1, GRID_SIZE//2-4] = 1
        grid[GRID_SIZE//2-1, GRID_SIZE//2+1] = 1
        grid[GRID_SIZE//2, GRID_SIZE//2-6] = 1
        grid[GRID_SIZE//2, GRID_SIZE//2-6] = 1
        grid[GRID_SIZE//2, GRID_SIZE//2-6] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2-5] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2-5] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2-4] = 1
        grid[GRID_SIZE//2+1, GRID_SIZE//2+1] = 1
        grid[GRID_SIZE//2+2, GRID_SIZE//2-5] = 1
        grid[GRID_SIZE//2+2, GRID_SIZE//2-4] = 1
        grid[GRID_SIZE//2+2, GRID_SIZE//2-3] = 1
        grid[GRID_SIZE//2+3, GRID_SIZE//2-4] = 1
    return grid


# warunki brzegowe
def count_neighbors(grid, x, y, boundary="periodic"):
    if boundary == "periodic":
        return (
            grid[(x - 1) % GRID_SIZE, (y - 1) % GRID_SIZE]
            + grid[(x - 1) % GRID_SIZE, y % GRID_SIZE]
            + grid[(x - 1) % GRID_SIZE, (y + 1) % GRID_SIZE]
            + grid[x % GRID_SIZE, (y - 1) % GRID_SIZE]
            + grid[x % GRID_SIZE, (y + 1) % GRID_SIZE]
            + grid[(x + 1) % GRID_SIZE, (y - 1) % GRID_SIZE]
            + grid[(x + 1) % GRID_SIZE, y % GRID_SIZE]
            + grid[(x + 1) % GRID_SIZE, (y + 1) % GRID_SIZE]
        )
    elif boundary == "reflective":
        def get(i, j):
            if i < 0: i = 0
            if i >= GRID_SIZE: i = GRID_SIZE - 1
            if j < 0: j = 0
            if j >= GRID_SIZE: j = GRID_SIZE - 1
            return grid[i, j]
        return (
            get(x - 1, y - 1)
            + get(x - 1, y)
            + get(x - 1, y + 1)
            + get(x, y - 1)
            + get(x, y + 1)
            + get(x + 1, y - 1)
            + get(x + 1, y)
            + get(x + 1, y + 1)
        )


# reguły
def apply_rules(grid, boundary="periodic"):
    new_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            neighbors = count_neighbors(grid, x, y, boundary)
            if grid[x, y] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[x, y] = 0  # dead
                else:
                    new_grid[x, y] = 1  # alive
            else:
                if neighbors == 3:
                    new_grid[x, y] = 1  # born
    return new_grid



# tworzenie gifa
def animate(pattern="glider", boundary="periodic"):
    grid = init_grid(pattern)
    images = []

    for step in range(STEPS):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(grid, cmap="binary")
        plt.axis('off')

        # tymczasową klatkę jako obraz PNG
        filename = f"frame_{step}.png"
        plt.savefig(filename)
        plt.close(fig)

        # obraz jako klatkę do GIF-a
        images.append(Image.open(filename))

        # aktualizuj stan gry
        grid = apply_rules(grid, boundary)

    # gif:
    images[0].save(f"game_of_life_{pattern}_{boundary}.gif", save_all=True, append_images=images[1:], duration=200, loop=0)



animate(pattern="glider", boundary="periodic")
animate(pattern="glider", boundary="reflective")

animate(pattern="oscillator", boundary="periodic")
#animate(pattern="oscillator", boundary="reflective")

animate(pattern="random", boundary="periodic")
#animate(pattern="random", boundary="reflective")

animate(pattern="still", boundary="periodic")
#animate(pattern="still", boundary="reflective")

animate(pattern="żabka", boundary="periodic")
#animate(pattern="żabka", boundary="reflective")

animate(pattern="blinker", boundary="periodic")
#animate(pattern="blinker", boundary="reflective")

animate(pattern="chaos", boundary="periodic")
#animate(pattern="chaos", boundary="reflective")

animate(pattern="glider_gun", boundary="periodic")
#animate(pattern=""glider_gun", boundary="reflective")
