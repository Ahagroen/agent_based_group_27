from src.datatypes import Aircraft,TowingVehicle
from src.atc import ATC
from src.ground_control import groundControl
from src.environment import Airport


#CURRENT ASSUMPTIONS = 2 RUNWAYS (one departing one arriving)

#STATE
num_tugs = 2
ac_freq = 15 #min - standard timestep

ac_waiting:dict[str,list[Aircraft]] = {}#AC waiting at runway (arriving), or gate (departing)
ac_loading:list[Aircraft] = []#AC that are currently loading, 

tug_waiting:list[TowingVehicle] = []
tug_travelling:list[TowingVehicle] = []
tug_intersection:list[TowingVehicle] = []

atc = ATC(ac_freq,10,45,[])
ground_control = groundControl()

def add_new_aircraft(time):
    carry = atc.add_aircraft(time)
    if carry is not None:
        ac_waiting["arv_runway"].append(carry)

def check_loading(time):
    for i in ac_loading:
        if i.loading_completion_time <= time:
            ac_loading.remove(i)
            ac_waiting[i.target.name].append(i)
            i.target = None #Fix this once nodes are defined
            atc.empty_gate(i)

def check_tug_waiting():
    for i in tug_waiting:
        for j in ac_waiting.keys():
            if i.pos.name == j:
                if len(ac_waiting[j])>0:
                    aircraft = ac_waiting[j][0]
                    ac_waiting[j].remove(aircraft)#No longer waiting
                    i.connected_aircraft = aircraft
                    i.next_node_list = ground_control.determine_route(i.pos,aircraft.target)
                    tug_waiting.remove(i)
                    tug_intersection.append(i)


def check_tug_intersection(time):
    for i in tug_intersection:
        tug_intersection.remove(i)
        if i.pos == i.connected_aircraft:
            if i.pos.name == "dep_runway": #The aircraft has arrived at the departure runway
                i.connected_aircraft = None
                tug_waiting.append(i)
            else:
                i.connected_aircraft.loading_completion_time = time + i.connected_aircraft.loading_time
                ac_loading.append(i.connected_aircraft)
                i.connected_aircraft = None
                tug_waiting.append(i)
        else:
            next_node = i.next_node_list.pop(0) 
            i.arrival_time = i.pos.edges[next_node.name]
            i.pos = next_node
            tug_travelling.append(i)

def check_tug_travelling(time):
    for i in tug_travelling:
        if i.arrival_time >= time:
            tug_travelling.remove(i)
            tug_intersection.append(i)





def main():
    time = 0
    while time < 1080:
        check_loading(time)
        add_new_aircraft(time)
        check_tug_waiting()
        check_tug_intersection(time)
        check_tug_travelling(time)
        time +=1


if __name__ == "__main__":
    main()
