from src.datatypes import Schedule_Algo, Status
from src.environment import Airport
from src.visulization import Run_visualization  # noqa: F401
from src.simulation import run_simulation # noqa: F401
from SIM_P_Reader import parse_multiple_runs, parse_single_run
from loguru import logger
import sys


def simulate_data_multiple_runs(runs, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed,inc_rng=False):

    logger.remove()
    logger.add(sys.stderr, level="SUCCESS")
    logger.add("runlog.txt", mode="w", level="DEBUG")

    x_dim = 900  # Width of window
    y_dim = 780  # Height of window
    window_dims = (x_dim, y_dim)

    airport = Airport("baseline_airport.json", window_dims)

    for i in range(runs):
        logger.info(f"=== STARTING SIM RUN {i} ===")
        if inc_rng:
            new_rng = rng_seed + i
        else:
            new_rng = rng_seed
        run_simulation(airport, run_time, ac_freq, taxi_margin, loading_time, scheduler, new_rng)
        print(f"SIM RUN: {i+1}/{runs}")

    results = parse_multiple_runs("runlog.txt")

    for item in results:
        item["run_time"] = run_time
        item["ac_freq"] = ac_freq
        item["taxi_margin"] = taxi_margin
        item["loading_time"] = loading_time
        item["scheduler"] = str(scheduler)
        item["rng_seed"] = rng_seed

    succesfull_sim_str = "Status.Success"
    n_successes = str([item['simulation_end_result'] for item in results].count(succesfull_sim_str)) + "/" + str(runs)
    per_successes = float([item['simulation_end_result'] for item in results].count(succesfull_sim_str)/len(results))
    print(f"SIM RUN SUCCESS: {n_successes}, {per_successes*100}%")


    return results

def simulate_data_single_run(run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed):

    logger.remove()
    logger.add(sys.stderr, level="SUCCESS")
    logger.add("runlog.txt", mode="w", level="DEBUG")

    x_dim = 900  # Width of window
    y_dim = 780  # Height of window
    window_dims = (x_dim, y_dim)

    simulate_data_multiple_runs(1, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)[0]
    data=parse_single_run() 
    min_tugs = data['min_tugs']
    util_pct_tugs = data['util_pct']
    avg_iddle_t_per_ac = data['avg_wait_arr'] + data['avg_wait_dep']
    avg_taxi_t_per_ac = data['avg_taxi_arr'] + data['avg_taxi_dep']
    simulation_end_result = str(data["status"])

    # print(f"Minimum number of tugs:            {min_tugs}")
    # print(f"Utilization % of tugs:             {util_pct_tugs}")
    # print(f"Average iddle time per aircraft:   {avg_iddle_t_per_ac}")
    # print(f"Average taxi time per aircraft:    {avg_taxi_t_per_ac}")
    # print(f"Reason for Simulation Termination: {simulation_end_result}")


    return min_tugs, util_pct_tugs, avg_iddle_t_per_ac, avg_taxi_t_per_ac, simulation_end_result



def main():

    # Simulation Inputs
    # -----------------
    x_dim = 900                        # Width of window                                    # [Pixels]
    y_dim = 780                        # Height of window                                   # [Pixels]
    fps = 240                          # Frames per second                                  # [-]
    run_time = 6 * 60 * 60             # Length of simulation                               # [s]
    ac_freq = 10 * 60                  # Frequency of aircraft arrival                      # [s]  20, 30, 40
    taxi_margin = 15 * 60              # Time margin for aircraft to be moved from A to B   # [s]  10, 15, 20
    loading_time = 30 * 60             # Time spent by aircraft at gate                     # [s]  40, 50, 60
    scheduler = Schedule_Algo.genetic   # Time of algorith used to manage tug schedule       # [-]
    rng_seed = 42+12                     # Seed used to generate random variables             # [-]

    # Run Simulations or Visualization
    # --------------------------------

    # Visualization
    # Run_visualization(x_dim, y_dim, fps, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)

    # Simulation
    # print(simulate_data_single_run(run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed))
    simulate_data_multiple_runs(1, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)


if __name__ == "__main__":
    main()
