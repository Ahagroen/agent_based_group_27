
from src.datatypes import TowingVehicle


class groundControl():
    def __init__(self,nodes):
        self.nodes = nodes
    def determine_route(self,start_pos:int,end_pos:int,invalid_nodes:list[list[int]] = [])->list[int]:
        """Determine the route using a pathfinding algorithm - If needed it can have access to all other paths through state

        Args:
            start_pos (int): starting node
            end_pos (int): ending node
            invalid_nodes: list of list of nodes that are occupied at any one time - how do we handle edges?

        Returns:
            list[int]: list of nodes to travel to
        """
        #The main pathfinding algorithm - TODO
        pass