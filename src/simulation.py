from loguru import logger
from src.datatypes import ActiveRoute, Aircraft,TowingVehicle,Status,TravellingVehicle
from src.atc import ATC
from src.ground_control import groundControl
from src.environment import Airport
from src.ants_v2 import generate_schedule_tugs_2
class Simulation:
    def __init__(self,airport:Airport,max_time,ac_interval:int,taxi_margin:int,loading_margin:int):
        self.airport:Airport = airport
        self.ground_control:groundControl = groundControl(airport.nodes)
        self.atc:ATC = ATC(max_time,ac_interval,loading_margin,airport,self.ground_control)
        self.max_time:int = max_time
        self.taxi_margin = taxi_margin
        self.ac_waiting:dict[str,Aircraft|None] = airport.populate_waiting_dict()#AC waiting at runway (arriving), or gate (departing)
        self.ac_loading:list[Aircraft] = []#AC that are currently loading - location is inside struct 
        self.tug_waiting:list[TowingVehicle] = [] #empty tugs
        self.tug_intersection:list[TowingVehicle] = generate_schedule_tugs_2(self.airport,self.atc.ac_schedule,self.ground_control) #full tugs - we might need to add travel down the line
        self.tug_travelling:list[TravellingVehicle] = []
        self.current_active_routes:list[ActiveRoute] = []
        self.time:int = 0
        self.state:Status = Status.Running

        
    def _add_new_aircraft(self):
        """Adds new aircraft to the simulation if there is a free gate. Aircraft are added to the corresponding arrival runway off-ramp
        """
        carry = self.atc.add_aircraft(self.time)
        if carry is not None:
            logger.info(f"Added Aircraft to {carry[1]}")
            if self.ac_waiting[carry[1]] is not None:
                self.state = Status.Failed_No_Landing_Space
            aircraft = carry[0]
            aircraft.max_travel_time= self.time+self.taxi_margin
            self.ac_waiting[carry[1]] = carry[0]

    def _check_loading(self):
        """Determines if an aircraft is finished loading. if so, adds the aircraft to the waiting list
        """
        for i in self.ac_loading:
            if i.loading_completion_time <= self.time:
                logger.info(f"Aircraft completed loading at {i.target}")
                self.ac_loading.remove(i)
                self.ac_waiting[i.target] = i
                i.target = i.departure_runway #Fix this once nodes are defined
                i.max_travel_time= self.time+self.taxi_margin
                i.direction = False
                self.atc.empty_gate(i)

    def _check_tug_waiting(self):
        """ Checks if a tug has an aircraft ready"""
        for i in self.tug_waiting:
            for j in self.ac_waiting.keys():
                if i.pos == j:
                    if self.ac_waiting[j] is not None:
                        logger.debug("aircraft is picked up")
                        aircraft = self.ac_waiting[j]
                        self.ac_waiting[j] = None  #No longer waiting
                        if aircraft:
                            i.connected_aircraft = aircraft
                        else:
                            raise RuntimeError
                        if len(i.schedule) != 0:
                            i.determine_route(self.current_active_routes,self.time,self.ground_control)
                            self.current_active_routes.append(ActiveRoute(self.time,i.pos,i.get_next_pos()))
                            if i.connected_aircraft:
                                i.schedule.pop(0)
                            self.tug_waiting.remove(i)
                            self.tug_intersection.append(i)


    def _check_tug_intersection(self):
        """Handles tugs arriving at a node
        """
        for i in self.tug_intersection:
            collision_risk = [x for x in self.tug_intersection if x is not i and x.pos == i.pos]
            if len(collision_risk)>0 and i.pos != 109:
                logger.warning("Collision!")
                self.state = Status.Failed_Collision
            if i.start_time > self.time:
                continue
            if i.connected_aircraft:
                if i.connected_aircraft.max_travel_time < self.time:
                    self.state = Status.Failed_Aircraft_Taxi_Time
            if len(i.next_node_list) == 0: #we have arrived at our destination
                if i.connected_aircraft:
                    if i.pos not in self.airport.dept_runways: #The aircraft has arrived at the departure runway
                        i.connected_aircraft.loading_completion_time = self.time + i.connected_aircraft.loading_time
                        self.ac_loading.append(i.connected_aircraft)
                    i.connected_aircraft = None
                    i.determine_route(self.current_active_routes,self.time,self.ground_control)
                    self.current_active_routes.append(ActiveRoute(self.time,i.pos,i.get_next_pos()))
                else: #We are waiting
                    if i.pos == 109:
                        i.determine_route(self.current_active_routes,self.time,self.ground_control)
                        self.current_active_routes.append(ActiveRoute(self.time,i.pos,i.get_next_pos()))
                    else:
                        self.tug_intersection.remove(i)
                        self.tug_waiting.append(i)
            else:
                #add collision avoidance here TODO's
                next_node = i.next_node_list.pop(0)
                old_pos = i.pos
                i.pos = next_node
                self.tug_intersection.remove(i)
                if i.connected_aircraft:
                    con_air = True
                else:
                    con_air = False
                self.tug_travelling.append(TravellingVehicle(i,i.time_to_next_node,old_pos,i.pos,con_air))


    def _check_ac_waiting_time(self):
        for i in self.ac_waiting.keys():
            if self.ac_waiting[i]:
                if self.ac_waiting[i].direction:# type: ignore #arriving
                    if self.ac_waiting[i].max_travel_time < self.time: # type: ignore
                        self.state = Status.Failed_Aircraft_Taxi_Time
                else:
                    if self.ac_waiting[i].max_travel_time < self.time: # type: ignore
                        self.state = Status.Failed_Aircraft_Taxi_Time

    def _check_tug_travelling(self):
        for i in self.tug_travelling:
            if i.remaining_time > 0:
                i.remaining_time -=1
            else:
                self.tug_intersection.append(i.vehicle)
                self.tug_travelling.remove(i)
            

    def simulation_tick(self):
        if self.max_time <= self.time:
            self.state = Status.Success
        self._check_ac_waiting_time()
        self._check_loading()
        self._add_new_aircraft()
        self._check_tug_waiting()
        self._check_tug_intersection()
        self._check_tug_travelling()
        self.time += 1

    def position_list(self)->dict[str,list[tuple[str,int]]]:
        output = {}
        output["aircraft"] = []
        output["tugs"] = []
        output["tugs_loaded"] = []
        output["tugs_travelling"] = []
        for i in self.ac_waiting.keys():
            if self.ac_waiting[i]:
                output["aircraft"].append(((self.ac_waiting[i]).name,i))
        for i in self.ac_loading:
            output["aircraft"].append((i.name,i.target))
        for i in self.tug_waiting:
            output["tugs"].append((i.name,i.pos))
        for i in self.tug_intersection:
            if i.connected_aircraft is not None:
                output["tugs_loaded"].append((i.name,i.pos))
            else:
                output["tugs"].append((i.name,i.pos))
        for i in self.tug_travelling:
            output["tugs_travelling"].append(i)
        return output
    

def run_simulation(airport,run_time,ac_freq,taxi_margin,loading_time):
    sim = Simulation(airport,run_time,ac_freq,taxi_margin,loading_time)
    while sim.state == Status.Running:
        sim.simulation_tick()
    logger.warning(f"Simulation Ended!\nreason: {sim.state}")
    return sim.state
