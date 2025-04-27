import pandas as pd
from src.datatypes import Schedule_Algo, Status
from main import simulate_data_single_run

def mean_outputs(data, min_runs_ac_freq_min):
    run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed = data

    # Define the columns
    # ------------------
    columns = [
        "ac_freq",               # Frequency of aircraft arrival                  # [s]
        "taxi_margin",           # Time margin for aircraft to move from A to B   # [s]
        "loading_time",          # Time spent by aircraft at gate                 # [s]
        "scheduler",             # Time of algorith used to manage tug schedule   # [-]
        "min_tugs",              # Minimum number of tugs needed                  # [-]
        "util_pct_tugs",         # Tug utilization percentage                     # [%]
        "avg_iddle_t_per_ac",    # Average idle time per aircraft                 # [-]
        "avg_taxi_t_per_ac",      # Average taxi time per aircraft                 # [-]
        "simulation_end_result"  # Reason for ending simulation                   # [-]
    ]

    # Create an empty DataFrame with the specified columns
    # ----------------------------------------------------
    df = pd.DataFrame(columns=columns)

    for i in range(min_runs_ac_freq_min):

        try:
            r1, r2, r3, r4, r5 = simulate_data_single_run(run_time,
                                                          ac_freq,
                                                          taxi_margin,
                                                          loading_time,
                                                          scheduler,
                                                          rng_seed)

            new_data = {"ac_freq": ac_freq,
                        "taxi_margin": taxi_margin,
                        "loading_time": loading_time,
                        "scheduler": str(Schedule_Algo.greedy),
                        "min_tugs": r1,
                        "util_pct_tugs": r2,
                        "avg_iddle_t_per_ac": r3,
                        "avg_taxi_t_per_ac": r4,
                        "simulation_end_result": r5}

            df.loc[len(df)] = new_data

        except Exception:

            new_data = {
                "ac_freq": ac_freq,
                "taxi_margin": taxi_margin,
                "loading_time": loading_time,
                "scheduler": str(scheduler),
                "min_tugs": None,
                "util_pct_tugs": None,
                "avg_iddle_t_per_ac": None,
                "avg_taxi_t_per_ac": None,
                "simulation_end_result": r5
            }

            df.loc[len(df)] = new_data

    print(df)

    mean_results = {
        "mean_min_tugs": df["min_tugs"].mean(),
        "mean_util_pct_tugs": df["util_pct_tugs"].mean(),
        "mean_avg_iddle_t_per_ac": df["avg_iddle_t_per_ac"].mean(),
        "mean_avg_taxi_t_per_ac": df["avg_taxi_t_per_ac"].mean(),
    }

    return mean_results


x_dim = 900                          # Width of window                                    # [Pixels]
y_dim = 780                          # Height of window                                   # [Pixels]
fps = 240                            # Frames per second                                  # [-]
run_time = 6 * 60 * 60               # Length of simulation                               # [s]
ac_freq = 30 * 60                    # Frequency of aircraft arrival                      # [s]  20, 30, 40
taxi_margin = 15 * 60                # Time margin for aircraft to be moved from A to B  # [s]  10, 15, 20
loading_time = 50 * 60               # Time spent by aircraft at gate                     # [s]  40, 50, 60
scheduler = Schedule_Algo.greedy     # Time of algorith used to manage tug schedule       # [-]
rng_seed = - 1                       # Seed used to generate random variables             # [-]


data = [run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed]


print(mean_outputs(data, 2))