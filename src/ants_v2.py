from loguru import logger
from src.environment import Airport
from src.datatypes import Schedule, TowingVehicle
from src.ground_control import groundControl
from copy import deepcopy


def generate_schedule_tugs(airport:Airport,ac_schedule:list,ground_control:groundControl)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    tugs = []
    working_ac = deepcopy(ac_schedule)
    margin = 400
    edge_len = 15
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


def generate_schedule_tugs_2(airport:Airport,ac_schedule:list[Schedule],ground_controller:groundControl)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    times:dict[int,dict[int,int]] = {}#each row = start position, each column = end_position. None means its an invalid entry (or leave it empty?)
    mission_times:dict[tuple,int] = {}# options are Arrivals-gates, gates-departures - Only routes an aircraft can take
    travel_times:dict[tuple,int] = {} #options are 109-arrivals, 109-gates, gates-arrivals (same as arrivals-gates), departures-arrivals, departures-gates(same as gates-departures)
    edge_len = 15
    for i in airport.gates:
        for j in airport.arrival_runways:
            length = len(ground_controller.determine_route(i,j,{},0))*edge_len #depends on length of the edges
            mission_times[j,i] = travel_times[i,j] = length
        for j in airport.dept_runways:
            length = len(ground_controller.determine_route(i,j,{},0))*edge_len #depends on length of the edges
            mission_times[i,j] = travel_times[j,i] = length
        travel_times[109,i] = len(ground_controller.determine_route(i,109,{},0))*edge_len
    for i in airport.arrival_runways:
        for j in airport.arrival_runways:
            if i == j:
                continue
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
                continue
            travel_times[j,i] = len(ground_controller.determine_route(i,j,{},0))*edge_len
        travel_times[109,i] = len(ground_controller.determine_route(i,109,{},0))*edge_len
    start_time = 0
    times[0] = compute_row(ac_schedule, travel_times, start_time,109)
    counter = 0
    for i in ac_schedule:#build the tabu
        counter += 1
        times[counter] = compute_row(ac_schedule,travel_times,i.estimated_time+mission_times[i.start_pos,i.end_pos],i.end_pos)    
    missions:list[list[Schedule]] = []
    ac_schedule_len = len(ac_schedule)
    while max(times[0]) != 0:
        data = route(times,ac_schedule_len)
        if not data:
            break
        times = remove_used(times,data)
        mission_data = [ac_schedule[i-1] for i in data]
        mission_data.reverse()
        missions.append(mission_data)

    #Ok so basically: compute the time taken for gate-arrival runway and gate-departure runway in the ideal case (both directions are the same)
    #Then you have a known travel time.
    #We know when each AC sched ule starts, so our graph is a directed graph connecting each mission with the next. Since we know 
    #which gate the AC is going to, we can model all possible paths. Best to do this on paper I think
    #So the matrix looks like a triangle, with 
    #Build the tugs
    tugs = []
    logger.info(f"Required Number of tugs:{len(missions)}")
    for i in range(len(missions)):
        start_time = missions[i][0].estimated_time-travel_times[109,missions[i][0].start_pos]-180
        tugs.append(TowingVehicle(str(i),109,missions[i],start_time,None))
    return tugs

def compute_row(ac_schedule, travel_times, start_time,start_node):
    time_list = {0:travel_times[start_node,109]}
    margin = 1
    counter = 0
    for i in ac_schedule:
        counter += 1
        if start_node == i.start_pos:
            if start_time+margin < i.estimated_time:
                time_list[counter] = margin#margin handling? TODO
        else:
            if travel_times[start_node,i.start_pos]+start_time+margin < i.estimated_time:#we can make it 
                time_list[counter] = travel_times[start_node,i.start_pos]+margin#margin handling? TODO
    return time_list


def naieve_route(costs_table:dict,ac_schedule_len):
   pass 

def remove_used(times:dict,used_nodes):
    for i in used_nodes:
        times.pop(i)
        for j in times.keys():
            times[j][i] = 0
    return times

    # initial_options:list = costs_table[0]
    # best_choice = initial_options.index(min([i for i in initial_options if i != 0]))#find the index of the smallest non-zero cost


