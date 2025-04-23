import json

from src.datatypes import Aircraft, Node,ImageType
class Airport():
    def __init__(self,airport_file,window_dims):
        self._load_airport_data(airport_file,window_dims)
    def _load_airport_data(self,airport_file,window_dims:tuple[int,int]):
        with open(airport_file,"r") as fs:
            data = json.load(fs)
            node_map = data["nodes"]
            updated_node_map = {}
            for i in node_map.keys():
                # We need to add 75 for some reason
                #This might need to be extracted into a method
                x_pos = int(((node_map[i]["x_pos"])/(window_dims[0]/100))*window_dims[0])
                y_pos = window_dims[1] - int(((node_map[i]["y_pos"])/(window_dims[1]/100))*window_dims[1])
                if len(node_map[i]["edges"]) == 4:
                    image_type = ImageType.four_way_intersection
                    orientation = 0
                elif len(node_map[i]["edges"]) == 3:
                    image_type = ImageType.three_way_intersection
                    x_less, y_less, x_greater, y_greater = self.determine_incoming(node_map, i)
                    if x_less and y_less and x_greater:
                        orientation = 0
                    elif y_less and x_greater and y_greater:
                        orientation = 90
                    elif x_less and y_greater and x_greater:
                        orientation = 180
                    elif y_less and y_greater and x_less:
                        orientation = 270
                    else:
                        raise RuntimeError
                elif len(node_map[i]["edges"]) == 2:
                    x_less, y_less, x_greater, y_greater = self.determine_incoming(node_map, i)
                    if x_less and x_greater:
                        image_type = ImageType.straight
                        orientation = 90
                    elif y_less and y_greater:
                        image_type = ImageType.straight
                        orientation = 0
                    elif x_less and y_less:
                        image_type = ImageType.turn
                        orientation = 270
                    elif x_less and y_greater:
                        image_type = ImageType.turn
                        orientation = 180
                    elif x_greater and y_greater:
                        image_type = ImageType.turn
                        orientation = 90
                    elif x_greater and y_less:
                        image_type = ImageType.turn
                        orientation = 0
                    else:
                        raise RuntimeError
                else:
                    image_type = ImageType.four_way_intersection
                    orientation = 0
                updated_node_map[i] = Node(node_map[i]["edges"],x_pos,y_pos,image_type,orientation)
            self.dept_runways:list= data["dept_runways"]
            self.arrival_runways:list = data["arrival_runways"]
            self.tug_chargers:list = data["chargers"]
            self.gates:list = data["gates"]
            self.nodes:dict[int,Node] = updated_node_map

    def determine_incoming(self, node_map, i):
        x_less = False
        y_less = False
        x_greater = False
        y_greater = False
        for edge in node_map[i]["edges"]:
            if node_map[str(edge)]["x_pos"] < node_map[i]["x_pos"]: #that means that the incoming node is to the left of the current node
                x_less = True
            elif node_map[str(edge)]["x_pos"] > node_map[i]["x_pos"]: #that means that the incoming node is to the right of the current node
                x_greater = True
            elif node_map[str(edge)]["y_pos"] < node_map[i]["y_pos"]: #then the incoming node is above the current node
                y_less = True
            elif node_map[str(edge)]["y_pos"] > node_map[i]["y_pos"]: #then the incoming node is below the current node
                y_greater = True
        return x_less,y_less,x_greater,y_greater
 

    def populate_waiting_dict(self)->dict[int,Aircraft|None]:
        carry = {}
        for i in self.arrival_runways:
            carry[i] = None
        for i in self.dept_runways:
            carry[i] = None
        for i in self.gates:
            carry[i] = None
        return carry




