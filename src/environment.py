import json
from typing import Union

from src.datatypes import Aircraft
class Airport():
    def __init__(self,airport_file):
        self.load_airport_data(airport_file)
    def load_airport_data(self,airport_file):
        with open(airport_file,"r") as fs:
            data = json.load(fs)
            node_map = data["nodes"]
            # updated_map = deepcopy(node_map)
            # for i in node_map.keys():
            #     for j in node_map[i]:
            #         if j not in updated_map.keys():
            #             updated_map[j] = [i]
            #         elif i not in updated_map[j]:
            #             updated_map[j].append(i)
            self.dept_runways= data["dept_runways"]
            self.arrival_runways = data["arrival_runways"]
            self.gates = data["gates"]
            self.nodes = node_map
            
    def save_airport_data(self,airport_file):
        with open(airport_file,"w") as fs:
            json.dump(self.data,fs)

    def populate_waiting_dict(self)->dict[str,Union[Aircraft|None]]:
        carry = {}
        for i in self.arrival_runways:
            carry[i] = None
        for i in self.dept_runways:
            carry[i] = None
        for i in self.gates:
            carry[i] = None
        return carry



if __name__ == "__main__":
    Airport("baseline_airport_1.json").save_airport_data("baseline_airport.json")
            