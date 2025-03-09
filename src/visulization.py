from raylib import BeginDrawing, ClearBackground, EndDrawing, InitWindow, SetTargetFPS, WindowShouldClose,DrawCircle,RED,GREEN,PURPLE,YELLOW,WHITE
from src.simulation import Simulation
from src.environment import Airport

def Run_simulation():
    InitWindow(800,600,b"AutoTaxi Simulation")
    SetTargetFPS(24)
    airport = Airport("baseline_airport.json")
    sim = Simulation(2,airport,15,10,45,1080)
    debug = True
    while not WindowShouldClose():
        BeginDrawing()
        ClearBackground(WHITE)
        if debug:
            for i in airport.nodes.keys():
                if int(i) in airport.dept_runways:
                    DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,RED)
                elif int(i) in airport.arrival_runways:
                    DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,GREEN)
                elif int(i) in airport.gates:
                    DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,PURPLE)
                else:
                    DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,YELLOW)
        EndDrawing()


    