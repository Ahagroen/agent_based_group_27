import numpy as np
from scipy.stats import ttest_rel
from src.datatypes import Schedule_Algo
from main import simulate_data_single_run  # <-- pas dit aan naar de juiste import

# Simulatie parameters
N_RUNS = 100
BASE_SEED = 42

RUN_TIME = 6 * 60 * 60
AC_FREQ = 2400
TAXI_MARGIN = 1800
LOADING_TIME = 2700

# Scheduler opties
algorithms = {
    "greedy": Schedule_Algo.greedy,
    "aco": Schedule_Algo.aco,
    "genetic": Schedule_Algo.genetic
}

# Resultaten opslaan
results = {key: [] for key in algorithms.keys()}

# Simulaties draaien
for name, scheduler in algorithms.items():
    print(f"\nRunning simulations for {name.upper()}")
    for i in range(N_RUNS):
        seed = BASE_SEED + i
        min_tugs, *_ = simulate_data_single_run(
            RUN_TIME, AC_FREQ, TAXI_MARGIN, LOADING_TIME, scheduler, seed
        )
        results[name].append(min_tugs)

# T-tests uitvoeren
print("\n--- Paired t-tests on min_tugs ---")

def do_ttest(algo1, algo2):
    arr1 = results[algo1]
    arr2 = results[algo2]
    t_stat, p_val = ttest_rel(arr1, arr2)
    print(f"{algo1.upper()} vs {algo2.upper()}: t = {t_stat:.3f}, p = {p_val:.4f}")

do_ttest("greedy", "aco")
do_ttest("greedy", "genetic")
do_ttest("aco", "genetic")
