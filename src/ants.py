from random import seed,randint,random
from copy import deepcopy

from src.environment import Airport

def compute_schedule(airport:Airport,num_taxibots:int):
    nodes = airport.nodes
    weights = []
    distances = []
    def populate_weights_distances():
        for i in nodes:
            weight_i = []
            distance_i = []
            for j in nodes:
                if j == i:
                    weight_i.append(0.0)
                    distance_i.append(0.0)
                    continue
                else:
                    weight_i.append(1.0)
                    distance_i.append(5.0)
            weights.append(weight_i)
            distances.append(distance_i)
    populate_weights_distances()
    alpha = 1.0 #pheromone weight
    beta = 2.0 #greedy weight
    rho = 0.001

    seed(101)
    rng = randint(0,len(nodes)-1)
    
    def run_ACO_batch(batch_size: int):
        # running = False
        #Evaporate
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                weights[i][j] *= (1-rho) #0.999  # weights[i][j] =  weights[i][j]*0.999  -> does this mean rho is 0.001?
        new_weights = deepcopy(weights)

        #run the whole batch
        for i in range(batch_size):
            ret = get_random_path_from(rng)
            path = ret[0]
            length = ret[1]
            best_len = 99999999999999999
            if length < best_len:
                best_len = length
            diff = length-best_len+0.05
            w = 0.01/diff #is Q=0.01?
            for i in range(len(nodes) + 1):
                idx1 = path[i%len(nodes)]
                idx2 = path[(i+1) %len(nodes)]
                new_weights[idx1][idx2]+= w
                new_weights[idx2][idx1]+= w

        #update the weights after normalizing
        for i in range(len(nodes)):
            n_sum = 0.0
            for j in range(len(nodes)):
                if i==j:
                    continue
                n_sum += new_weights[i][j]
            for j in range(len(nodes)):
                #multiplying by 2 since every node has two neighbors eventally
                weights[i][j] = 2*new_weights[i][j]/n_sum
        #add_edges()
        #draw_stuff()
        return best_len

    def get_transition_probability(idx1:int, idx2:int) -> float:
        return weights[idx1][idx2]**alpha * distances[idx1][idx2]**(-beta)
        #return pow(weights[idx1][idx2], alpha)*pow(distances[idx1][idx2], -beta)

    def get_random_path_from(idx:int):
        path = []
        dist = 0.0
        path.append(idx)
        curr_idx = idx
        while len(path)<len(nodes):
            n_sum = 0.0
            possible_next = []
            for n in range(len(nodes)):
                if n in path: #already visited
                    continue
                n_sum += get_transition_probability(curr_idx, n)
                possible_next.append(n)
            r = random()*n_sum #random.uniform(0, n_sum)
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
    
    print(run_ACO_batch(1))
        
