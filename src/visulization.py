from raylib import BeginDrawing, ClearBackground, EndDrawing, InitWindow, SetTargetFPS, WindowShouldClose,DrawCircle,RED,GREEN,PURPLE,YELLOW,WHITE
from src.simulation import Simulation
from src.environment import Airport

def Run_simulation(x_dim,y_dim,fps,run_time,ac_freq,taxi_margin,loading_time):
    InitWindow(x_dim,y_dim,b"AutoTaxi Simulation")
    SetTargetFPS(fps)
    airport = Airport("baseline_airport.json")
    sim = Simulation(2,airport,ac_freq,taxi_margin,loading_time,run_time)
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


    