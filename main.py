from src.datatypes import Schedule_Algo, Status
from src.environment import Airport
from src.visulization import Run_visualization  # noqa: F401
from src.simulation import run_simulation # noqa: F401
from loguru import logger
import sys


def simulate_data(runs:int):
    logger.remove()
    logger.add(sys.stderr, level="SUCCESS")
    logger.add("runlog.txt", mode="w", level="DEBUG")
    airport = Airport("baseline_airport.json")
    carry = []
    for _ in range(runs):
        run_time = 8 * 60 * 60             # Length of simulation                           # [s]
        ac_freq = 10 * 60                  # Frequency of aircraft arrival                  # [s]
        taxi_margin = 20 * 60              # Time margin for aircraft to arrive at gate     # [s]
        loading_time = 30 * 60             # Time spent by aircraft at gate                 # [s]
        scheduler = Schedule_Algo.greedy   # Time of algorith used to manage tug schedule   # [-]
        rng_seed = 42                      # Seed used to generate random variables         # [-]

        result = run_simulation(airport, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)
        carry.append(result)

    print(f"num successes: {[x[0] for x in carry].count(Status.Success)},"
          f" percentage = {[x[0] for x in carry].count(Status.Success)/len(carry)}")

def main():

    # Simulation Inputs
    # -----------------
    x_dim = 900                        # Width of window                                # [Pixels]
    y_dim = 780                        # Height of window                               # [Pixels]
    fps = 120                          # Frames per second                              # [-]
    run_time = 8 * 60 * 60             # Length of simulation                           # [s]
    ac_freq = 10 * 60                  # Frequency of aircraft arrival                  # [s]
    taxi_margin = 20 * 60              # Time margin for aircraft to arrive at gate     # [s]
    loading_time = 30 * 60             # Time spent by aircraft at gate                 # [s]
    scheduler = Schedule_Algo.greedy   # Time of algorith used to manage tug schedule   # [-]
    rng_seed = 42                      # Seed used to generate random variables         # [-]

    # Run Simulations or Visualization
    # --------------------------------

    # Visualization
    Run_visualization(x_dim, y_dim, fps, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)

    # Simulation
    # simulate_data(25)

if __name__ == "__main__":
    main()
