from raylib import BeginDrawing, ClearBackground, EndDrawing, InitWindow, SetTargetFPS, WindowShouldClose,DrawCircle,RED,GREEN,PURPLE,WHITE,LoadTexture,DrawTexturePro
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
    unit_height = 45
    unit_width = 45


    sim = Simulation(2,airport,ac_freq,taxi_margin,loading_time,run_time)
    while not WindowShouldClose():
        BeginDrawing()
        ClearBackground((27,108,39))
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
                            DrawTexturePro(quad_intersection,(0,0,quad_intersection.width,quad_intersection.height),(airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),(unit_width/2,unit_height/2),airport.nodes[i].orientation,WHITE)
                        case ImageType.three_way_intersection:
                            DrawTexturePro(triple_intersection,(0,0,triple_intersection.width,triple_intersection.height),(airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),(unit_width/2,unit_height/2),-airport.nodes[i].orientation,WHITE)
                        case ImageType.turn:
                            DrawTexturePro(turns,(0,0,turns.width,turns.height),(airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),(unit_width/2,unit_height/2),-airport.nodes[i].orientation,WHITE)
                        case ImageType.straight:
                            DrawTexturePro(straightaway,(0,0,straightaway.width,straightaway.height),(airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),(unit_width/2,unit_height/2),airport.nodes[i].orientation,WHITE)
        EndDrawing()


    