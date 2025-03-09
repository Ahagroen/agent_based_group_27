from dataclasses import dataclass
from enum import Enum

#This is a linked list basically, so each node of the airport connects to N other nodes with certain time costs, and only one vehicle is allowed to be in an edge at once


@dataclass
class Aircraft():
    target:int #This implicitly holds direction, since its either a gate or a runway
    direction:bool #false = departing (travelling to runway) true = arriving
    target_arrival_time:int #When the aircraft must be at the target
    loading_time:int #How long the aircraft takes to load at the gate
    loading_completion_time:int
    target_departure_time:int #When the aircraft should depart = arrival time + load time + allowable taxi

@dataclass
class TowingVehicle():
    pos:int#Assume all travel time takes the same number of mins (say 1) - can't assume this
    next_node_list = []
    connected_aircraft:Aircraft
    priority:int


class Status(Enum):
    Running = 0
    Success = 1
    Failed_Aircraft_Taxi_Time = 2
    Failed_Collision = 3

