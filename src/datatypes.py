from dataclasses import dataclass
from enum import Enum

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
class TowingVehicle():
    name:str
    pos:int#Assume all travel time takes the same number of mins (say 1) - can't assume this
    connected_aircraft:Aircraft|None
    priority:int
    time_to_next_node:int = 15 #seconds
    next_node_list = []

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
