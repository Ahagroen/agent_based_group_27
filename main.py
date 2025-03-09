from src.datatypes import Status
from src.environment import Airport
from src.simulation import Simulation


def main():
    sim = Simulation(2,Airport("baseline_airport.json"),15,10,45,1080)
    while sim.state == Status.Running:
        sim.simulation_tick()
    print(sim.state)

if __name__ == "__main__":
    main()
