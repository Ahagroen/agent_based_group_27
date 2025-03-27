from dataclasses import dataclass
from enum import Enum

from src.ground_control import groundControl

#This is a linked list basically, so each node of the airport connects to N other nodes with certain time costs, and only one vehicle is allowed to be in an edge at once


@dataclass
class Aircraft():
    name:str
    target:int #This implicitly holds direction, since its either a gate or a runway
    direction:bool #false = departing (travelling to runway) true = arriving
    target_arrival_time:int #When the aircraft must be at the target
    loading_time:int #How long the aircraft takes to load at the gate
    loading_completion_time:int
    target_departure_time:int #When the aircraft should depart = arrival time + load time + allowable taxi

@dataclass
class Schedule():
    estimated_time:int
    start_pos:int
    end_pos:int
    landing:bool

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
    connected_aircraft:Aircraft|None
    time_to_next_node:int = 15 #seconds - Come back to this
    next_node_list = []

    def determine_route(self,known_routes:list[ActiveRoute],time:int,ground_control:groundControl):
        #We assume no collisions once pathing is started
        active_route_pathing:list[list[int]] = []
        for i in known_routes:
            nodes = ground_control.determine_route(i.start_node,i.end_node,active_route_pathing)
            current_time = (time - i.start_time)//15 #the number of timesteps already taken on this route
            if current_time < len(nodes):
                for index,val in enumerate(nodes[current_time:]):
                    if active_route_pathing[index]:
                        active_route_pathing[index].append(val)
                    else:
                        active_route_pathing[index] = [val]
        self.next_node_list = ground_control.determine_route((self.pos,self.get_next_pos(),active_route_pathing))

    def get_next_pos(self)->int:
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

class Status(Enum):
    Running = 0
    Success = 1
    Failed_Aircraft_Taxi_Time = 2
    Failed_Collision = 3
    Failed_No_Landing_Space = 4

class ImageType(Enum):
    four_way_intersection = 0
    three_way_intersection = 1
    turn = 2
    straight = 3


@dataclass
class Node():
    edges:list
    x_pos:int
    y_pos:int
    image_type:ImageType
    orientation:int #0 for first 
