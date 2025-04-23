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
    for _ in range(1):
        result = run_simulation(airport,480*60,10*60,20*60,30*60,Schedule_Algo.greedy)
        carry.append(result)
    print(f"num successes: {[x[0] for x in carry].count(Status.Success)}, percentage = {[x[0] for x in carry].count(Status.Success)/len(carry)}")

def main():
    #Run_visualization(800,600,120,480*60,10*60,20*60,30*60)
    simulate_data(25)

if __name__ == "__main__":
    main()
