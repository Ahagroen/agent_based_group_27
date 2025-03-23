from random import seed
from random import randint
from copy import deepcopy

nodes = []
edges = []
num_nodes = 20
#node_radius = 50
#edge_width = 100
#edge_scale = 0.1
weights = []
distances = []
running = False
best_len = 100000000
alpha = 1.0 #pheromone weight
beta = 2.0 #greedy weight
rho = 0.001

seed(101)
rng = randint(0,num_nodes-1)

def run_ACO_batch(batch_size: int):
    # running = False
    #Evaporate
    for i in range(num_nodes):
        for j in range(num_nodes):
            weights[i][j] *= (1-rho) #0.999  # weights[i][j] =  weights[i][j]*0.999  -> does this mean rho is 0.001?
    print(weights)
    new_weights = deepcopy(weights)

    #run the whole batch
    for i in range(batch_size):
        ret = get_random_path_from(rng)
        path = ret[0]
        len = ret[1]
        best_len = 99999999999999999
        if len < best_len:
            best_len = len
        diff = len-best_len+0.05
        w = 0.01/diff #is Q=0.01?
        for i in range(num_nodes + 1):
            idx1 = path[i%num_nodes]
            idx2 = path[(i+1) %num_nodes]
            new_weights[idx1][idx2]+= w
            new_weights[idx2][idx1]+= w

    #update the weights after normalizing
    for i in range(num_nodes):
        n_sum = 0.0
        for j in range(num_nodes):
            if i==j:
                continue
            n_sum += new_weights[i][j]
        for j in range(num_nodes):
            #multiplying by 2 since every node has two neighbors eventally
            weights[i][j] = 2*new_weights[i][j]/n_sum
    #add_edges()
    #draw_stuff()
    return best_len
run_ACO_batch(1)

def get_transition_probability(idx1:int, idx2:int) -> float:
    return weights[idx1][idx2]**alpha * distances[idx1][idx2]**(-beta)
    #return pow(weights[idx1][idx2], alpha)*pow(distances[idx1][idx2], -beta)

def get_random_path_from(idx:int):
    path = []
    dist = 0.0
    path.append(idx)
    curr_idx = idx
    while len(path)<num_nodes:
        n_sum = 0.0
        possible_next = []
        for n in range(num_nodes):
            if n in path: #already visited
                continue
            n_sum += get_transition_probability(curr_idx, n)
            possible_next.append(n)
        r = randint(0, n_sum) #random.uniform(0, n_sum)
        x = 0.0
        for nn in possible_next:
            x += get_transition_probability(curr_idx, nn)
            if r <= x:
                dist =+ distances[curr_idx][nn]
                curr_idx = nn
                path.append(nn)
                break
    dist += distances[curr_idx][idx]
    return [path, dist]

        
