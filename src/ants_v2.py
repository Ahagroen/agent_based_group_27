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