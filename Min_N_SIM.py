import numpy as np
import scipy.stats as stats
import math
from main import simulate_data_single_run
from src.datatypes import Schedule_Algo, Status


def run_model():
    """
    Simulate a run of the model.
    If the model fails, it should return None to handle the errors.
    """
    try:
        run_time = 6 * 60 * 60  # Length of simulation                                     # [s]
        ac_freq = 10 * 60  # Frequency of aircraft arrival                                 # [s]
        taxi_margin = 20 * 60  # Time margin for aircraft to arrive at gate                # [s]
        loading_time = 30 * 60  # Time spent by aircraft at gate                           # [s]
        scheduler = Schedule_Algo.greedy  # Time of algorith used to manage tug schedule   # [-]
        rng_seed = - 1  # Seed used to generate random variables                           # [-]

        return simulate_data_single_run(run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)[3]

    except Exception:
        return None  # If the model fails, return None to indicate failure


    # min_tugs, util_pct_tugs, avg_iddle_t_per_ac, avg_taxi_t_per_ac


def calculate_n(std_dev, margin_of_error, alpha):
    """
    Calculate the number of simulation runs (n) required for a given confidence interval.

    Parameters:
    std_dev (float): The standard deviation of the simulation results.
    margin_of_error (float): The desired margin of error for the estimate.
    alpha (float): The significance level (e.g., 0.05 for 95% confidence interval).

    Returns:
    int: The required number of simulation runs (n).
    """
    # Calculate the z-score for the given alpha (for two-tailed test)
    z_score = stats.norm.ppf(1 - alpha / 2)

    # Calculate the required number of runs (n) using the formula
    n = (z_score * std_dev / margin_of_error) ** 2

    return math.ceil(n)  # Round up to the nearest integer


def estimate_required_runs(num_simulations, margin_of_error, alpha):
    """
    Run the model multiple times, calculate the standard deviation of the outputs,
    and estimate the required number of runs.

    Parameters:
    num_simulations (int): Number of times to run the model to calculate the standard deviation.
    margin_of_error (float): Desired margin of error for the estimate.
    alpha (float): Significance level (e.g., 0.05 for 95% confidence).

    Returns:
    int: The required number of runs (n).
    """
    results = []
    attempts = 0

    # Keep running the model until we get valid results for the required number of simulations
    while len(results) < num_simulations:
        attempts += 1
        result = run_model()
        if result is not None:
            results.append(result)


        print(f"Attempts so far: {attempts}, valid runs: {len(results)}")

    # Calculate the standard deviation of the results
    std_dev = np.std(results)

    # Calculate the required number of runs based on the standard deviation
    n = calculate_n(std_dev, margin_of_error, alpha)

    return n, std_dev, len(results), attempts  # Return n, std_dev, valid runs, and total attempts


# Example usage
num_simulations = 100 # Number of valid simulations to run for standard deviation calculation
margin_of_error = 5  # Desired margin of error (e.g., 5 for 5% of the mean)
alpha = 0.05         # Significance level for 95% confidence

n, std_dev, valid_runs, total_attempts = estimate_required_runs(num_simulations, margin_of_error, alpha)
print("")
print(f"Calculated standard deviation from {valid_runs} valid runs: {std_dev:.2f}")
print(f"Required number of runs for desired margin of error: {n}")
print(f"Total attempts made (including failed runs): {total_attempts}")
print("")