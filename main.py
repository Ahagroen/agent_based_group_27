from src.datatypes import Schedule_Algo, Status
from src.environment import Airport
from src.visulization import Run_visualization  # noqa: F401
from src.simulation import run_simulation # noqa: F401
from SIM_P_Reader import parse_multiple_runs
from loguru import logger
import sys


def simulate_data_multiple_runs(runs, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed):

    logger.remove()
    logger.add(sys.stderr, level="SUCCESS")
    logger.add("runlog.txt", mode="w", level="DEBUG")

    x_dim = 900  # Width of window
    y_dim = 780  # Height of window
    window_dims = (x_dim, y_dim)

    airport = Airport("baseline_airport.json", window_dims)
    carry = []
    for i in range(runs):

        logger.info(f"=== STARTING SIM RUN {i} ===")
        result = run_simulation(airport, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)
        carry.append(result)

    # print(f"num successes: {[x[0] for x in carry].count(Status.Success)},"
    #       f" percentage = {[x[0] for x in carry].count(Status.Success)/len(carry)}")

    return parse_multiple_runs("runlog.txt")

def simulate_data_single_run(run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed):

    logger.remove()
    logger.add(sys.stderr, level="SUCCESS")
    logger.add("runlog.txt", mode="w", level="DEBUG")

    x_dim = 900  # Width of window
    y_dim = 780  # Height of window
    window_dims = (x_dim, y_dim)

    runs = 1

    airport = Airport("baseline_airport.json", window_dims)
    carry = []
    for i in range(runs):

        logger.info(f"=== STARTING SIM RUN {i} ===")
        result = run_simulation(airport, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)
        carry.append(result)

    data = parse_multiple_runs("runlog.txt")[0]

    min_tugs = data['min_tugs']
    util_pct_tugs = data['util_pct']
    avg_iddle_t_per_ac = data['avg_wait_arr'] + data['avg_wait_dep']
    avg_taxi_t_per_ac = data['avg_taxi_arr'] + data['avg_taxi_dep']

    print(f"Minimum number of tugs:            {min_tugs}")
    print(f"Utilization % of tugs:             {util_pct_tugs}")
    print(f"Average iddle time per aircraft:   {avg_iddle_t_per_ac}")
    print(f"Average taxi time per aircraft:    {avg_taxi_t_per_ac}")


    return min_tugs, util_pct_tugs, avg_iddle_t_per_ac, avg_taxi_t_per_ac



def main():

    # Simulation Inputs
    # -----------------
    x_dim = 900                        # Width of window                                # [Pixels]
    y_dim = 780                        # Height of window                               # [Pixels]
    fps = 120                          # Frames per second                              # [-]
    run_time = 6 * 60 * 60             # Length of simulation                           # [s]
    ac_freq = 10 * 60                  # Frequency of aircraft arrival                  # [s]
    taxi_margin = 20 * 60              # Time margin for aircraft to arrive at gate     # [s]
    loading_time = 30 * 60             # Time spent by aircraft at gate                 # [s]
    scheduler = Schedule_Algo.greedy   # Time of algorith used to manage tug schedule   # [-]
    rng_seed = - 1                     # Seed used to generate random variables         # [-]

    # Run Simulations or Visualization
    # --------------------------------

    # Visualization
    # Run_visualization(x_dim, y_dim, fps, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)

    # Simulation
    simulate_data_single_run(run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)



if __name__ == "__main__":
    main()
