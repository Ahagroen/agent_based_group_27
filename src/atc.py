from random import random,choice
from src.datatypes import Aircraft
from loguru import logger

class ATC():
    def __init__(self,total_time:int,ac_pace:int,taxi_margin:int,loading_time:int,gates_list:list,arrival_runways:list,departure_runways:list):
        self.ac_pace = ac_pace
        self.next_ac_time = ac_pace+self.get_random_shift(self.ac_pace)
        self.gates_list:list = gates_list
        self.departure_runways = departure_runways
        self.taxi_margin = taxi_margin
        self.arrival_runways = arrival_runways
        self.base_loading_time = loading_time
        self.loading_margin = loading_time + self.get_random_shift(self.base_loading_time)
        self.next_aircraft_name = 0
        self.ac_schedule:list = self.populate_schedule(total_time)

    def get_random_shift(self,base)->int:
        return int(round(random()*(base/5) - (base/10))) #Uniformly distrobuted random noise +-10%
    
    def add_aircraft(self,current_time):
        if self.next_ac_time-current_time <=0:
            self.next_ac_time = current_time + self.ac_pace + self.get_random_shift(self.ac_pace)
            while True:
                carry = self.ac_schedule.pop(0)
                if carry[4]:
                    gate = carry[1]
                    arr_runway = carry[2]
                    break
            loading_time = self.loading_margin
            self.loading_margin = self.base_loading_time + self.get_random_shift(self.base_loading_time)
            self.next_aircraft_name += 1
            logger.info("Added Aircraft")
            return Aircraft(str(self.next_aircraft_name),gate,True,current_time+self.taxi_margin,loading_time,0,current_time+loading_time+2*self.taxi_margin),arr_runway
        else:
            return None
    def empty_gate(self,aircraft:Aircraft):
        #Re-adds gate as available when aircraft is moved to departures list
        if aircraft.target not in self.gates_list:
            self.gates_list.append(aircraft.target)


    def populate_schedule(self,total_time:int):
        output = []
        gates = []
        working_gates_list = self.gates_list
        carry = 0
        while carry < total_time:
            for i in gates:
                if i[1] < carry:
                    gates.remove(i)
                    working_gates_list.append(i[0])
            carry+=self.ac_pace
            gate = choice(working_gates_list)
            working_gates_list.remove(gate)
            gates.append((gate,carry+self.taxi_margin+self.loading_margin))
            output.append((carry,choice(self.arrival_runways),gate,True))
            output.append((carry+self.taxi_margin+self.loading_margin,gate,choice(self.departure_runways),False))
        return output
