from copy import deepcopy
from numpy import random
from src.datatypes import Aircraft, Schedule
from loguru import logger
from random import choice,seed
from src.environment import Airport
from src.ground_control import groundControl

class ATC():
    def __init__(self,total_time:int,ac_pace:int,loading_time:int,airport:Airport,ground_control:groundControl,rng_seed:int):
        self.ac_pace = ac_pace
        if rng_seed != -1:
            self.random_norm = random.default_rng(rng_seed)
            seed(rng_seed)
        else:
            self.random_norm = random.default_rng()
        self.next_ac_time = ac_pace+self.get_random_shift(self.ac_pace)
        self.gates_list:list = deepcopy(airport.gates)
        self.departure_runways = airport.dept_runways
        self.arrival_runways = airport.arrival_runways
        self.base_loading_time = loading_time
        self.loading_margin = loading_time + self.get_random_shift(self.base_loading_time)
        self.next_aircraft_name = 0
        self.ac_schedule:list = self.populate_schedule(total_time,ground_control)

    def get_random_shift(self,base)->int:
        return int(round(self.random_norm.normal(0,0.05)*(base/5))) #normally distrobuted random noise +-10%
    
    def add_aircraft(self,current_time):
        if self.next_ac_time-current_time <=0:
            self.next_ac_time = current_time + self.ac_pace + self.get_random_shift(self.ac_pace)
            while True:
                carry:Schedule = self.ac_schedule.pop(0)
                if carry.dept_runway:
                    gate = carry.end_pos
                    arr_runway = carry.start_pos
                    dept_runway = carry.dept_runway
                    next_name = carry.name_ac
                    break
            loading_time = self.loading_margin
            self.loading_margin = self.base_loading_time + self.get_random_shift(self.base_loading_time)
            return Aircraft(str(next_name),gate,dept_runway,True,0,loading_time),arr_runway
        else:
            return None
    def empty_gate(self,aircraft:Aircraft):
        #Re-adds gate as available when aircraft is moved to departures list
        if aircraft.target not in self.gates_list:
            self.gates_list.append(aircraft.target)


    def populate_schedule(self,total_time:int,gc):
        output = []
        gates = []
        working_gates_list = self.gates_list
        carry = 0
        count_vics = 0
        while carry < total_time:
            for i in gates:
                if i[1] < carry:
                    gates.remove(i)
                    working_gates_list.append(i[0])
            carry+=self.ac_pace
            if len(working_gates_list) == 0:
                logger.warning("Configuration is invalid")
                continue
            gate = choice(working_gates_list)
            working_gates_list.remove(gate)
            arr_runway = self.arrival_runways[count_vics%len(self.arrival_runways)]
            count_vics += 1
            taxi_time = len(gc.determine_route(gate,arr_runway,{},0))*15
            gates.append((gate,carry+taxi_time+self.loading_margin))
            dept_runway = choice(self.departure_runways)
            output.append(Schedule(count_vics,carry,arr_runway,gate,dept_runway))
            output.append(Schedule(count_vics,carry+taxi_time+self.loading_margin,gate,dept_runway,False))
        return output
