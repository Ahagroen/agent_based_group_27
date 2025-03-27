from src.environment import Airport
from src.datatypes import Schedule, TowingVehicle



def generate_schedule_tugs(airport:Airport,ac_schedule:list,num_tugs:int)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    missions:list[list[Schedule]] = []
    for i in range(len(ac_schedule)):
        if missions[i%num_tugs]:
            missions[i%num_tugs].append(ac_schedule[i]) #

    #Build the tugs
    tugs = []
    for i in range(num_tugs):
        tugs.append([TowingVehicle(str(i),109,missions[i],None)])
    return tugs


def generate_schedule_tugs_2(airport:Airport,ac_schedule:list,num_tugs:int)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    missions:list[list[Schedule]] = []
    #Ok so basically: compute the time taken for gate-arrival runway and gate-departure runway in the ideal case (both directions are the same)
    #Then you have a known travel time.
    #We know when each AC sched ule starts, so our graph is a directed graph connecting each mission with the next. Since we know 
    #which gate the AC is going to, we can model all possible paths. Best to do this on paper I think
    #So the matrix looks like a triangle, with 
    #Build the tugs
    tugs = []
    for i in range(num_tugs):
        tugs.append([TowingVehicle(str(i),109,missions[i],None)])
    return tugs