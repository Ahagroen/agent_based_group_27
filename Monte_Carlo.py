import numpy as np
import scipy.stats as stats
import math
from main import simulate_data_single_run
from src.datatypes import Schedule_Algo, Status
import pandas as pd


# Define the columns
columns = [
    "ac_freq",               # Frequency of aircraft arrival                  # [s]
    "taxi_margin",           # Time margin for aircraft to move from A to B   # [s]
    "loading_time",          # Time spent by aircraft at gate                 # [s]
    "scheduler",             # Time of algorith used to manage tug schedule   # [-]
    "min_tugs",              # Minimum number of tugs needed                  # [-]
    "util_pct_tugs",         # Tug utilization percentage                     # [%]
    "avg_iddle_t_per_ac",    # Average idle time per aircraft                 # [-]
    "avg_taxi_t_per_ac"      # Average taxi time per aircraft                 # [-]
]

# Create an empty DataFrame with the specified columns
df = pd.DataFrame(columns=columns)

# Define the ranges globally or pass them in
i_range = np.arange(5, 50, 5)
j_range = np.arange(5, 50, 5)
k_range = np.arange(5, 50, 5)

def get_progress(i, j, k):
    i_index = np.where(i_range == i)[0][0]
    j_index = np.where(j_range == j)[0][0]
    k_index = np.where(k_range == k)[0][0]

    i_len = len(i_range)
    j_len = len(j_range)
    k_len = len(k_range)

    total = i_len * j_len * k_len
    current = i_index * j_len * k_len + j_index * k_len + k_index + 1

    progress = (current / total) * 100
    print(f"Progress: {progress:.2f}%")



for i in i_range:
    for j in j_range:
        for k in k_range:

            try:
                run_time = 6 * 60 * 60            # Length of simulation                           # [s]
                ac_freq = i * 60                  # Frequency of aircraft arrival                  # [s]
                taxi_margin = j * 60              # Time margin for aircraft to move from A to B   # [s]
                loading_time = k * 60             # Time spent by aircraft at gate                 # [s]
                scheduler = Schedule_Algo.greedy  # Time of algorith used to manage tug schedule   # [-]
                rng_seed = - 1                    # Seed used to generate random variables         # [-]

                min_tugs,\
                util_pct_tugs,\
                avg_iddle_t_per_ac,\
                avg_taxi_t_per_ac = simulate_data_single_run(run_time,
                                                             ac_freq,
                                                             taxi_margin,
                                                             loading_time,
                                                             scheduler,
                                                             rng_seed)

                new_data = {
                    "ac_freq": ac_freq,
                    "taxi_margin": taxi_margin,
                    "loading_time": loading_time,
                    "scheduler": str(Schedule_Algo.greedy),
                    "min_tugs": min_tugs,
                    "util_pct_tugs": util_pct_tugs,
                    "avg_iddle_t_per_ac": avg_iddle_t_per_ac,
                    "avg_taxi_t_per_ac": avg_taxi_t_per_ac
                }

                df.loc[len(df)] = new_data

            except Exception:


                new_data = {
                    "ac_freq": ac_freq,
                    "taxi_margin": taxi_margin,
                    "loading_time": loading_time,
                    "scheduler": str(Schedule_Algo.aco),
                    "min_tugs": None,
                    "util_pct_tugs": None,
                    "avg_iddle_t_per_ac": None,
                    "avg_taxi_t_per_ac": None
                }

                df.loc[len(df)] = new_data

            print("")
            get_progress(i, j, k)
            print(i, j, k)

# Save DataFrame to a .txt file with tab-separated values
df.to_csv("MonteCarlo.txt", sep=",", index=False)

# Read Data frame from a .txt file
# df_loaded = pd.read_csv("simulation_output.txt", sep=",")


