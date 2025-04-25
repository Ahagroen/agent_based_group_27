import numpy as np
from math import ceil
from scipy.stats import norm
from main import simulate_data_single_run
from src.datatypes import Schedule_Algo

def run_model():
    """
    Simulate one run of the tug/aircraft model.
    Returns:
        float or None: key output metric (e.g. average taxi time per aircraft),
                       or None if the simulation failed.
    """
    try:
        run_time     = 6 * 60 * 60    # [s] length of simulation
        ac_freq      = 10 * 60        # [s] time between arrivals
        taxi_margin  = 20 * 60        # [s] buffer for gate arrival
        loading_time = 30 * 60        # [s] turnaround time at gate
        scheduler    = Schedule_Algo.greedy
        rng_seed     = -1             # no fixed seed

        return simulate_data_single_run(
            run_time,
            ac_freq,
            taxi_margin,
            loading_time,
            scheduler,
            rng_seed
        )[3]

    except Exception:
        return None  # indicate a failed run

def calculate_n(std_dev, margin_of_error, alpha):
    """
    Calculate required total replications so that the half‐width
    of the (1-alpha) CI for the mean is <= margin_of_error.

    Args:
        std_dev (float): observed sample standard deviation (ddof=1)
        margin_of_error (float): target half‐width (same units as the metric)
        alpha (float): significance level (e.g. 0.05 for 95% CI)

    Returns:
        int: required total number of runs
    """
    z = norm.ppf(1 - alpha/2)
    return ceil((z * std_dev / margin_of_error) ** 2)

def estimate_required_runs(margin_of_error, alpha, initial_n=100):
    """
    Estimate how many simulation replications are needed so that the half‐width
    of the (1–alpha) confidence interval for mean tug utilization is below margin_of_error.

    Args:
        margin_of_error (float): desired CI half‐width
        alpha (float): significance level
        initial_n (int): initial batch size

    Returns:
        n_required     (int): theoretical total replications needed (>= valid_runs)
        std_dev        (float): sample standard deviation of collected outputs
        valid_runs     (int): number of successful runs performed
        total_attempts (int): total simulation calls (including failures)
    """
    U = []
    attempts = 0

    # 1) Initial batch
    while len(U) < initial_n:
        attempts += 1
        result = run_model()
        if result is not None:
            U.append(result)

    # 2) Iterative extension
    raw_n_required = None
    while True:
        std_dev = np.std(U, ddof=1)  # sample std (ddof=1)
        z = norm.ppf(1 - alpha/2)
        half_width = z * std_dev / np.sqrt(len(U))
        raw_n_required = calculate_n(std_dev, margin_of_error, alpha)

        if half_width < margin_of_error:
            break

        # collect additional runs until we reach raw_n_required
        while len(U) < raw_n_required:
            attempts += 1
            result = run_model()
            if result is not None:
                U.append(result)

    # ensure we never report fewer required runs than we've already executed
    n_required = max(raw_n_required, len(U))

    return n_required, std_dev, len(U), attempts

# Example usage
if __name__ == "__main__":
    initial_n       = 3     # initial sample size for std estimation
    margin_of_error = 2.0     # desired half‐width
    alpha           = 0.005    # 95% confidence

    n_req, std_dev, valid_runs, total_attempts = \
        estimate_required_runs(margin_of_error, alpha, initial_n)

    print(f"Observed std dev from {valid_runs} runs: {std_dev:.2f}")
    print(f"Required total runs     : {n_req}")
    print(f"Total attempts (incl. failures): {total_attempts}")
