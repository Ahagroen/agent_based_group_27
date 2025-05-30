from dataclasses import dataclass
from random import choices, seed
from loguru import logger
from src.environment import Airport
from src.datatypes import Schedule, TowingVehicle
from src.genetic import find_min_tugs, genetic_algorithm, merge_tug_assignments
from src.ground_control import groundControl
from copy import deepcopy


def generate_schedule_tugs(airport:Airport,ac_schedule:list,ground_control:groundControl)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    """
    Generate the towing vehicle schedule with a naive approach. Not intended for meaningful use, but mainly as an indication for the formulation of a scheduling algorithm.

    Inputs:
        airport(Airport): the airport object for the simulation
        ac_schedule(List(Schedule)): A list of all aircraft that will be spawned, based on the ideal arrival times
        ground_control(groundControl): a groundControl object for use to generate paths
    Outputs:
        list(TowingVehicles): List of towing vehicles required for the simulation, preloaded with its schedule

    """
    tugs = []
    working_ac = deepcopy(ac_schedule)
    margin = 180
    edge_len = 15
    ac_schedule.sort(key=lambda x: x.estimated_time)
    while len(working_ac) > 0:
        new_tug = []
        next_schedule = working_ac.pop(0)
        new_tug.append(next_schedule)
        eligible = [x for x in working_ac if x.estimated_time > (next_schedule.estimated_time + len(ground_control.determine_route(next_schedule.start_pos,next_schedule.end_pos,{},0))*edge_len + 
                                                                   len(ground_control.determine_route(next_schedule.end_pos,x.start_pos,{},0))*edge_len+margin)] 
        while len(eligible) >0:
            next_schedule = eligible.pop(0)
            working_ac.remove(next_schedule)
            new_tug.append(next_schedule)
            eligible = [x for x in working_ac if x.estimated_time > (next_schedule.estimated_time + len(ground_control.determine_route(next_schedule.start_pos,next_schedule.end_pos,{},0))*edge_len + 
                                                                      len(ground_control.determine_route(next_schedule.end_pos,x.start_pos,{},0))*edge_len+margin)] 
        tugs.append(new_tug)
    num_tugs = len(tugs)
    carry_tugs = []
    logger.info(f"Number of tugs: {num_tugs}")
    for i in range(num_tugs):
        logger.debug(f"Tug schedule for tug {i}: {tugs[i]}")
        carry_tugs.append(TowingVehicle(str(i),109,tugs[i],tugs[i][0].estimated_time-180,None))
    return carry_tugs


def generate_schedule_tugs_2(airport:Airport,ac_schedule:list[Schedule],ground_controller:groundControl,num_cycles:int=10,num_ants:int=250,Q:int=1,rho=0.2)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    """
    Generate towing vehicles with preloaded schedule using an Ant Colony Optimization approach
    Inputs:
        airport(Airport): the airport object for the simulation
        ac_schedule(List(Schedule)): A list of all aircraft that will be spawned, based on the ideal arrival times
        ground_control(groundControl): a groundControl object for use to generate paths
        num_cycles(int)=10: The number of iterations of the algorithm
        num_ants(int)=250: the number of ants to consider to the algorithm
        Q(int)=250: the Q value for pheremone determination
        rho(int)=0.2: the rho value for pheremone decay
    Outputs:
        list(TowingVehicles): List of towing vehicles required for the simulation, preloaded with its schedule


    """
    times:dict[int,list[int]] = {}#each row = start position, each column = end_position. None means its an invalid entry (or leave it empty?)
    travel_times:dict[tuple,int] = {} #options are 109-arrivals, 109-gates, gates-arrivals (same as arrivals-gates), departures-arrivals, departures-gates(same as gates-departures)
    edge_len = 15
    for i in airport.gates:
        for j in airport.arrival_runways:
            length = len(ground_controller.determine_route(i,j,{},0))*edge_len #depends on length of the edges
            travel_times[j,i] = length
        travel_times[109,i] = len(ground_controller.determine_route(i,109,{},0))*edge_len
    for i in airport.arrival_runways:
        for j in airport.arrival_runways:
            if i == j:
                travel_times[j,i] = 0
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        for j in airport.dept_runways:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        for j in airport.gates:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        travel_times[109,i] = len(ground_controller.determine_route(i,109,{},0))*edge_len
    for i in airport.gates:
        for j in airport.dept_runways:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        for j in airport.gates:
            if i == j:
                travel_times[j,i] = 0
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
    for i in airport.dept_runways:
        for j in airport.gates:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
    start_time = 0
    costs = {}
    times[0] = compute_row(ac_schedule, travel_times, start_time,109)
    costs[0] = compute_costs(ac_schedule, start_time)
    counter = 0
    for i in ac_schedule:#build the tabu
        counter += 1
        times[counter] = compute_row(ac_schedule,travel_times,i.estimated_time+travel_times[i.start_pos,i.end_pos],i.end_pos)  
        costs[counter] = compute_costs(ac_schedule, i.estimated_time+travel_times[i.start_pos,i.end_pos])
    num_tugs,schedule_nodes = populate_aco(times,costs,num_cycles,num_ants,Q,rho)
    schedules = []
    for i in schedule_nodes:
        schedule_i = []
        for j in i:
            schedule_i.append(ac_schedule[j-1])
        schedules.append(schedule_i)



    #Then you have a known travel time.
    #We know when each AC sched ule starts, so our graph is a directed graph connecting each mission with the next. Since we know 
    #which gate the AC is going to, we can model all possible paths. Best to do this on paper I think
    #So the matrix looks like a triangle, with 
    #Build the tugs
    tugs = []
    logger.info(f"Required Number of tugs:{num_tugs}")
    for i in range(len(schedules)):
        start_time = schedules[i][0].estimated_time-travel_times[109,schedules[i][0].start_pos]-180
        tugs.append(TowingVehicle(str(i),109,schedules[i],start_time,None))
    return tugs

def populate_aco(connections_list, cost_dict, num_cycles,num_ants,Q,rho,rand_seed:int=-1)->tuple[int,list]:
    """
    Run the ant colony optimzation
    """

    pheremones_dict = {}
    for i in connections_list.keys():
        pheremones_dict[i] = {}
        for j in connections_list[i]:
            pheremones_dict[i][j] = 0
    base_pheremones_dict = deepcopy(pheremones_dict)
    for i in pheremones_dict.keys():
        for j in pheremones_dict[i].keys():
            pheremones_dict[i][j] = 1
    if rand_seed != -1:
        seed(rand_seed)

    def determine_weights(start_node,options,pheremones)->list:
        alpha = 1
        beta = 1
        weights_list = []
        sum_total = 0
        for i in options:
            distance = cost_dict[start_node][i]
            pheremones_val = pheremones[start_node][i]
            total = pheremones_val**alpha*1/distance**beta 
            sum_total += total
            weights_list.append(total)
        return [x/sum_total for x in weights_list]

    class Ant():
        """
        Ant Class for the ACO, inputs are the pheremones dictionary for a deepcopy of it for analysis
        """
        def __init__(self,pheremones):
            self.position = 0
            self.options = deepcopy(pheremones)
            self.nodes_list = []
            self.trips_list = []
            self.already_visited = []
            self.alive = True
        def go_to_next(self):
            options = list(set(self.options[self.position].keys()) - set(self.already_visited)) 
            if len(options) == 0:
                self.already_visited = self.already_visited + self.nodes_list
                if self.position == 0:
                     self.alive = False
                     return
                else:
                    self.trips_list.append(self.nodes_list)
                    self.position = 0
                    self.nodes_list = []
                return 
            else:
                weights = determine_weights(self.position,options,self.options) 
                choice = choices(options,weights=weights)[0]
                self.nodes_list.append(choice)
                self.position = choice

        def return_performance(self)->tuple[int,list]:
            num_tugs = len(self.trips_list)
            used_nodes = []
            for i in self.trips_list:
                used_nodes.append((0,i[0]))
                for j in range(1,len(i)):
                    used_nodes.append((i[j-1],i[j]))
            return num_tugs,used_nodes


    for run in range(num_cycles):
        ants_list = []
        for _ in range(num_ants):
            ants_list.append(Ant(pheremones_dict))
        while any([x.alive for x in ants_list]):
            for ant in ants_list:
                if ant.alive:
                    ant.go_to_next()
        updating = deepcopy(base_pheremones_dict)
        for ant in ants_list:
            num_tugs,edges = ant.return_performance()
            delta_ph = Q/(num_tugs*100)
            for i in edges:
                updating[i[0]][i[1]] += delta_ph 
        for i in pheremones_dict.keys():
            for j in pheremones_dict[i].keys():
                pheremones_dict[i][j] = (1-rho)*pheremones_dict[i][j] + updating[i][j]

    return compute_ideal(pheremones_dict)
def compute_ideal(pheremone)->tuple[int,list]:
    """
    Compute the ideal path, by selecting the highest pheremone option at each step
    """
    tug_missions = []
    used_nodes = []
    while len(used_nodes) < len(pheremone.keys())-1:
        start_node = 0
        current_mission = []
        while len(pheremone[start_node]) > 0:
            eligible = [x for x in pheremone[start_node].keys() if x not in used_nodes]
            if len(eligible) == 0:
                break
            next_node = max(eligible, key=lambda x: pheremone[start_node][x])
            used_nodes.append(next_node)
            current_mission.append(next_node)
            start_node = next_node
        tug_missions.append(current_mission)
    return len(tug_missions),tug_missions

def compute_costs(ac_schedule, start_time):
    data = {}
    counter = 0
    for i in ac_schedule:
        counter += 1
        if start_time<i.estimated_time:
            data[counter] = i.estimated_time-start_time #the wait time between missions
    return data

def compute_row(ac_schedule, travel_times, start_time,start_node):
    time_list = []
    margin = 180
    counter = 0
    for i in ac_schedule:
        counter += 1
        if start_node == i.start_pos:
            if start_time+margin < i.estimated_time:
                time_list.append(counter)#margin handling? TODO
        else:
            if travel_times[start_node,i.start_pos]+start_time+margin < i.estimated_time:#we can make it 
                time_list.append(counter)
    return time_list

def generate_schedule_tugs_3(airport:Airport,ac_schedule:list[Schedule],ground_controller:groundControl)->list:
    """
    Generate the towing vehicles for the simulation with pre-loaded schedules using a greedy algorithm
    Inputs:
        airport(Airport): the airport object for the simulation
        ac_schedule(List(Schedule)): A list of all aircraft that will be spawned, based on the ideal arrival times
        ground_control(groundControl): a groundControl object for use to generate paths
    Outputs:
        list(TowingVehicles): List of towing vehicles required for the simulation, preloaded with its schedule

    """
    margin = 180
    ac_schedule.sort(key=lambda x: x.estimated_time)
    travel_times:dict[tuple,int] = {} #Pre-compute paths to save computational cost
    edge_len = 15
    for i in airport.gates:
        for j in airport.arrival_runways:
            length = len(ground_controller.determine_route(i,j,{},0))*edge_len #depends on length of the edges
            travel_times[j,i] = length
        travel_times[109,i] = len(ground_controller.determine_route(i,109,{},0))*edge_len
    for i in airport.arrival_runways:
        for j in airport.arrival_runways:
            if i == j:
                travel_times[j,i] = 0
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        for j in airport.dept_runways:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        for j in airport.gates:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        travel_times[109,i] = len(ground_controller.determine_route(i,109,{},0))*edge_len
    for i in airport.gates:
        for j in airport.dept_runways:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        for j in airport.gates:
            if i == j:
                travel_times[j,i] = 0
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
    for i in airport.dept_runways:
        for j in airport.gates:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
    @dataclass
    class tug_carry:
        missions:list
        last_finish_time:int = 0
        last_node:int = 109
    tug_list = [tug_carry([])]
    for i in ac_schedule:
        eligible = [x for x in tug_list if x.last_finish_time+travel_times[x.last_node,i.start_pos]+margin < i.estimated_time]
        eligible.sort(key=lambda x: x.last_finish_time)
        if len(eligible) > 0:
            eligible[0].missions.append(i)
            eligible[0].last_finish_time = i.estimated_time + travel_times[i.start_pos,i.end_pos] 
            eligible[0].last_node = i.end_pos
        else:
            tug_list.append(tug_carry([i],i.estimated_time + travel_times[i.start_pos,i.end_pos],i.end_pos))
    schedules = [x.missions for x in tug_list]
    tugs = []
    logger.info(f"Required Number of tugs:{len(schedules)}")
    for i in range(len(schedules)):
        start_time = schedules[i][0].estimated_time-len(ground_controller.determine_route(109,schedules[i][0].start_pos,{},0))*15-180
        tugs.append(TowingVehicle(str(i),109,schedules[i],start_time,None))
    return tugs

def remove_used(times:dict,used_nodes):
    for i in used_nodes:
        times.pop(i)
        for j in times.keys():
            times[j][i] = 0
    return times

    # initial_options:list = costs_table[0]
    # best_choice = initial_options.index(min([i for i in initial_options if i != 0]))#find the index of the smallest non-zero cost

def generate_schedule_tugs_4(airport:Airport,ac_schedule:list[Schedule],ground_controller:groundControl)->list:
    """
    Generate towing vehicles for the simulation with pre-loaded schedules using a genetic algorithm
    Inputs:
        airport(Airport): the airport object for the simulation
        ac_schedule(List(Schedule)): A list of all aircraft that will be spawned, based on the ideal arrival times
        ground_control(groundControl): a groundControl object for use to generate paths
    Outputs:
        list(TowingVehicles): List of towing vehicles required for the simulation, preloaded with its schedule

    """
    jobs = []
    ac_schedule.sort(key=lambda x: x.estimated_time)
    for i in ac_schedule:
        start_time = i.estimated_time
        end_time = start_time + len(ground_controller.determine_route(i.start_pos, i.end_pos, {}, 0))*15+350+180
        #determine_route(self, start_pos: int, end_pos: int,invalid_nodes:dict[int,list[int]],start_time:int) -> list[tuple[int,int]]:
        jobs.append((start_time, end_time))
    
    #here genetic algorithm

    #best_assignment, tug_count = genetic_algorithm(jobs)

    #clean_assignment, final_tugs = merge_tug_assignments(best_assignment, jobs)
    value = find_min_tugs(jobs, pop_size=30, generations=300)
    if value:
        best_assignment, min_tugs = value
    else:
        raise RuntimeError
    #logger.debug(f"Best feasible schedule uses {min_tugs} tugs.")
    #print(f"\nBest feasible schedule uses {min_tugs} tugs.")
    #print(best_assignment)
    #now convert back final best assignment output (which is best chromosome):
    #->what output format do we want? e.g. [[1,3,4,5], [2,6,5,8]], so list of lists of missions per tug
    #maximum = max(best_assignment) # or just use tug_count instead of maximum?

    missions_list = []
    #for j in range (0, min_tugs): #j is tug index
    for j in set(best_assignment):
        missions_indiv = []
        for i in range(len(best_assignment)): #i is index from best_assignment
            if j==best_assignment[i]:
                missions_indiv.append(ac_schedule[i])
        missions_list.append(missions_indiv)
    for i in missions_list:
        if len(i) == 0:
            #print(i)
            missions_list.remove(i)

    #print(missions_list)
    tugs = []
    logger.info(f"Required Number of tugs:{len(missions_list)}")
    for i in range(len(missions_list)):
        start_time = missions_list[i][0].estimated_time-len(ground_controller.determine_route(109,missions_list[i][0].start_pos,{},0))*15-180
        tugs.append(TowingVehicle(str(i),109,missions_list[i],start_time,None))
    return tugs


