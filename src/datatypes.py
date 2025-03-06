from dataclasses import dataclass

#This is a linked list basically, so each node of the airport connects to N other nodes with certain time costs, and only one vehicle is allowed to be in an edge at once


@dataclass
class Aircraft():
    target:int #This implicitly holds direction, since its either a gate or a runway
    target_arrival_time:int #When the aircraft must be at the target
    loading_time:int #How long the aircraft takes to load at the gate
    loading_completion_time:int
    target_departure_time:int #When the aircraft should depart = arrival time + load time + allowable taxi

@dataclass
class TowingVehicle():
    pos:int#Node the vehicle will _arrive_ to: IE if travelling from A to B this is B and distance is != 0
    next_node_list = []
    connected_aircraft:Aircraft

