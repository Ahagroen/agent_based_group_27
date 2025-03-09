from raylib import BeginDrawing, ClearBackground, EndDrawing, InitWindow, SetTargetFPS, WindowShouldClose,DrawCircle,RED,GREEN,PURPLE,WHITE,LoadTexture,DrawTextureEx
from src.simulation import Simulation
from src.environment import Airport
from src.datatypes import ImageType

def Run_simulation(x_dim,y_dim,fps,run_time,ac_freq,taxi_margin,loading_time):
    InitWindow(x_dim,y_dim,b"AutoTaxi Simulation")
    SetTargetFPS(fps)
    airport = Airport("baseline_airport.json")
    
    straightaway= LoadTexture(b"images\\taxiway_straight.png")

    turns = LoadTexture(b"images\\taxiway_corner.png")

    triple_intersection = LoadTexture(b"images\\taxiway_3way.png")
    quad_intersection = LoadTexture(b"images\\taxiway_4way.png")
    debug = True
    scale = 0.2


    sim = Simulation(2,airport,ac_freq,taxi_margin,loading_time,run_time)
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
                    match airport.nodes[i].image_type:
                        case ImageType.four_way_intersection:
                            DrawTextureEx(quad_intersection,(airport.nodes[i].x_pos,airport.nodes[i].y_pos),airport.nodes[i].orientation,scale,WHITE)
                        case ImageType.three_way_intersection:
                            DrawTextureEx(triple_intersection,(airport.nodes[i].x_pos,airport.nodes[i].y_pos),airport.nodes[i].orientation,scale,WHITE)
                        case ImageType.turn:
                            DrawTextureEx(turns,(airport.nodes[i].x_pos,airport.nodes[i].y_pos),airport.nodes[i].orientation,scale,WHITE)
                        case ImageType.straight:
                            DrawTextureEx(straightaway,(airport.nodes[i].x_pos,airport.nodes[i].y_pos),airport.nodes[i].orientation,scale,WHITE)
        EndDrawing()


    