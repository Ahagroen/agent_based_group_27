from dataclasses import dataclass
from enum import Enum

import src.ground_control as gc

class ImageType(Enum):
    """
    Type of intersection for visualization
    """
    four_way_intersection = 0
    three_way_intersection = 1
    turn = 2
    straight = 3

class Schedule_Algo(Enum):
    """
    Schedule algorithm selection
    """
    naive = 0
    greedy = 1
    aco = 2
    genetic = 3

@dataclass
class Node():
    """
    Node class 
        edges:list of connected node numbers
        x_pos: x position of the node in the world
        y_pos: y position of the node in the world
        image_type: What image to display
        orientation: how the image should be oriented
    """
    edges:list
    x_pos:int
    y_pos:int
    image_type:ImageType
    orientation:int #0 for first

@dataclass
class NodePathfinding():
    """
    Node class for pathfinding, extending the base node class to include a list of blocked times when the node is already in use
    """
    node:Node
    blocked_times:list

@dataclass
class Aircraft():
    """
    Aircraft Agent class
    Attributes:
        name:The name of the aircraft
        target: The node the aircraft is going to 
        departure_runway: The departure runway ID of the aircraft if travelling to the gate, or false if travelling from the gate (since the departure runway data is encoded in target)
        target:True if arriving
        max_travel_time:the timestamp when this aircraft will violate the taxi time constraint
        loading_time:How long this aircraft will take to load
        loading_completion_time:the timestamp when the aircraft will finish loading (not manually set)
    """
    name:str
    target:int                          #This implicitly holds direction, since its either a gate or a runway
    departure_runway:int
    direction:bool #false = departing (travelling to runway) true = arriving
    max_travel_time:int #When the aircraft must be at the target
    loading_time:int #How long the aircraft takes to load at the gate
    loading_completion_time:int = 0

@dataclass
class Schedule():
    """
    Schedule dataclass
    attributes:
        name_ac: the name of the aircraft in question
        estimated_time: the estimated start time of the schedule (when the aircraft arrives or finishes loading)
        start_pos: the start node of the schedule
        end_pos: the end node of the schedule
        dept_runway: the departure runway of the associated aircraft if this schedule is the first half, used in generation of aircraft only.
    """
    name_ac:int
    estimated_time:int
    start_pos:int
    end_pos:int
    dept_runway:int|None

@dataclass
class ActiveRoute():
    """
    Structure of the broadcast towing vehicle route information
    """
    start_time:int
    start_node:int
    end_node:int

@dataclass
class TowingVehicle():
    """
    Towing vehicle Agent
    Attributes:
        name: name of the towing vehicle
        pos: position of the towing vehicle
        schedule:remaining schedule of this towing vehicle
        start_time: when the towing vehicle should exit the garage
    Private Members:
        connected_aircraft: Aircraft connected to this towing vehicle, none otherwise
        time_to_next_node: speed of the tug
        next_node_list: current path to follow
        done: if the tug is finished with its schedule and returning to base
    """
    name:str
    pos:int
    schedule:list[Schedule]
    start_time:int #when the towing vehicle starts its route
    connected_aircraft:Aircraft|None
    time_to_next_node:int = 13 #seconds - Come back to this
    next_node_list = [] 
    done = False

    def determine_route(self,known_routes:list[ActiveRoute],time:int,ground_control:gc.groundControl):
        """
        Pathfinding method. First reconstructs the current global state by determining the paths of all known towing vehicle travel (stored in known routes), then pathfinds its own route
        """
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
    """
    Travelling vehicle representation, composed with towing vehicle base class and needed information to represent travel in an edge between two nodes
    """
    vehicle:TowingVehicle
    remaining_time:int
    departure_node:int
    arrival_node:int
    loaded:bool

class Status(Enum):
    """
    Different simulation states, any state but 0 ends the simulation
    """
    Running = 0
    Success = 1
    Failed_Aircraft_Taxi_Time = 2
    Failed_Collision = 3
    Failed_No_Landing_Space = 4




