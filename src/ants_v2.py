from loguru import logger
from src.environment import Airport
from src.datatypes import Schedule, TowingVehicle
from src.ground_control import groundControl



def generate_schedule_tugs(airport:Airport,ac_schedule:list,ground_control:groundControl)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    num_tugs = 2
    missions:list[list[Schedule]] = []
    for i in range(num_tugs):
        missions.append([])
    for i in range(len(ac_schedule)):
        missions[i%num_tugs].append(ac_schedule[i]) #

    #Build the tugs
    tugs = []
    counter = 1
    for i in range(num_tugs):
        print(missions[i])
        tugs.append(TowingVehicle(str(i),109,missions[i],counter*15,None))
        counter += 1
    return tugs


def generate_schedule_tugs_2(airport:Airport,ac_schedule:list[Schedule],ground_controller:groundControl)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    times:dict[str,list] = {}#each row = start position, each column = end_position. None means its an invalid entry (or leave it empty?)
    mission_times:dict[tuple,int] = {}# options are Arrivals-gates, gates-departures - Only routes an aircraft can take
    travel_times:dict[tuple,int] = {} #options are 109-arrivals, 109-gates, gates-arrivals (same as arrivals-gates), departures-arrivals, departures-gates(same as gates-departures)
    edge_len = 15
    for i in airport.gates:
        for j in airport.arrival_runways:
            length = len(ground_controller.determine_route(i,j,[]))*edge_len #depends on length of the edges
            mission_times[j,i] = travel_times[i,j] = length
        for j in airport.dept_runways:
            length = len(ground_controller.determine_route(i,j,[]))*edge_len #depends on length of the edges
            mission_times[i,j] = travel_times[j,i] = length
        travel_times[109,i] = len(ground_controller.determine_route(i,109,[]))*edge_len
    for i in airport.arrival_runways:
        for j in airport.dept_runways:
            travel_times[j,i] = len(ground_controller.determine_route(i,j,[]))*edge_len
        travel_times[109,i] = len(ground_controller.determine_route(i,109,[]))*edge_len

    start_time = 0
    times[0] = compute_row(ac_schedule, travel_times, start_time)
    counter = 0
    for i in ac_schedule:#build the tabu
        counter += 1
        times[counter] = compute_row(ac_schedule,travel_times,i.estimated_time+mission_times[i.start_pos,i.end_pos])    
    missions:list[list[Schedule]] = []
    ac_schedule_len = len(ac_schedule)
    while max(times[0]) != 0:
        data = dijkstra(times,ac_schedule_len)
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
        start_time = missions[i][0].estimated_time-travel_times[109,missions[i][0].start_pos]-120
        tugs.append(TowingVehicle(str(i),109,missions[i],start_time,None))
    return tugs

def compute_row(ac_schedule, travel_times, start_time):
    time_list = {0:0}
    margin = 180
    counter = 0
    for i in ac_schedule:
        counter += 1
        if travel_times[109,i.start_pos]+start_time < i.estimated_time:#we can make it 
            time_list[counter] = i.estimated_time-start_time-margin#margin handling? TODO
        else:
            time_list[counter] = 0
    return time_list


def dijkstra(costs_table:dict,ac_schedule_len):
    dist = [0]*(ac_schedule_len+1)
    prev = [None]*(ac_schedule_len+1)
    unchecked = []
    for i in costs_table.keys():
        dist[i] = 9999999999
        prev[i] = None
        unchecked.append(i)
    dist[0] = 0
    while unchecked:
        best_next = None
        min_val = 999999999
        for test in unchecked:
            if dist[test] < min_val:
                min_val = dist[test]
                best_next = test
        unchecked.remove(best_next)
        possible_connection = False
        for mission in unchecked:
            if costs_table[best_next][mission] != 0:
                possible_connection = True
                alt = dist[best_next]+costs_table[best_next][mission]
                if alt < dist[mission]:
                    dist[mission] = alt
                    prev[mission] = best_next
        if not possible_connection:
            break
    data = []
    for i in costs_table.keys():
        if prev[i] is not None:#filter out nodes that were not visited
            working = [i]
            j = prev[i]
            while prev[j]:
                working.append(j)
                j = prev[j]
            data.append(working)
    lengths = [len(x) for x in data]
    if len(lengths) == 0:
        return False
    best = lengths.index(max(lengths))
    return data[best]


def remove_used(times:dict,used_nodes):
    for i in used_nodes:
        times.pop(i)
        for j in times.keys():
            times[j][i] = 0
    return times

    # initial_options:list = costs_table[0]
    # best_choice = initial_options.index(min([i for i in initial_options if i != 0]))#find the index of the smallest non-zero cost


