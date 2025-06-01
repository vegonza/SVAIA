# %% [markdown]
# # Algoritmos genéticos

# %% [markdown]
# ## Importaciones

# %%
!pip install deap
!pip install tqdm

# %%
import random
from typing import Callable

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from deap import base, creator, tools
from matplotlib import pyplot as plt
from tqdm import tqdm

# %% [markdown]
# ## Inicialización

# %%
SEED = 27  # Valor de seed aleatoria
FIL = 4  # num de files
COL = 3  # num de columns
START = 0
END = FIL * COL
CXPB = 0.5  # Probabilidad de cruce
MUTPB = 0.2  # Probabilidad de mutabilidad
POP_LEN = 10  # Tamaño de la poblacion
GENS = 1000  # Número máximo de iteraciones
INDP = 0.05  # Probabilidad de que un determinado indice se intercambie
random.seed(SEED)

# %% [markdown]
# ## Funciones auxiliares

# %%


def draw_chessboard(solution: list[int]):
    """Dibuja un tablero y coloca los números de la lista (tablero aplanado) en las casillas."""
    rows = FIL
    cols = COL
    fig, ax = plt.subplots(figsize=(cols * 1.2, rows * 1.2))
    colors = ['#f0d9b5', '#b58863']

    def get_fontsize(rows, cols):
        max_dim = max(rows, cols)
        if max_dim <= 8:
            return 20
        elif max_dim <= 12:
            return 16
        elif max_dim <= 16:
            return 14
        else:
            return 12

    fontsize = get_fontsize(rows, cols)

    # dibujamos tablero
    for row in range(rows):
        for col in range(cols):
            color = colors[(row + col + 1) % 2]
            square = patches.Rectangle((col, row), 1, 1, facecolor=color)
            ax.add_patch(square)

    # dibujamos los números de la lista en cada casilla
    for idx, value in enumerate(solution):
        row = idx // cols
        col = idx % cols
        # Ajusta el desplazamiento horizontal para centrar mejor los números de 2 dígitos
        text_str = str(value)
        ax.text(col + 0.5, row + 0.5, text_str, fontsize=fontsize,
                ha='center', va='center', color='black', fontweight='bold')

    # Función para verificar si un movimiento es válido para un caballo
    def is_valid_knight_move(pos1, pos2):
        # Convertir posiciones planas a coordenadas 2D
        row1, col1 = pos1 // cols, pos1 % cols
        row2, col2 = pos2 // cols, pos2 % cols

        # Calcular diferencias en filas y columnas
        row_diff = abs(row1 - row2)
        col_diff = abs(col1 - col2)

        # Un movimiento de caballo válido es: (2,1) o (1,2)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    # Función para convertir posición plana a coordenadas
    def pos_to_coords(pos):
        row = pos // cols
        col = pos % cols
        return col + 0.5, row + 0.5  # Centro de la casilla

    # Dibujamos flechas para movimientos válidos consecutivos
    for i in range(len(solution) - 1):
        current_num = i
        next_num = i + 1

        # Encontramos las posiciones de estos números en el tablero
        current_pos = solution.index(current_num)
        next_pos = solution.index(next_num)

        # Verificamos si es un movimiento válido de caballo
        if is_valid_knight_move(current_pos, next_pos):
            # Obtenemos coordenadas
            x1, y1 = pos_to_coords(current_pos)
            x2, y2 = pos_to_coords(next_pos)

            # Dibujamos flecha verde para movimientos válidos
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='->', color='green', lw=3, alpha=0.7))

    ax.set_xlim(-0.1, cols + 0.1)
    ax.set_ylim(-0.1, rows + 0.1)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.box(False)

    # Añadimos una leyenda
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='green', lw=3, label='Valid knight move')]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

    plt.tight_layout()
    plt.show()


# %%
import random
solution = list(range(FIL * COL))
random.shuffle(solution)

draw_chessboard(solution)

# %%
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

disponible = []


def restriction(*args, **kwargs):
    global disponible
    if not disponible:
        disponible.extend(range(FIL * COL))
        disponible = random.sample(disponible, FIL * COL)

    return disponible.pop(0)


toolbox = base.Toolbox()
# Generador de atributos
toolbox.register("attr_bool", restriction, 0, FIL - 1)
# Inicializamos estructuras
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_bool, FIL * COL)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# %%


def fitness(individual: list[int]):
    """Función para evaluar el fitness de los individuos"""
    current_pos = 0
    path_len = 0
    max_path_len = 0
    while current_pos < FIL * COL - 1:
        pos = individual.index(current_pos)
        next_pos = individual.index(current_pos + 1)
        col_diff = abs(pos % COL - next_pos % COL)
        row_diff = abs(pos // COL - next_pos // COL)
        if col_diff == 1 and row_diff == 2 or col_diff == 2 and row_diff == 1:
            path_len += 1
        else:  # TODO: fitness del inicio a fallo vs total combinaciones validas
            max_path_len = max(max_path_len, path_len)
            # return path_len,
            pass

        current_pos += 1

    return max_path_len,


# %%


def mate(horse1: list[int], horse2: list[int]) -> list[int]:
    """Función para realizar el cruce de individuos"""
    colt = [-1 for _ in range(len(horse1))]
    not_used = set(range(len(colt)))
    for idx in range(len(colt)):
        selected_horse = random.randint(0, 1)
        if selected_horse == 0:
            new_att = horse1[idx]
        else:
            new_att = horse2[idx]

        if new_att in not_used:
            colt[idx] = new_att
            not_used.remove(new_att)

    not_used = random.sample(list(not_used), len(not_used))
    for idx in range(len(colt)):
        if colt[idx] == -1:
            colt[idx] = not_used.pop()

    return colt


# %%

toolbox.register("evaluate", fitness)
toolbox.register("mate", mate)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=INDP)
toolbox.register("select", tools.selTournament, tournsize=3)

# %% [markdown]
# # Función de algoritmo genético.

# %%


def execute_genetic_algorithm(toolbox: base.Toolbox, pop_size: int, num_generations: int, CXPB: float, MUTPB: float, debug: bool = False) -> tuple[int, list, bool]:
    pop = toolbox.population(n=pop_size)
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    fits = [ind.fitness.values[0] for ind in pop]

    converged = False
    iter = tqdm(range(num_generations),
                desc=f"Max: {max(fits):.2f} | Avg: {sum(fits) / len(fits):.2f} | Min: {min(fits):.2f}")
    for num_it in iter:
        iter.desc = f"Max: {max(fits):.2f} | Avg: {sum(fits) / len(fits):.2f} | Min: {min(fits):.2f}"
        if debug:
            pop.sort(key=lambda ind: ind.fitness.values, reverse=True)
            # Mostramos los mejores individuos de la población para cada iteración (si debug está activado)
            print(f"{num_it}: {max(fits)})")
            draw_chessboard(pop[0])

        # ha pasado por todas las casillas
        if max(fits) >= COL * FIL - 1:
            converged = True
            break

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # Por cada par de individuos comprobamos si los cruzamos
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            # Comprobamos por cada individuo si debe mutar
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        # Reevaluamos los individuos no validos
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

        fits = [ind.fitness.values[0] for ind in pop]

    return num_it, pop, converged

# %% [markdown]
# Ejecutamos el algoritmo con una población inicial de 25 individuos, y un máximo de 100 iteraciones.
#


# %%
num_it, final_pop, converged = execute_genetic_algorithm(toolbox, 250, 100000000, CXPB, MUTPB, False)
final_pop.sort(key=lambda ind: ind.fitness.values, reverse=True)

print(f"{num_it=} | {converged=} | {final_pop[0].fitness.values=}")
draw_chessboard(final_pop[0])


# %% [markdown]
# ## Experimentamos variando la probabilidad de mutación con el índice

# %%


def experiment_varying_indpb(toolbox: base.Toolbox, pop_size: int, num_generations: int, cxpb: float, mutpb: float, num_runs: int = 5):
    indpb_values = np.linspace(0.0, 1.0, 20)
    results = []

    for indpb in indpb_values:
        # Registramos la mutacion con el nuevo valor de indpb
        toolbox.unregister("mutate")
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=indpb)

        min_fits_list = []
        max_fits_list = []
        mean_list = []
        std_list = []
        num_it_list = []

        for _ in range(num_runs):
            num_it, pop, converged = execute_genetic_algorithm(toolbox, pop_size, num_generations, cxpb, mutpb)
            fits = [ind.fitness.values[0] for ind in pop]
            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5

            min_fits_list.append(min(fits))
            max_fits_list.append(max(fits))
            mean_list.append(mean)
            std_list.append(std)
            num_it_list.append(num_it)

        # Calculamos medias
        avg_min_fits = np.mean(min_fits_list)
        avg_max_fits = np.mean(max_fits_list)
        avg_mean = np.mean(mean_list)
        avg_std = np.mean(std_list)
        avg_num_it = np.mean(num_it_list)

        stats = (avg_min_fits, avg_max_fits, avg_mean, avg_std, avg_num_it)
        results.append((indpb, stats))

    return results


# %%
results = experiment_varying_indpb(toolbox, pop_size=POP_LEN, num_generations=GENS, cxpb=CXPB, mutpb=MUTPB, num_runs=5)

# %%


def plot_indpb_results(results):
    indpb_vals = [r[0] for r in results]
    min_vals = [r[1][0] for r in results]
    max_vals = [r[1][1] for r in results]
    mean_vals = [r[1][2] for r in results]
    std_vals = [r[1][3] for r in results]
    num_it_vals = [r[1][4] for r in results]

    plt.figure(figsize=(12, 8))

    # Subplot 1 - Number of Iterations
    plt.subplot(2, 2, 1)
    plt.plot(indpb_vals, num_it_vals, marker='o')
    plt.title("Iterations to Converge vs indpb")
    plt.xlabel("indpb")
    plt.ylabel("Number of Iterations")
    plt.grid(True)

    # Encontramos el indpb con menor número de iteraciones
    min_it = min(num_it_vals)
    min_index = num_it_vals.index(min_it)
    x_val = indpb_vals[min_index]

    # Línea vertical para el indpb
    plt.axvline(x=x_val, color='red', linestyle='--')
    y_lower, y_upper = plt.ylim()
    plt.text(x_val, y_lower - 0.1 * (y_upper - y_lower),
             f"{x_val:.2f}",
             color='red', ha='center', va='top')

    # Linea horizontal para el numero mínimo de iteraciones
    plt.axhline(y=min_it, color='red', linestyle='--')
    plt.text(min(indpb_vals), min_it,
             f"{int(min_it)}", color='red', ha='left', va='bottom')

    # Subplot 2 - Mean Fitness
    plt.subplot(2, 2, 2)
    plt.plot(indpb_vals, mean_vals, marker='o', color='orange')
    plt.title("Mean Fitness vs indpb")
    plt.xlabel("indpb")
    plt.ylabel("Mean Fitness")
    plt.grid(True)

    # Encontrar el indpb con la mayor media de fitness
    max_mean = max(mean_vals)
    max_index = mean_vals.index(max_mean)
    x_val = indpb_vals[max_index]

    # Línea vertical para el indpb
    plt.axvline(x=x_val, color='red', linestyle='--')
    y_lower, y_upper = plt.ylim()
    plt.text(x_val, y_lower - 0.1 * (y_upper - y_lower),
             f"{x_val:.2f}", color='red', ha='center', va='top')

    # Linea horizontal para el máximo de las medias de fitness
    plt.axhline(y=max_mean, color='red', linestyle='--')
    plt.text(min(indpb_vals), max_mean,
             f"{max_mean:.2f}", color='red', ha='left', va='bottom')

    # Subplot 3 - Min Fitness
    plt.subplot(2, 2, 3)
    plt.plot(indpb_vals, min_vals, marker='o', color='green')
    plt.title("Min Fitness vs indpb")
    plt.xlabel("indpb")
    plt.ylabel("Min Fitness")
    plt.grid(True)

    # Encontramos el indpb con el mayor mínimo de fitness
    max_min = max(min_vals)
    max_index = min_vals.index(max_min)
    x_val = indpb_vals[max_index]

    # Línea vertical para el indpb
    plt.axvline(x=x_val, color='red', linestyle='--')
    y_lower, y_upper = plt.ylim()
    plt.text(x_val, y_lower - 0.1 * (y_upper - y_lower),
             f"{x_val:.2f}",
             color='red', ha='center', va='top')

    # Linea horizontal para el mayor valor del mínimo de fitness
    plt.axhline(y=max_min, color='red', linestyle='--')
    plt.text(min(indpb_vals), max_min,
             f"{max_min:.2f}", color='red', ha='left', va='bottom')

    # Subplot 4 - Std Dev
    plt.subplot(2, 2, 4)
    plt.plot(indpb_vals, std_vals, marker='o', color='red')
    plt.title("Std Dev of Fitness vs indpb")
    plt.xlabel("indpb")
    plt.ylabel("Standard Deviation")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


# %%
plot_indpb_results(results)

# %% [markdown]
# ## Experimentamos cambiando el método de selección

# %%


def experiment_varying_selection(toolbox: base.Toolbox, pop_size: int, num_generations: int, cxpb: float, mutpb: float, num_runs: int = 5):
    # Métodos de selección
    selection_methods = {
        "Random": tools.selRandom,
        "Roulette": tools.selRoulette,
        "Tournament": lambda individuals, k: tools.selTournament(individuals, k, tournsize=3),
        "Best": tools.selBest,
        "Worst": tools.selWorst
    }

    results = []
    # Iteramos con todos los métodos para obtener información
    for name, method in selection_methods.items():
        toolbox.unregister("select")
        toolbox.register("select", method)

        print(f"\nRunning selection method: {name}")
        min_fits_list = []
        max_fits_list = []
        mean_list = []
        std_list = []
        num_it_list = []

        for _ in range(num_runs):
            num_it, pop, converged = execute_genetic_algorithm(toolbox, pop_size, num_generations, cxpb, mutpb)
            fits = [ind.fitness.values[0] for ind in pop]
            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5

            min_fits_list.append(min(fits))
            max_fits_list.append(max(fits))
            mean_list.append(mean)
            std_list.append(std)
            num_it_list.append(num_it)

        # Calculamos medias
        avg_min_fits = np.mean(min_fits_list)
        avg_max_fits = np.mean(max_fits_list)
        avg_mean = np.mean(mean_list)
        avg_std = np.mean(std_list)
        avg_num_it = np.mean(num_it_list)

        stats = (avg_min_fits, avg_max_fits, avg_mean, avg_std, avg_num_it)
        results.append((name, stats))

    return results

# %%


def plot_selection_results(results):
    """ Mostramos las gráficas con los resultados. """
    names = [r[0] for r in results]
    min_vals = [r[1][0] for r in results]
    max_vals = [r[1][1] for r in results]
    mean_vals = [r[1][2] for r in results]
    std_vals = [r[1][3] for r in results]
    num_it_vals = [r[1][4] for r in results]

    x = np.arange(len(names))

    plt.figure(figsize=(12, 8))

    # Subplot 1 - Number of Iterations
    plt.subplot(2, 2, 1)
    plt.bar(x, num_it_vals, color='skyblue')
    plt.xticks(x, names)
    plt.title("Iterations to Converge por método de selección")
    plt.ylabel("Number of Iterations")

    # Señalamos el método con el menor número de iteraciones
    min_it = min(num_it_vals)
    min_index = num_it_vals.index(min_it)
    plt.text(min_index, min_it, f"{int(min_it)}", color='red', ha='center', va='bottom')

    # Subplot 2 - Mean Fitness
    plt.subplot(2, 2, 2)
    plt.bar(x, mean_vals, color='orange')
    plt.xticks(x, names)
    plt.title("Mean Fitness por método de selección")
    plt.ylabel("Mean Fitness")

    # Señalamos el método con el mayor valor de fitness medio
    max_mean = max(mean_vals)
    max_index = mean_vals.index(max_mean)
    plt.text(max_index, max_mean, f"{max_mean:.2f}", color='red', ha='center', va='bottom')

    # Subplot 3 - Min Fitness
    plt.subplot(2, 2, 3)
    plt.bar(x, min_vals, color='green')
    plt.xticks(x, names)
    plt.title("Min Fitness por método de selección")
    plt.ylabel("Min Fitness")

    # Señalamos el método con el mayor valor de fitness mínimo
    max_min = max(min_vals)
    max_index = min_vals.index(max_min)
    plt.text(max_index, max_min, f"{max_min:.2f}", color='red', ha='center', va='bottom')

    # Subplot 4 - Std Dev
    plt.subplot(2, 2, 4)
    plt.bar(x, std_vals, color='red')
    plt.xticks(x, names)
    plt.title("Std Dev por método de selección")
    plt.ylabel("Standard Deviation")

    plt.tight_layout()
    plt.show()


# %%
results = experiment_varying_selection(toolbox, POP_LEN, GENS, CXPB, MUTPB, num_runs=5)

# %%
plot_selection_results(results)

# %% [markdown]
# # Optimización de parametros

# %%


def show_parameter_changes(
    x: np.ndarray,
    y: np.ndarray,
    function: Callable[[float, float], tuple[float, bool]],
    x_label: str,
    y_label: str
):
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    failures = []

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            iters, _, converged = function(X[i, j], Y[i, j])
            Z[i, j] = iters
            if not converged:
                failures.append((X[i, j], Y[i, j], iters))

    fig, axes = plt.subplots(
        1, 3,
        subplot_kw={'projection': '3d'},
        figsize=(18, 6),
        constrained_layout=True
    )

    view_angles = [
        (30, 45),
        (60, 120),
        (20, 200),
    ]

    zmin = np.min(Z)
    zmax = np.max(Z)

    red_dot_proxy = plt.Line2D([0], [0], linestyle="none", marker='o', color='red', label='No convergencia')

    for idx, (ax, (elev, azim)) in enumerate(zip(axes, view_angles), start=1):
        surf = ax.plot_surface(
            X, Y, Z,
            cmap='viridis',
            linewidth=0,
            antialiased=True,
            rcount=100,
            ccount=100,
            vmin=zmin,
            vmax=zmax
        )

        if failures:
            fx, fy, fz = zip(*failures)
            ax.scatter(
                fx, fy, fz,
                color='red',
                s=50,
                depthshade=True
            )

        ax.set_title(f'View {idx}: Elev={elev}, Azim={azim}', pad=10)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_zlabel('Iteraciones')
        ax.set_zlim(zmin, zmax)
        ax.view_init(elev=elev, azim=azim)

    fig.colorbar(
        surf,
        ax=axes,
        shrink=0.6,
        aspect=20,
        pad=0.05,
        label='Iteraciones'
    )

    fig.legend(
        handles=[red_dot_proxy],
        loc='upper right',
        bbox_to_anchor=(1.02, 1.02),
        borderaxespad=0.0
    )

    plt.show()


# %% [markdown]
# ## Probabilidad de Cruce y Mutación

# %%
show_parameter_changes(
    np.arange(0.0, 1, 0.05),
    np.arange(0.0, 1, 0.05),
    lambda CXPB, MUTPB: execute_genetic_algorithm(toolbox, 10, 2500, CXPB, MUTPB),
    'Probabilidad de cruce (CXPB)',
    'Probabilidad de mutación (MUTPB)'
)

# %% [markdown]
# ## Tamaño de la población y cantidad de iteraciones

# %%
show_parameter_changes(
    np.arange(10, 500, 10),
    np.arange(100, 1000, 100),
    lambda POP_LEN, GENS: execute_genetic_algorithm(toolbox, POP_LEN, GENS, CXPB, MUTPB),
    'Tamaño de la población (POP_LEN)',
    'Número de generaciones (GENS)'
)
