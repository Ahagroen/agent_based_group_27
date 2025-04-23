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
        result = run_simulation(airport,480*60,10*60,20*60,30*60, Schedule_Algo.greedy, 42)
        carry.append(result)
    print(f"num successes: {[x[0] for x in carry].count(Status.Success)}, percentage = {[x[0] for x in carry].count(Status.Success)/len(carry)}")

def main():

    # Simulation Inputs
    # -----------------
    x_dim = 900
    y_dim = 780
    fps = 120
    run_time = 8 * 60 * 60
    ac_freq = 10 * 60
    taxi_margin = 20 * 60
    loading_time = 30 * 60
    scheduler = Schedule_Algo.greedy
    rng_seed = 42

    Run_visualization(x_dim, y_dim, fps, run_time, ac_freq, taxi_margin, loading_time, scheduler, rng_seed)
    # simulate_data(25)

if __name__ == "__main__":
    main()
