from src.datatypes import Aircraft,TowingVehicle,Status
from src.atc import ATC
from src.ground_control import groundControl
from src.environment import Airport
from random import choice

class Simulation:
    def __init__(self,num_tugs,airport:Airport,ac_freq:int,taxi_margin:int,loading_margin:int,max_time:int):
        self.num_tugs = num_tugs
        self.airport:Airport = airport
        self.atc:ATC = ATC(ac_freq,taxi_margin,loading_margin,airport.gates,airport.arrival_runways)
        self.ground_control:groundControl = groundControl(airport.nodes)
        self.max_time:int = max_time
        self.ac_waiting:dict[str,list[Aircraft]] = airport.populate_waiting_dict()#AC waiting at runway (arriving), or gate (departing)
        self.ac_loading:list[Aircraft] = []#AC that are currently loading, 
        self.tug_waiting:list[TowingVehicle] = []
        self.tug_intersection:list[TowingVehicle] = []
        self.time:int = 0
        self.state:Status = Status.Running

    def _add_new_aircraft(self):
        carry = self.atc.add_aircraft(self.time)
        if carry is not None:
            self.ac_waiting[carry[1]].append(carry[0])

    def _check_loading(self):
        for i in self.ac_loading:
            if i.loading_completion_time <= self.time:
                self.ac_loading.remove(i)
                self.ac_waiting[i.target.name].append(i)
                i.target = choice(self.airport.dept_runways) #Fix this once nodes are defined
                i.direction = False
                self.atc.empty_gate(i)

    def _check_tug_waiting(self):
        for i in self.tug_waiting:
            for j in self.ac_waiting.keys():
                if i.pos.name == j:
                    if len(self.ac_waiting[j])>0:
                        aircraft = self.ac_waiting[j][0]
                        self.ac_waiting[j].remove(aircraft)#No longer waiting
                        i.connected_aircraft = aircraft
                        i.next_node_list = self.ground_control.determine_route(i.pos,aircraft.target)
                        self.tug_waiting.remove(i)
                        self.tug_intersection.append(i)


    def _check_tug_intersection(self):
        for i in self.tug_intersection:
            if i.connected_aircraft.direction:#arriving
                if i.connected_aircraft.target_arrival_time < self.time:
                    self.state = Status.Failed_Aircraft_Taxi_Time
            else:
                if i.connected_aircraft.target_departure_time < self.time:
                    self.state = Status.Failed_Aircraft_Taxi_Time
            if len(i.next_node_list) == 0: #we have arrived at our destination
                if i.connected_aircraft:
                    if i.pos.name in self.airport.dept_runways: #The aircraft has arrived at the departure runway
                        i.connected_aircraft = None
                        i.next_node_list = self.ground_control.determine_route(i.pos,self.ground_control.determine_next_wait_position(i.pos,self.ac_loading))
                    else:
                        i.connected_aircraft.loading_completion_time = self.time + i.connected_aircraft.loading_time
                        self.ac_loading.append(i.connected_aircraft)
                        i.connected_aircraft = None
                        i.next_node_list = self.ground_control.determine_route(i.pos,self.ground_control.determine_next_wait_position(i.pos,self.ac_loading))
                else: #We are waiting
                    self.tug_intersection.remove(i)
                    self.tug_waiting.append(i)
            else:
                #add collision avoidance here TODO's
                next_node = i.next_node_list.pop(0)
                i.pos = next_node

    def _check_ac_waiting_time(self):
        for i in self.ac_waiting.keys():
            for j in self.ac_waiting[i]:
                if j.direction:#arriving
                    if j.target_arrival_time < self.time:
                        self.state = Status.Failed_Aircraft_Taxi_Time
                else:
                    if j.target_departure_time < self.time:
                        self.state = Status.Failed_Aircraft_Taxi_Time

    def simulation_tick(self):
        if self.max_time <= self.time:
            self.state = Status.Success
        self._check_ac_waiting_time()
        self._check_loading()
        self._add_new_aircraft()
        self._check_tug_waiting()
        self._check_tug_intersection()
        self.time += 1
