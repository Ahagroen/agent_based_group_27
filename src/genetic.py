import random

# Example tow jobs: (start_time, end_time)


def generate_chromosome(num_jobs, max_tugs):
    return [random.randint(0, max_tugs - 1) for _ in range(num_jobs)]

def is_valid_schedule(job_list):
    job_list = sorted(job_list)
    for i in range(1, len(job_list)):
        if job_list[i][0] < job_list[i - 1][1]:
            return False
    return True

def fitness(chromosome, jobs):
    tug_schedules = {}
    for job_index, tug_id in enumerate(chromosome):
        if tug_id not in tug_schedules:
            tug_schedules[tug_id] = []
        tug_schedules[tug_id].append(jobs[job_index])

    penalty = 0
    for job_list in tug_schedules.values():
        if not is_valid_schedule(job_list):
            penalty += 1

    num_tugs_used = len(set(chromosome))
    return -(num_tugs_used + penalty * 1000)  # We want to maximize (minimize negative value)

def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 2)
    return parent1[:point] + parent2[point:]

def mutate(chromosome, max_tugs):
    new = chromosome[:]
    index = random.randint(0, len(chromosome) - 1)
    new[index] = random.randint(0, max_tugs - 1)
    return new

def genetic_algorithm(jobs, max_tugs=10, pop_size=50, generations=100):
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
            print(f"Generation {gen}: Best Fitness = {fitness(best, jobs)}")

    best = max(population, key=lambda c: fitness(c, jobs))
    best_tugs = len(set(best))
    print("\n🎯 Final Best Assignment:", best)
    print("🛠️ Tugs used:", best_tugs)

    return best, best_tugs

# Run it
# if __name__ == "__main__":
#     best_assignment, tug_count = genetic_algorithm(jobs)
