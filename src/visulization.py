from raylib import BeginDrawing, InitWindow, SetTargetFPS, WindowShouldClose,DrawCircle
from src.simulation import Simulation
from src.environment import Airport

InitWindow(1920,1080,b"AutoTaxi Simulation")
SetTargetFPS(24)
airport = Airport("baseline_airport.json")
sim = Simulation(2,airport,15,10,45,1080)
debug = True
while not WindowShouldClose():
    BeginDrawing()
    if debug:
        for i in airport.nodes:
            DrawCircle()
    position_data = sim.position_list()
    