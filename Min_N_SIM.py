import numpy as np
import scipy.stats as stats
import math
from main import simulate_data_single_run
from src.datatypes import Schedule_Algo, Status


def run_model(run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed):
    """
    Simulate a run of the model.
    If the model fails or returns NaN, it should return None to handle the errors.
    Returns a single metric from simulate_data_single_run.
    """
    try:
        value = simulate_data_single_run(run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)[3]
        if np.isnan(value):  # Check for NaN
            return None
        return value
    except Exception:
        return None


def calculate_n(std_dev, margin_of_error, alpha):
    """
    Calculate the number of simulation runs (n) required for a given confidence interval.
    n = (z_{1-alpha/2} * S / \ell)^2
    """
    if np.isnan(std_dev):
        raise ValueError("Standard deviation is NaN, check simulation outputs.")
    z_score = stats.norm.ppf(1 - alpha / 2)
    n = (z_score * std_dev / margin_of_error) ** 2
    return math.ceil(n)


def estimate_required_runs(sim_input, margin_of_error, alpha, initial_runs=100):
    """
    Sequentially run the model until the half-width of the (1-alpha) CI
    for the sample mean U_bar is less than the desired margin_of_error \ell.

    Returns:
      U_bar: sample mean of results
      S: sample standard deviation of results
      n: required number of runs (metering condition)
      half_width: z_{1-alpha/2} * S / sqrt(N)
      total_runs: total valid runs generated
      total_attempts: total model invocations (including failures)
    """
    results = []
    total_attempts = 0

    # Step 1 & 2: collect initial_runs valid results
    while len(results) < initial_runs:
        total_attempts += 1
        value = run_model(sim_input[0], sim_input[1], sim_input[2], sim_input[3], sim_input[4], sim_input[5])
        if value is not None:
            results.append(value)
        print(f"Attempts: {total_attempts}, valid: {len(results)}")

    # Initial statistics
    U_bar = np.mean(results)
    S = np.std(results, ddof=1)
    z = stats.norm.ppf(1 - alpha / 2)
    half_width = z * S / math.sqrt(len(results))
    # Initial required sample size
    n = calculate_n(S, margin_of_error, alpha)

    # Step 5 & 6: iterate until half-width criterion met
    while half_width >= margin_of_error:
        # Determine additional runs needed
        additional = n - len(results)
        print(f"Current N={len(results)}, required n={n}, adding {additional} runs.")

        # Run additional simulations
        for _ in range(additional):
            value = run_model(sim_input[0], sim_input[1], sim_input[2], sim_input[3], sim_input[4], sim_input[5])

            if value is not None:
                results.append(value)
            total_attempts += 1

        # Update statistics
        U_bar = np.mean(results)
        S = np.std(results, ddof=1)
        half_width = z * S / math.sqrt(len(results))
        n = calculate_n(S, margin_of_error, alpha)

    total_runs = len(results)
    return U_bar, S, n, half_width, total_runs, total_attempts


if __name__ == "__main__":
    margin_of_error = 5               # desired half-width
    alpha = 0.05                      # for 95% CI

    run_time = 6 * 60 * 60            # Length of simulation                               [s]
    ac_freq = 20 * 60                 # Frequency of aircraft arrival                      [s]  20, 30, 40
    taxi_margin = 7 * 60              # Time margin for aircraft to be moved from A to B   [s]  10, 15, 20
    loading_time = 40 * 60            # Time spent by aircraft at gate                     [s]  40, 50, 60
    scheduler = Schedule_Algo.greedy  # Algorithm used to manage tug schedule               [-]
    rng_seed = -1                     # Seed used to generate random variables             [-]

    sim_input = [run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed]
    U_bar, S, n, half_width, runs, attempts = estimate_required_runs(sim_input, margin_of_error, alpha)

    print(f"Sample mean U_bar from {runs} runs: {U_bar:.2f}")
    print(f"Sample standard deviation S: {S:.2f}")
    print(f"Half-width: {half_width:.2f} (< {margin_of_error})")
    print(f"Required n: {n}")
    print(f"Total attempts (incl. failures): {attempts}")
