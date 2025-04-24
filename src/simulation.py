from loguru import logger
from src.datatypes import ActiveRoute, Aircraft, Schedule_Algo,TowingVehicle,Status,TravellingVehicle
from src.atc import ATC
from src.ground_control import groundControl
from src.environment import Airport
from src.ants_v2 import generate_schedule_tugs,generate_schedule_tugs_2,generate_schedule_tugs_3, generate_schedule_tugs_4
from random import choice
class Simulation:
    def __init__(self,airport:Airport,max_time,ac_interval:int,taxi_margin:int,loading_margin:int, scheduler:Schedule_Algo,rng_seed:int=-1):
        self.airport:Airport = airport
        self.ground_control:groundControl = groundControl(airport.nodes,max_time)
        nominal_taxi = len(self.ground_control.determine_route(choice(self.airport.dept_runways),choice(self.airport.gates),{},0))*15
        if nominal_taxi > taxi_margin:
            logger.warning(f"minimum taxi time is: {nominal_taxi}, current taxi time threshold is: {taxi_margin}")
        else:
            logger.info(f"minimum taxi time is: {nominal_taxi}, current taxi time threshold is: {taxi_margin}")
        self.atc:ATC = ATC(max_time,ac_interval,loading_margin,airport,self.ground_control,rng_seed)
        self.max_time:int = max_time
        self.taxi_margin = taxi_margin
        self.ac_waiting:dict[int,Aircraft|None] = airport.populate_waiting_dict()#AC waiting at runway (arriving), or gate (departing)
        self.ac_loading:list[Aircraft] = []#AC that are currently loading - location is inside struct 
        self.tug_waiting:list[TowingVehicle] = [] #empty tugs
        match scheduler:
            case Schedule_Algo.naive: 
                self.tug_intersection:list[TowingVehicle] = generate_schedule_tugs(self.airport,self.atc.ac_schedule,self.ground_control) #full tugs - we might need to add travel down the line
            case Schedule_Algo.aco:
                self.tug_intersection:list[TowingVehicle] = generate_schedule_tugs_2(self.airport,self.atc.ac_schedule,self.ground_control)
            case Schedule_Algo.greedy:
                self.tug_intersection:list[TowingVehicle] = generate_schedule_tugs_3(self.airport,self.atc.ac_schedule,self.ground_control)
            case Schedule_Algo.genetic:
                self.tug_intersection:list[TowingVehicle] = generate_schedule_tugs_4(self.airport,self.atc.ac_schedule,self.ground_control)
        self.num_tugs = len(self.tug_intersection)
        self.tug_travelling:list[TravellingVehicle] = []
        self.current_active_routes:list[ActiveRoute] = []
        self.time:int = 0
        self.state:Status = Status.Running

        
    def _add_new_aircraft(self):
        """Adds new aircraft to the simulation if there is a free gate. Aircraft are added to the corresponding arrival runway off-ramp
        """
        carry = self.atc.add_aircraft(self.time)
        if carry is not None:
            if self.ac_waiting[carry[1]] is not None:
                self.state = Status.Failed_No_Landing_Space
                self.dump_state()
            aircraft = carry[0]
            aircraft.max_travel_time= self.time+self.taxi_margin
            self.ac_waiting[carry[1]] = carry[0]
            logger.debug(f"{self.time}: Aircraft {carry[0].name} arrived at {carry[1]} going to {carry[0].target}, then {carry[0].departure_runway}")

    def _check_loading(self):
        """Determines if an aircraft is finished loading. if so, adds the aircraft to the waiting list
        """
        for i in self.ac_loading:
            if i.loading_completion_time <= self.time:
                logger.debug(f"{self.time}: Aircraft {i.name} completed loading at {i.target}")
                self.ac_loading.remove(i)
                self.ac_waiting[i.target] = i
                i.target = i.departure_runway #Fix this once nodes are defined
                i.max_travel_time= self.time+self.taxi_margin
                i.direction = False
                self.atc.empty_gate(i)

    def _check_tug_waiting(self):
        """ Checks if a tug has an aircraft ready"""
        for i in self.tug_waiting:
            if len(i.schedule) == 0:
                self.tug_waiting.remove(i)
                continue
            if i.pos != i.schedule[0].start_pos:
                logger.debug(f"{i.name} Went to the wrong place - {i.schedule}")
                i.determine_route(self.current_active_routes,self.time,self.ground_control)
                self.current_active_routes.append(ActiveRoute(self.time,i.pos,i.get_next_pos()))
                self.tug_waiting.remove(i)
                self.tug_intersection.append(i)
                continue
            for j in self.ac_waiting.keys():
                if i.pos == j:
                    if self.ac_waiting[j] is not None:
                        aircraft = self.ac_waiting[j]
                        if str(aircraft.name) != str(i.schedule[0].name_ac):
                            continue
                        self.ac_waiting[j] = None  #No longer waiting
                        if aircraft:
                            i.connected_aircraft = aircraft
                            logger.debug(f"{self.time}: Aircraft {i.connected_aircraft.name} picked up at {i.pos} by tug {i.name} going to {i.connected_aircraft.target if i.connected_aircraft.departure_runway else i.connected_aircraft.departure_runway}")
                        else:
                            raise RuntimeError
                        self.tug_waiting.remove(i)
                        self.tug_intersection.append(i)



    def _check_tug_intersection(self):
        """Handles tugs arriving at a node
        """
        for i in self.tug_intersection:
            collision_risk = [x for x in self.tug_intersection if x is not i and x.pos == i.pos]
            if len(collision_risk)>0 and i.pos != 109 and i.pos not in self.airport.gates and i.pos not in self.airport.dept_runways and i.pos not in self.airport.arrival_runways:
                logger.warning(f"{self.time}: Collision!")
                self.state = Status.Failed_Collision
                self.dump_state()
            if i.start_time > self.time:
                continue
            if i.connected_aircraft:
                if i.connected_aircraft.max_travel_time < self.time:
                    logger.debug(f"{self.time}: Aircraft {i.connected_aircraft.name} being towed by {i.name} timed out!")
                    self.state = Status.Failed_Aircraft_Taxi_Time
                    self.dump_state()
            if len(i.next_node_list) == 0: #we have arrived at our destination
                if i.connected_aircraft:
                    if i.pos != i.connected_aircraft.target:
                        i.determine_route(self.current_active_routes,self.time,self.ground_control)
                        logger.debug(f"path for tug {i.name} to {i.get_next_pos()}: {i.next_node_list}")
                        self.current_active_routes.append(ActiveRoute(self.time,i.pos,i.get_next_pos()))
                        continue
                    elif i.pos in self.airport.gates: #The aircraft has arrived at the departure runway
                        i.connected_aircraft.loading_completion_time = self.time + i.connected_aircraft.loading_time
                        self.ac_loading.append(i.connected_aircraft)
                        logger.debug(f"{self.time}: Aircraft {i.connected_aircraft.name} started loading at {i.pos}")
                    elif i.pos in self.airport.dept_runways:
                        logger.debug(f"{self.time}: Aircraft {i.connected_aircraft.name} departing from {i.pos}")
                    else:
                        logger.critical(f"{self.time}: Aircraft {i.connected_aircraft.name} is being dropped off in the wrong place (currently at {i.pos})!!!")
                        self.dump_state()
                        self.state = Status.Failed_Aircraft_Taxi_Time
                    i.connected_aircraft = None
                    i.schedule.pop(0)
                    i.determine_route(self.current_active_routes,self.time,self.ground_control)
                    logger.debug(f"path for tug {i.name}: {i.next_node_list}")

                    self.current_active_routes.append(ActiveRoute(self.time,i.pos,i.get_next_pos()))
                else: #We are waiting
                    if i.pos == 109:
                        if len(i.schedule) == 0:
                            self.tug_intersection.remove(i)
                        i.determine_route(self.current_active_routes,self.time,self.ground_control)
                        logger.debug(f"path for tug {i.name}: {i.next_node_list}")
                        self.current_active_routes.append(ActiveRoute(self.time,i.pos,i.get_next_pos()))
                    else:
                        logger.debug(f"{self.time}: tug {i.name} arrived at {i.pos}. Waiting")
                        self.tug_intersection.remove(i)
                        self.tug_waiting.append(i)
            else:
                #add collision avoidance here TODO's
                logger.debug(f"{self.time} - {i.name} is currently at {i.pos}. Next position: {i.next_node_list[0][0]} at {i.next_node_list[0][1]}")
                if i.next_node_list[0][1] > self.time:
                    continue
                next_node = i.next_node_list.pop(0)[0]
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
                if i in self.airport.dept_runways:
                    self.ac_waiting[i] = None
                    continue
                if self.ac_waiting[i].direction:# type: ignore #arriving
                    if self.ac_waiting[i].max_travel_time < self.time: # type: ignore
                        logger.debug(f"{self.time}: Aircraft {self.ac_waiting[i].name} at {i} waited too long!")
                        self.state = Status.Failed_Aircraft_Taxi_Time
                        self.dump_state()
                else:
                    if self.ac_waiting[i].max_travel_time < self.time: # type: ignore
                        logger.debug(f"{self.time}: Aircraft {self.ac_waiting[i].name} at {i} waited too long!")
                        self.state = Status.Failed_Aircraft_Taxi_Time
                        self.dump_state()

    def _check_tug_travelling(self):
        for i in self.tug_travelling:
            for j in self.tug_travelling:
                if i != j: 
                    if i.departure_node == j.arrival_node and i.arrival_node == j.departure_node and i.arrival_node != i.departure_node and j.arrival_node != j.departure_node:
                        if i.vehicle.connected_aircraft or j.vehicle.connected_aircraft:
                            logger.warning(f"{self.time}: Collision! Head On")
                            self.state = Status.Failed_Collision
                            self.dump_state()
                            break
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
                output["aircraft"].append((self.ac_waiting[i].name,i))
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
    
    def dump_state(self):
        for i in self.tug_waiting:
            logger.debug(f"Tug {i.name} is waiting at {i.pos}. remaining schedule: {i.schedule}")
        for i in self.tug_intersection:
            logger.debug(f"Tug {i.name} is currently at intersection {i.pos}. remaining schedule: {i.schedule}")
        for i in self.tug_travelling:
             logger.debug(f"Tug {i.vehicle.name} is travelling between {i.departure_node} and {i.arrival_node}. remaining schedule: {i.vehicle.schedule}")           


def run_simulation(airport,run_time,ac_freq,taxi_margin,loading_time,schedule_algo:Schedule_Algo,rng):
    sim = Simulation(airport,run_time,ac_freq,taxi_margin,loading_time,schedule_algo,rng)
    while sim.state == Status.Running:
        sim.simulation_tick()
    logger.warning(f"Simulation Ended!\nreason: {sim.state}")
    return sim.state,sim.num_tugs
