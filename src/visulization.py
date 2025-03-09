from raylib import BeginDrawing, InitWindow, SetTargetFPS, WindowShouldClose
from src.simulation import Simulation
from src.environment import Airport

InitWindow(1920,1080,b"AutoTaxi Simulation")
SetTargetFPS(24)
sim = Simulation(2,Airport.load_airport_data("baseline_airport.json"),15,10,45,1080)
while not WindowShouldClose():
    BeginDrawing()
    position_data = sim.position_list()
    