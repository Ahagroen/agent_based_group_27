import numpy as np
import scipy.stats as stats
import math
from main import simulate_data_single_run
from src.datatypes import Schedule_Algo, Status
import pandas as pd
from Min_N_SIM import estimate_required_runs


# =======================================
# Creating Pandas Dataframe to store data
# =======================================

def mean_outputs(data, min_runs_ac_freq_min):
    run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed = data

    run_n = 1

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
        "avg_taxi_t_per_ac",      # Average taxi time per aircraft                # [-]
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

        finally:
            print(run_n)
            run_n += 1

    mean_results = {
        "mean_min_tugs": df["min_tugs"].mean(),
        "mean_util_pct_tugs": df["util_pct_tugs"].mean(),
        "mean_avg_iddle_t_per_ac": df["avg_iddle_t_per_ac"].mean(),
        "mean_avg_taxi_t_per_ac": df["avg_taxi_t_per_ac"].mean(),
    }

    return mean_results

# ============================================================
# STEP 1 - Set Baseline Simulation Inputs & Range of Variation
# ============================================================

# Baseline Simulation Inputs
# --------------------------
x_dim = 900                          # Width of window                                    # [Pixels]
y_dim = 780                          # Height of window                                   # [Pixels]
fps = 240                            # Frames per second                                  # [-]
run_time = 6 * 60 * 60               # Length of simulation                               # [s]
ac_freq = 30 * 60                    # Frequency of aircraft arrival                      # [s]  20, 30, 40
taxi_margin = 15 * 60                # Time margin for aircraft to be moved from A to B   # [s]  10, 15, 20
loading_time = 50 * 60               # Time spent by aircraft at gate                     # [s]  40, 50, 60
scheduler = Schedule_Algo.greedy     # Time of algorith used to manage tug schedule       # [-]
rng_seed = - 1                       # Seed used to generate random variables             # [-]

# Variation Range
# ---------------
Var_Range = 0.1

Range_ac_freq = [ac_freq*(1-Var_Range), ac_freq, ac_freq*(1+Var_Range)]
Range_taxi_margin = [taxi_margin*(1-Var_Range), taxi_margin, taxi_margin*(1+Var_Range)]
Range_loading_time = [loading_time*(1-Var_Range), loading_time, loading_time*(1+Var_Range)]

# =======================================
# STEP 2 - Estimate mean of model outputs
# =======================================

# Determine number of simulation runs to get mean of outputs
# ----------------------------------------------------------
margin_of_error = 5               # desired half-width
alpha = 0.05                      # for 95% CI
initial_runs = 100
hardcoded_n_runs = 1

# ac_freq
# -------
sim_input_1 = [run_time, Range_ac_freq[0], taxi_margin, loading_time, scheduler, rng_seed]
sim_input_2 = [run_time, Range_ac_freq[1], taxi_margin, loading_time, scheduler, rng_seed]
sim_input_3 = [run_time, Range_ac_freq[2], taxi_margin, loading_time, scheduler, rng_seed]

# min_runs_ac_freq_min = estimate_required_runs(sim_input_1, margin_of_error, alpha, initial_runs)
# min_runs_ac_freq_mid = estimate_required_runs(sim_input_2, margin_of_error, alpha, initial_runs)
# min_runs_ac_freq_max = estimate_required_runs(sim_input_3, margin_of_error, alpha, initial_runs)

min_runs_ac_freq_min = hardcoded_n_runs
min_runs_ac_freq_mid = hardcoded_n_runs
min_runs_ac_freq_max = hardcoded_n_runs

print(f"")
print(f"Minimum number of runs for min_runs_ac_freq_min: {min_runs_ac_freq_min}")
print(f"Minimum number of runs for min_runs_ac_freq_mid: {min_runs_ac_freq_mid}")
print(f"Minimum number of runs for min_runs_ac_freq_max: {min_runs_ac_freq_max}")
print(f"")

mean_results_1 = mean_outputs(sim_input_1, min_runs_ac_freq_min)
mean_results_2 = mean_outputs(sim_input_2, min_runs_ac_freq_mid)
mean_results_3 = mean_outputs(sim_input_2, min_runs_ac_freq_max)

# taxi_margin
# -----------
sim_input_4 = [run_time, ac_freq, Range_taxi_margin[0], loading_time, scheduler, rng_seed]
sim_input_5 = [run_time, ac_freq, Range_taxi_margin[1], loading_time, scheduler, rng_seed]
sim_input_6 = [run_time, ac_freq, Range_taxi_margin[2], loading_time, scheduler, rng_seed]

# min_runs_taxi_margin_min = estimate_required_runs(sim_input_4, margin_of_error, alpha, initial_runs)
# min_runs_taxi_margin_mid = estimate_required_runs(sim_input_5, margin_of_error, alpha, initial_runs)
# min_runs_taxi_margin_max = estimate_required_runs(sim_input_6, margin_of_error, alpha, initial_runs)

min_runs_taxi_margin_min = hardcoded_n_runs
min_runs_taxi_margin_mid = hardcoded_n_runs
min_runs_taxi_margin_max = hardcoded_n_runs

print(f"")
print(f"Minimum number of runs for min_runs_taxi_margin_min: {min_runs_taxi_margin_min}")
print(f"Minimum number of runs for min_runs_taxi_margin_mid: {min_runs_taxi_margin_mid}")
print(f"Minimum number of runs for min_runs_taxi_margin_max: {min_runs_taxi_margin_max}")
print(f"")

mean_results_4 = mean_outputs(sim_input_4, min_runs_taxi_margin_min)
mean_results_5 = mean_outputs(sim_input_5, min_runs_taxi_margin_mid)
mean_results_6 = mean_outputs(sim_input_6, min_runs_taxi_margin_max)

# loading_time
# ------------
sim_input_7 = [run_time, ac_freq, taxi_margin, Range_loading_time[0], scheduler, rng_seed]
sim_input_8 = [run_time, ac_freq, taxi_margin, Range_loading_time[1], scheduler, rng_seed]
sim_input_9 = [run_time, ac_freq, taxi_margin, Range_loading_time[2], scheduler, rng_seed]

# min_runs_loading_time_min = estimate_required_runs(sim_input_7, margin_of_error, alpha, initial_runs)
# min_runs_loading_time_mid = estimate_required_runs(sim_input_8, margin_of_error, alpha, initial_runs)
# min_runs_loading_time_max = estimate_required_runs(sim_input_9, margin_of_error, alpha, initial_runs)

min_runs_loading_time_min = hardcoded_n_runs
min_runs_loading_time_mid = hardcoded_n_runs
min_runs_loading_time_max = hardcoded_n_runs

print(f"")
print(f"Minimum number of runs for min_runs_loading_time_min: {min_runs_loading_time_min}")
print(f"Minimum number of runs for min_runs_loading_time_mid: {min_runs_loading_time_mid}")
print(f"Minimum number of runs for min_runs_loading_time_max: {min_runs_loading_time_max}")
print(f"")

mean_results_7 = mean_outputs(sim_input_7, min_runs_loading_time_min)
mean_results_8 = mean_outputs(sim_input_8, min_runs_loading_time_mid)
mean_results_9 = mean_outputs(sim_input_9, min_runs_loading_time_max)


# ================================
# STEP 3 - Calculate Sensitivities
# ================================

def calculate_S(P, dP, X_minus, X, X_plus):
    """"
    X: estimate of mean of ref value           (Output)
    X_minus: estimate of mean of smaller value (Output)
    X_plus: estimate of mean of bigger value   (Output)
    P: Parameter reference value               (Input)
    dP: Amount to vary reference value         (Input)
    """

    S_plus = (X_plus - X) / (dP / P)
    S_minus = (X - X_minus) / (dP / P)
    return S_minus, S_plus

# Sensitivity for ac_freq
# -----------------------

S_ac_freq_vs_min_tugs =           calculate_S(ac_freq,
                                              ac_freq * Var_Range,
                                              mean_results_1["mean_min_tugs"],
                                              mean_results_2["mean_min_tugs"],
                                              mean_results_3["mean_min_tugs"])

S_ac_freq_vs_util_pct_tugs =      calculate_S(ac_freq,
                                              ac_freq * Var_Range,
                                              mean_results_1["mean_util_pct_tugs"],
                                              mean_results_2["mean_util_pct_tugs"],
                                              mean_results_3["mean_util_pct_tugs"])

S_ac_freq_vs_avg_iddle_t_per_ac = calculate_S(ac_freq,
                                              ac_freq * Var_Range,
                                              mean_results_1["mean_avg_iddle_t_per_ac"],
                                              mean_results_2["mean_avg_iddle_t_per_ac"],
                                              mean_results_3["mean_avg_iddle_t_per_ac"])

S_ac_freq_vs_avg_taxi_t_per_ac =  calculate_S(ac_freq,
                                              ac_freq * Var_Range,
                                              mean_results_1["mean_avg_taxi_t_per_ac"],
                                              mean_results_2["mean_avg_taxi_t_per_ac"],
                                              mean_results_3["mean_avg_taxi_t_per_ac"])

# Sensitivity for taxi_margin
# ---------------------------

S_taxi_margin_vs_min_tugs =           calculate_S(taxi_margin,
                                                  taxi_margin * Var_Range,
                                                  mean_results_4["mean_min_tugs"],
                                                  mean_results_5["mean_min_tugs"],
                                                  mean_results_6["mean_min_tugs"])

S_taxi_margin_vs_util_pct_tugs =      calculate_S(taxi_margin,
                                                  taxi_margin * Var_Range,
                                                  mean_results_4["mean_util_pct_tugs"],
                                                  mean_results_5["mean_util_pct_tugs"],
                                                  mean_results_6["mean_util_pct_tugs"])

S_taxi_margin_vs_avg_iddle_t_per_ac = calculate_S(taxi_margin,
                                                  taxi_margin * Var_Range,
                                                  mean_results_4["mean_avg_iddle_t_per_ac"],
                                                  mean_results_5["mean_avg_iddle_t_per_ac"],
                                                  mean_results_6["mean_avg_iddle_t_per_ac"])

S_taxi_margin_vs_avg_taxi_t_per_ac =  calculate_S(taxi_margin,
                                                  taxi_margin * Var_Range,
                                                  mean_results_4["mean_avg_taxi_t_per_ac"],
                                                  mean_results_5["mean_avg_taxi_t_per_ac"],
                                                  mean_results_6["mean_avg_taxi_t_per_ac"])

# Sensitivity for loading_time
# ----------------------------

loading_time_vs_min_tugs =           calculate_S(loading_time,
                                                 loading_time * Var_Range,
                                                 mean_results_7["mean_min_tugs"],
                                                 mean_results_8["mean_min_tugs"],
                                                 mean_results_9["mean_min_tugs"])

loading_time_vs_util_pct_tugs =      calculate_S(loading_time,
                                                 loading_time * Var_Range,
                                                 mean_results_7["mean_util_pct_tugs"],
                                                 mean_results_8["mean_util_pct_tugs"],
                                                 mean_results_9["mean_util_pct_tugs"])

loading_time_vs_avg_iddle_t_per_ac = calculate_S(loading_time,
                                                 loading_time * Var_Range,
                                                 mean_results_7["mean_avg_iddle_t_per_ac"],
                                                 mean_results_8["mean_avg_iddle_t_per_ac"],
                                                 mean_results_9["mean_avg_iddle_t_per_ac"])

loading_time_vs_avg_taxi_t_per_ac =  calculate_S(loading_time,
                                                 loading_time * Var_Range,
                                                 mean_results_7["mean_avg_taxi_t_per_ac"],
                                                 mean_results_8["mean_avg_taxi_t_per_ac"],
                                                 mean_results_9["mean_avg_taxi_t_per_ac"])

# Print Sensitivity Results
# -------------------------

# List of (name, value) pairs
sensitivities = [
    ("S_ac_freq_vs_min_tugs",              S_ac_freq_vs_min_tugs),
    ("S_ac_freq_vs_util_pct_tugs",          S_ac_freq_vs_util_pct_tugs),
    ("S_ac_freq_vs_avg_iddle_t_per_ac",     S_ac_freq_vs_avg_iddle_t_per_ac),
    ("S_ac_freq_vs_avg_taxi_t_per_ac",      S_ac_freq_vs_avg_taxi_t_per_ac),

    ("S_taxi_margin_vs_min_tugs",           S_taxi_margin_vs_min_tugs),
    ("S_taxi_margin_vs_util_pct_tugs",      S_taxi_margin_vs_util_pct_tugs),
    ("S_taxi_margin_vs_avg_iddle_t_per_ac", S_taxi_margin_vs_avg_iddle_t_per_ac),
    ("S_taxi_margin_vs_avg_taxi_t_per_ac",  S_taxi_margin_vs_avg_taxi_t_per_ac),

    ("loading_time_vs_min_tugs",            loading_time_vs_min_tugs),
    ("loading_time_vs_util_pct_tugs",       loading_time_vs_util_pct_tugs),
    ("loading_time_vs_avg_iddle_t_per_ac",  loading_time_vs_avg_iddle_t_per_ac),
    ("loading_time_vs_avg_taxi_t_per_ac",   loading_time_vs_avg_taxi_t_per_ac),
]

# Convert to a DataFrame
df = pd.DataFrame(sensitivities, columns=["Metric", "Values"])

# Expand 'Values' into two separate columns for S- and S+
df[['S-', 'S+']] = pd.DataFrame(df['Values'].tolist(), index=df.index)

# Round the S- and S+ values to 2 decimal places
df[['S-', 'S+']] = df[['S-', 'S+']].round(2)

# Center-align the text and print the DataFrame
pd.set_option('display.colheader_justify', 'center')  # Center column headers
print(df[['Metric', 'S-', 'S+']].to_string(index=False, justify='left'))


# Miscelaneous
# ------------
# Save DataFrame to a .txt file with tab-separated values
# df.to_csv("Sensitivity.txt", sep=",", index=False)

# Read Data frame from a .txt file
# df_loaded = pd.read_csv("simulation_output.txt", sep=",")