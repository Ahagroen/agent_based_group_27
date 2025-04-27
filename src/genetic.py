import random

def generate_chromosome(num_jobs, max_tugs):
    return [random.randint(0, max_tugs - 1) for _ in range(num_jobs)]

def is_valid_schedule(job_list):
    job_list = sorted(job_list)
    for i in range(1, len(job_list)):
        if job_list[i][0] < job_list[i - 1][1]:
            return False
    return True

def fitness(chromosome, jobs):
    from collections import defaultdict

    tug_schedules = defaultdict(list)
    for job_index, tug_id in enumerate(chromosome):
        tug_schedules[tug_id].append(jobs[job_index])

    total_penalty = 0
    total_idle_time = 0

    for job_list in tug_schedules.values():
        sorted_jobs = sorted(job_list)
        for i in range(1, len(sorted_jobs)):
            if sorted_jobs[i][0] < sorted_jobs[i - 1][1]:
                # Overlap => heavily penalize
                return -1_000_000
        if sorted_jobs:
            # Tug used time: time span covered
            start = sorted_jobs[0][0]
            end = sorted_jobs[-1][1]
            total_span = end - start
            active_time = sum(j[1] - j[0] for j in sorted_jobs)
            total_idle_time += (total_span - active_time)

    num_tugs_used = len(tug_schedules)
    return -(num_tugs_used * 1000 + total_idle_time)  # Lower is better


def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 2)
    return parent1[:point] + parent2[point:]

def mutate(chromosome, max_tugs):
    new = chromosome[:]
    index = random.randint(0, len(chromosome) - 1)
    new[index] = random.randint(0, max_tugs - 1)
    return new

def genetic_algorithm(jobs, max_tugs= 20, pop_size=50, generations=500):
    population = [generate_chromosome(len(jobs), max_tugs) for _ in range(pop_size)]

    for gen in range(generations):
        population.sort(key=lambda c: fitness(c, jobs), reverse=True)
        next_gen = population[:10]  # Elitism

        while len(next_gen) < pop_size:
            parent1, parent2 = random.sample(population[:25], 2)
            child = crossover(parent1, parent2)
            if random.random() < 0.3:
                child = mutate(child, max_tugs)
            next_gen.append(child)

        population = next_gen

        if gen % 10 == 0:
            best = max(population, key=lambda c: fitness(c, jobs))
            #print(f"Generation {gen}: Best Fitness = {fitness(best, jobs)}")

    best = max(population, key=lambda c: fitness(c, jobs))
    # if fitness(best,jobs) <= -1000000:
    #     raise RuntimeError
    best_tugs = len(set(best))
    #print("Final Best Assignment:", best)
    #print("Tugs used:", best_tugs)

    return best, best_tugs

def merge_tug_assignments(chromosome, jobs):
    from collections import defaultdict

    # Step 1: Build the tug schedules
    tug_schedules = defaultdict(list)
    for i, tug in enumerate(chromosome):
        tug_schedules[tug].append((jobs[i][0], jobs[i][1], i))  # store index too

    # Step 2: Build a list of all tug job sets, sorted
    schedules = []
    for job_list in tug_schedules.values():
        schedule = sorted(job_list)  # by start time
        schedules.append(schedule)

    # Step 3: Try to greedily merge tugs
    merged_schedules = []

    for schedule in schedules:
        merged = False
        for existing in merged_schedules:
            # Try merging this schedule into 'existing'
            combined = sorted(existing + schedule)
            valid = True
            for i in range(1, len(combined)):
                if combined[i][0] < combined[i - 1][1]:
                    valid = False
                    break
            if valid:
                existing.extend(schedule)
                existing.sort()
                merged = True
                break
        if not merged:
            merged_schedules.append(schedule)

    # Step 4: Reassign tug IDs based on merged schedules
    new_assignment = [None] * len(jobs)
    for new_tug_id, schedule in enumerate(merged_schedules):
        for _, _, job_idx in schedule:
            new_assignment[job_idx] = new_tug_id

    return new_assignment, len(merged_schedules)

def find_min_tugs(jobs, pop_size=50, generations=300):
    best_solution = None

    for t in range(len(jobs)//2 + 1,1,-1):
        #print(f"\n🔍 Trying with max_tugs = {t}")
        best, used = genetic_algorithm(jobs, max_tugs=t, pop_size=pop_size, generations=generations)

        if fitness(best, jobs) == -1_000_000:
            #print(f"Infeasible with {t} tugs.")
            #return best_solution
            pass
        else:
            #print(f"Feasible with {used} tugs.")
            if best_solution:
                if best_solution[1] > used:
                    best_solution = (best, used)
            else:
                best_solution = (best,used)

    return best_solution


# Run it
# if __name__ == "__main__":
#     best_assignment, tug_count = genetic_algorithm(jobs)
