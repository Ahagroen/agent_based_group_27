from copy import deepcopy
from raylib import ORANGE, PINK, BeginDrawing, ClearBackground, DrawText, EndDrawing, InitWindow, SetTargetFPS, WindowShouldClose,DrawCircle,RED,GREEN,PURPLE,WHITE,BLUE,YELLOW,LoadTexture,DrawTexturePro
from src.simulation import Simulation
from src.environment import Airport
from src.datatypes import ImageType, Status
from loguru import logger

def seconds_to_watch_format(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def Run_visualization(x_dim,y_dim,fps,run_time,ac_freq,taxi_margin,loading_time, scheduler, rng_seed):
    InitWindow(x_dim,y_dim,b"AutoTaxi Simulation")
    SetTargetFPS(fps)
    airport = Airport("airport_layout.json",(x_dim,y_dim))
    straightaway = LoadTexture(b"images/taxiway_straight.png")
    turns = LoadTexture(b"images/taxiway_corner.png")
    triple_intersection = LoadTexture(b"images/taxiway_3way.png")
    quad_intersection = LoadTexture(b"images/taxiway_4way.png")
    unit_height = 50
    unit_width = 50

    sim = Simulation(airport,run_time,ac_freq,taxi_margin,loading_time, scheduler, rng_seed)
    baseline_gates = deepcopy(airport.gates)
    while not WindowShouldClose():
        BeginDrawing()
        ClearBackground((27,108,39))
        for i in airport.nodes.keys():
            if int(i) in airport.dept_runways:
                DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,RED)
            elif int(i) in airport.arrival_runways:
                DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,GREEN)
            elif int(i) in baseline_gates:
                DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,PURPLE)
            elif int(i) in airport.tug_chargers:
                DrawCircle(airport.nodes[i].x_pos,airport.nodes[i].y_pos,10,ORANGE)
            else:
                match airport.nodes[i].image_type:
                    case ImageType.four_way_intersection:
                        DrawTexturePro(quad_intersection,
                                       (0,0,quad_intersection.width,quad_intersection.height),
                                       (airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),
                                       (unit_width/2,unit_height/2),airport.nodes[i].orientation,WHITE)
                    case ImageType.three_way_intersection:
                        DrawTexturePro(triple_intersection,
                                       (0,0,triple_intersection.width,triple_intersection.height),
                                       (airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),
                                       (unit_width/2,unit_height/2),-airport.nodes[i].orientation,WHITE)
                    case ImageType.turn:
                        DrawTexturePro(turns,
                                       (0,0,turns.width,turns.height),
                                       (airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),
                                       (unit_width/2,unit_height/2),-airport.nodes[i].orientation,WHITE)
                    case ImageType.straight:
                        DrawTexturePro(straightaway,
                                       (0,0,straightaway.width,straightaway.height),
                                       (airport.nodes[i].x_pos,airport.nodes[i].y_pos,unit_width,unit_height),
                                       (unit_width/2,unit_height/2),airport.nodes[i].orientation,WHITE)
            positions = sim.position_list()
            for j in positions["aircraft"]:
                DrawCircle(airport.nodes[str(j[1])].x_pos,airport.nodes[str(j[1])].y_pos,5,YELLOW)
            for j in positions["tugs"]:
                DrawCircle(airport.nodes[str(j[1])].x_pos,airport.nodes[str(j[1])].y_pos,5,BLUE)
            for j in positions["tugs_loaded"]:
                DrawCircle(airport.nodes[str(j[1])].x_pos,airport.nodes[str(j[1])].y_pos,5,PINK)
            for j in positions["tugs_travelling"]:
                new_pos = str(j.arrival_node)
                old_pos = str(j.departure_node)
                x_pos = (airport.nodes[new_pos].x_pos-airport.nodes[old_pos].x_pos)+airport.nodes[old_pos].x_pos
                y_pos = (airport.nodes[new_pos].y_pos-airport.nodes[old_pos].y_pos)+airport.nodes[old_pos].y_pos
                if (airport.nodes[new_pos].x_pos-airport.nodes[old_pos].x_pos) > 0:
                    #going right
                    pass
                elif (airport.nodes[new_pos].x_pos-airport.nodes[old_pos].x_pos) < 0:
                    #going left
                    pass
                elif (airport.nodes[new_pos].y_pos-airport.nodes[old_pos].y_pos) > 0:
                    #going down
                    pass
                elif (airport.nodes[new_pos].y_pos-airport.nodes[old_pos].y_pos) < 0:
                    #going up
                    pass
                if j.loaded:
                    DrawCircle(x_pos,y_pos,5,PINK)
                else:
                    DrawCircle(x_pos,y_pos,5,BLUE)

        # DrawText(bytes(f"Current Timestep: {sim.time}","utf-8"),0,0,30,WHITE)
        watch_string = seconds_to_watch_format(sim.time)
        DrawText(bytes(f"Current Timestep: {watch_string}","utf-8"),0,0,20,WHITE)

        EndDrawing()
        if sim.state is not Status.Running:
            logger.warning(f"Simulation Ended!\nreason: {sim.state}")
            break
        sim.simulation_tick()


    
