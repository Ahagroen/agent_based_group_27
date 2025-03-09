import json
from typing import Union

from src.datatypes import Aircraft, Node
class Airport():
    def __init__(self,airport_file,window_dims:tuple[int,int]=(700,500)):
        self._load_airport_data(airport_file,window_dims)
    def _load_airport_data(self,airport_file,window_dims:tuple[int,int]):
        with open(airport_file,"r") as fs:
            data = json.load(fs)
            node_map = data["nodes"]
            updated_node_map = {}
            for i in node_map.keys():
                #why does this need +75? Explore later
                #This might need to be extracted into a method
                updated_node_map[i] = Node(node_map[i]["edges"],int(((node_map[i]["x_pos"]-1)/8)*window_dims[0]+75),window_dims[1]+100 -int(((node_map[i]["y_pos"]-1)/7)*window_dims[1]+75))
            self.dept_runways:list= data["dept_runways"]
            self.arrival_runways:list = data["arrival_runways"]
            self.gates:list = data["gates"]
            self.nodes:dict[int,Node] = updated_node_map
 

    def populate_waiting_dict(self)->dict[str,Union[Aircraft|None]]:
        carry = {}
        for i in self.arrival_runways:
            carry[i] = None
        for i in self.dept_runways:
            carry[i] = None
        for i in self.gates:
            carry[i] = None
        return carry

