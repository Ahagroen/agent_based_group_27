from src.environment import Airport
from src.visulization import Run_visualization  # noqa: F401
from src.simulation import run_simulation
from src.ants import compute_schedule



def main():
    airport = Airport("baseline_airport.json")
    # run_simulation(2,airport,1080*60,15*60,10*60,45*60)
    compute_schedule(airport,2)

if __name__ == "__main__":
    main()
