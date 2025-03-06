from random import random,choice
from src.datatypes import Aircraft


class ATC():
    def __init__(self,ac_pace:int,taxi_margin:int,loading_margin:int,gates_list:list,arrival_runways:list):
        self.ac_pace = ac_pace
        self.next_ac_time = 0
        self.random_shift = self.get_random_shift(self.ac_pace)
        self.gates_list:list = gates_list
        self.taxi_margin = taxi_margin
        self.arrival_runways = arrival_runways
        self.base_loading_margin = loading_margin
        self.loading_margin = loading_margin + self.get_random_shift(self.base_loading_margin)

    def get_random_shift(self,base)->int:
        return int(round(random()*(base/5) - (base/10))) #Uniformly distrobuted random noise +-10%
    
    def add_aircraft(self,current_time):
        if len(self.gates_list) == 0: #No Free Gates
            self.next_ac_time = current_time + self.ac_pace + self.random_shift
            return None
        if current_time-self.next_ac_time <=0:
            self.next_ac_time = current_time + self.ac_pace + self.random_shift
            self.random_shift = self.get_random_shift(self.ac_pace)
            gate = choice(self.gates_list)
            self.gates_list.remove(gate)#Removes gate from available gates
            loading_time = self.loading_margin
            self.loading_margin = self.base_loading_margin + self.get_random_shift(self.base_loading_margin)
            return Aircraft(gate,current_time+self.taxi_margin,loading_time,0,current_time+loading_time+2*self.taxi_margin),choice(self.arrival_runways)
        else:
            return None
    def empty_gate(self,aircraft:Aircraft):
        #Re-adds gate as available when aircraft is moved to departures list
        if aircraft.target not in self.gates_list:
            self.gates_list.append(aircraft.target)
