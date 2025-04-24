from dataclasses import dataclass
from enum import Enum

import src.ground_control as gc

#This is a linked list basically, so each node of the airport connects to N other nodes with certain time costs, and only one vehicle is allowed to be in an edge at once
class ImageType(Enum):
    four_way_intersection = 0
    three_way_intersection = 1
    turn = 2
    straight = 3

class Schedule_Algo(Enum):
    naive = 0
    greedy = 1
    aco = 2
    genetic = 3

@dataclass
class Node():
    edges:list
    x_pos:int
    y_pos:int
    image_type:ImageType
    orientation:int #0 for first

@dataclass
class NodePathfinding():
    node:Node
    blocked_times:list

@dataclass
class Aircraft():
    name:str
    target:int                          #This implicitly holds direction, since its either a gate or a runway
    departure_runway:int
    direction:bool #false = departing (travelling to runway) true = arriving
    max_travel_time:int #When the aircraft must be at the target
    loading_time:int #How long the aircraft takes to load at the gate
    loading_completion_time:int = 0

@dataclass
class Schedule():
    name_ac:int
    estimated_time:int
    start_pos:int
    end_pos:int
    dept_runway:int|None

@dataclass
class ActiveRoute():
    start_time:int
    start_node:int
    end_node:int

@dataclass
class TowingVehicle():
    name:str
    pos:int#Assume all travel time takes the same number of mins (say 1) - can't assume this
    schedule:list[Schedule]
    start_time:int #when the towing vehicle starts its route
    connected_aircraft:Aircraft|None
    time_to_next_node:int = 15 #seconds - Come back to this
    next_node_list = [] 
    done = False

    def determine_route(self,known_routes:list[ActiveRoute],time:int,ground_control:gc.groundControl):
        #We assume no collisions once pathing is started
        active_route_pathing:dict[int,list[int]] = {}
        for i in known_routes:
            if i.start_time+30*60 < time:
                continue
            nodes = ground_control.determine_route(i.start_node,i.end_node,active_route_pathing,i.start_time)
            for i in nodes:
                if i[0] in active_route_pathing:
                    active_route_pathing[i[0]].append(i[1])
                else:
                    active_route_pathing[i[0]] = [i[1]]
        next_nodes = ground_control.determine_route(self.pos,self.get_next_pos(),active_route_pathing,time)
        self.next_node_list = next_nodes

    def get_next_pos(self)->int:
        if len(self.schedule) == 0:
            return 109
        next_schedule = self.schedule[0]
        if self.connected_aircraft:
            return next_schedule.end_pos
        else:
            return next_schedule.start_pos

@dataclass
class TravellingVehicle():
    vehicle:TowingVehicle
    remaining_time:int
    departure_node:int
    arrival_node:int
    loaded:bool

class Status(Enum):
    Running = 0
    Success = 1
    Failed_Aircraft_Taxi_Time = 2
    Failed_Collision = 3
    Failed_No_Landing_Space = 4




