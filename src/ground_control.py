
from src.datatypes import TowingVehicle


class groundControl():
    def __init__(self,nodes):
        self.nodes = nodes
    def determine_route(self,start_pos,end_pos)->list[int]:
        """Determine the route using a pathfinding algorithm - If needed it can have access to all other paths through state

        Args:
            start_pos (int): starting node
            end_pos (int): ending node

        Returns:
            list[int]: list of nodes to travel to
        """
        #The main pathfinding algorithm - TODO
        pass
    def determine_next_wait_position(self,tug:TowingVehicle)->int:
        """Determine where aircraft should wait/pick up the next aircraft

        Args:
            tug(TowingVehicle): data corresponding to the tug doing the computation

        Returns:
            int: end node to wait
        """
        #scheduler TODO - where do tugs wait for aircraft
        pass