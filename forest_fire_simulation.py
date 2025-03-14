import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from IPython.display import clear_output
import imageio
import random


EMPTY, TREE, FIRE, BURNT, WATER, ROCK, CONTAMINATED_WATER, BURNING_FOREST = 0, 1, 2, 3, 4, 5, 6, 7


# wczytanie mapy
def load_map(image_path):
    img = Image.open(image_path).convert('RGB')
    map_array = np.array(img)
    return map_array

# inicjalizacja przestrzeni automatu
def initialize_map(map_array):
    terrain = np.zeros(map_array.shape[:2], dtype=int)
    for x in range(map_array.shape[0]):
        for y in range(map_array.shape[1]):
            r, g, b = map_array[x, y]
            if (r, g, b) == (34, 139, 34):  # zielony
                terrain[x, y] = TREE
            elif (r, g, b) == (0, 0, 255):  # niebieski
                terrain[x, y] = WATER
            elif (r, g, b) == (139, 69, 19):  # brązowy na mapie -> szary w symulacji
                terrain[x, y] = ROCK
    return terrain


def update_fire_and_contamination(terrain, wind_direction=(0, 1), humidity=0.5, burn_time=None):
    new_terrain = terrain.copy()
    rows, cols = terrain.shape
    if burn_time is None:
        burn_time = np.zeros_like(terrain, dtype=int)

    dx, dy = wind_direction
    weighted_neighbors = [
        (-1, 0, 0.2), (1, 0, 0.2), (0, -1, 0.2), (0, 1, 0.2),  # sąsiedzi w pobliżu
        (dx, dy, 0.5)  # kierunek wiatru
    ]

    for x in range(1, rows - 1):
        for y in range(1, cols - 1):
            if terrain[x, y] == TREE:
                # Reguła 1: wilgotność
                for wx, wy, weight in weighted_neighbors:
                    nx, ny = x + wx, y + wy
                    if 0 <= nx < rows and 0 <= ny < cols and terrain[nx, ny] in [FIRE, BURNING_FOREST]:
                        if np.random.rand() < weight * (1 - humidity):
                            new_terrain[x, y] = BURNING_FOREST

            elif terrain[x, y] == BURNING_FOREST:
                # Reguła 2: czas trwania spalania
                burn_time[x, y] += 1
                if burn_time[x, y] >= 3:
                    new_terrain[x, y] = BURNT

                for wx, wy, weight in weighted_neighbors:
                    nx, ny = x + wx, y + wy
                    if 0 <= nx < rows and 0 <= ny < cols and terrain[nx, ny] == TREE:
                        if np.random.rand() < weight:
                            new_terrain[nx, ny] = BURNING_FOREST

            # Reguła 3: skażenie wody
            elif terrain[x, y] == CONTAMINATED_WATER:
                for wx, wy, weight in weighted_neighbors:
                    nx, ny = x + wx, y + wy
                    if 0 <= nx < rows and 0 <= ny < cols and terrain[nx, ny] == WATER:
                        if np.random.rand() < weight:
                            new_terrain[nx, ny] = CONTAMINATED_WATER

            # Reguła 4: teren niepalny
            elif terrain[x, y] in [ROCK, WATER]:
                new_terrain[x, y] = terrain[x, y]

    return new_terrain, burn_time


def drop_bomb(terrain, x, y):
    if terrain[x, y] == TREE:
        terrain[x, y] = BURNING_FOREST
    elif terrain[x, y] == WATER:
        terrain[x, y] = CONTAMINATED_WATER

def change_wind():
    try:
        dx, dy = map(int, input("podaj nowy kierunek wiatru (pliczby całkowitep): ").split())
        print(f"nowy kierunek wiatru: ({dx}, {dy})")
        return dx, dy
    except ValueError:
        print("WORNG DATA. wiatr się nie zmienia.")
        return None


def plot_map(terrain, step, gif_writer):
    colors = {
        EMPTY: (255, 255, 255),  # biały
        TREE: (34, 139, 34),     # zielony
        FIRE: (255, 0, 0),       # czerwony
        BURNING_FOREST: (255, 20, 147),  # różowy
        BURNT: (0, 0, 0),        # czarny
        WATER: (0, 0, 255),      # niebieskiB,
        CONTAMINATED_WATER: (0, 255, 0),  # jaskrawozielony
        ROCK: (128, 128, 128),   # szary
    }

    img = np.zeros((*terrain.shape, 3), dtype=np.uint8)
    for state, color in colors.items():
        img[terrain == state] = color

    plt.imshow(img)
    plt.title(f"Step: {step}")
    plt.axis('off')

    plt.savefig("/tmp/temp_image.png", format="png", bbox_inches="tight", pad_inches=0)
    plt.close()

    image = Image.open("/tmp/temp_image.png")
    gif_writer.append_data(np.array(image))

def simulate_fire(map_path, steps=100, wind_direction=(0, 1), humidity=0.5, output_gif_path='/content/fire_simulation.gif'):
    map_array = load_map(map_path)
    terrain = initialize_map(map_array)
    burn_time = np.zeros_like(terrain, dtype=int)

    # start fire w pktcie środkowym
    mid_x, mid_y = terrain.shape[0] // 2, terrain.shape[1] // 2
    terrain[mid_x, mid_y] = FIRE

    # BOMBY:
    num_bombs = int(input("podaj liczbę bomb do zrzutu: "))
    bomb_iterations = list(map(int, input("podaj iteracje zrzutu bomb (oddzielone spacją): ").split()))

    if len(bomb_iterations) != num_bombs:
        print("EROOR: liczba iteracji nie równa liczbie bomb.")
        return

    rows, cols = terrain.shape
    bomb_positions = [(random.randint(0, rows - 1), random.randint(0, cols - 1)) for _ in range(num_bombs)]
    print(f"pzycje bomb (losowe): {bomb_positions}")

    bombs_schedule = {}
    for i in range(num_bombs):
        if bomb_iterations[i] not in bombs_schedule:
            bombs_schedule[bomb_iterations[i]] = []
        bombs_schedule[bomb_iterations[i]].append(bomb_positions[i])

    with imageio.get_writer(output_gif_path, mode='I', duration=0.5) as gif_writer:
        for step in range(steps):
            # zrzut bomb
            if step in bombs_schedule:
                for x, y in bombs_schedule[step]:
                    drop_bomb(terrain, x, y)

            # zmiana kierunku wiatru
            if step % 30 == 0:
                user_action = input("czy chcesz zmienić kierunek wiatru (tak/nie)? ").strip().lower()
                if user_action == 'tak':
                    new_wind = change_wind()
                    if new_wind is not None:
                        wind_direction = new_wind

            clear_output(wait=True)
            plot_map(terrain, step, gif_writer)
            terrain, burn_time = update_fire_and_contamination(terrain, wind_direction, humidity, burn_time)


#simulate_fire('mapa.png', steps=90, wind_direction=(0, 0), humidity=0.6, output_gif_path='/content/fire_simulation.gif')
simulate_fire('mapa2.png', steps=90, wind_direction=(0, 0), humidity=0.6, output_gif_path='/content/fire_simulation2.gif')
