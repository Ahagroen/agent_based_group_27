from src.environment import Airport
from src.datatypes import TowingVehicle



def generate_schedule_tugs(airport:Airport,ac_schedule:list,num_tugs:int)->list:
    #So from ac_schedule, determine the mission, and the time taken to complete the mission (runway to gate)
    missions:list = []
    for i in range(len(ac_schedule)):
        missions.append((i%num_tugs,ac_schedule[i])) #
    
    


    #Build the tugs
    tugs = []
    for i in range(num_tugs):
        tugs.append([TowingVehicle(str(i),109,missions,None)])
    return tugs