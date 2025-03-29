from src.environment import Airport
from src.visulization import Run_visualization  # noqa: F401
from src.simulation import run_simulation # noqa: F401
from src.ants import compute_schedule



def main():
    airport = Airport("baseline_airport.json")
    Run_visualization(800,600,120,180*60,30*60,25*60,10*60)
    #run_simulation(airport,180*60,30*60,25*60,10*60)
    # compute_schedule(airport,2)

if __name__ == "__main__":
    main()
