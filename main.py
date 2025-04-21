from src.datatypes import Status
from src.environment import Airport
from src.visulization import Run_visualization  # noqa: F401
from src.simulation import run_simulation # noqa: F401
from src.ants import compute_schedule
from loguru import logger
import sys


def simulate_data(runs:int):
    logger.remove()
    logger.add(sys.stderr, level="SUCCESS")
    airport = Airport("baseline_airport.json")
    carry = []
    for _ in range(runs):
        result = run_simulation(airport,1800*60,15*60,15*60,20*60)
        carry.append(result)
    print(f"num successes: {[x[0] for x in carry].count(Status.Success)}, percentage = {[x[0] for x in carry].count(Status.Success)/len(carry)}")

def main():
    Run_visualization(800,600,60,1800*60,10*60,15*60,20*60)
    #simulate_data(100)

if __name__ == "__main__":
    main()
