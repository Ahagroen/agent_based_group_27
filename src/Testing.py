import pygame
import networkx as nx
import os
import heapq

# Center window
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# Set screen size and create window
screen_width, screen_height = 750, 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Prioritized A* with Labeled Nodes")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 16)

# Define environment as a dictionary of nodes
cols, rows = 5, 5
environment = {"nodes": []}
node_id_map = {}
node_counter = 1
for y in range(rows):
    for x in range(cols):
        environment["nodes"].append({
            "id": node_counter,
            "x": x,
            "y": y
        })
        node_id_map[(x, y)] = node_counter
        node_counter += 1

# Create graph from environment
G = nx.Graph()
for node in environment["nodes"]:
    coord = (node["x"], node["y"])
    G.add_node(coord)
    # Connect to neighbors (up/down/left/right)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        neighbor = (node["x"] + dx, node["y"] + dy)
        if 0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows:
            G.add_edge(coord, neighbor)

# Calculate screen positions for nodes
cell_width = screen_width / cols
cell_height = screen_height / rows
pos = {
    (node["x"], node["y"]): (
        node["x"] * cell_width + cell_width / 2,
        node["y"] * cell_height + cell_height / 2
    )
    for node in environment["nodes"]
}


# Heuristic function for A*
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Check if an edge is free (no other agents using it at the same time)
def is_edge_free(start, goal, reserved_edges):
    # Check if the edge from start to goal is free of other agents
    if (start, goal) in reserved_edges or (goal, start) in reserved_edges:
        return False
    return True


# A* with reservation system (including edge reservation)
def a_star(graph, start, goal, reserved_nodes=None, reserved_edges=None):
    if reserved_nodes is None:
        reserved_nodes = {}
    if reserved_edges is None:
        reserved_edges = {}

    frontier = [(0, start, [])]
    visited = set()

    while frontier:
        cost, current, path = heapq.heappop(frontier)

        if (current, len(path)) in reserved_nodes:
            continue

        path = path + [current]
        if current == goal:
            return path

        for neighbor in graph.neighbors(current):
            if (neighbor, len(path)) not in reserved_nodes:
                # Check if the edge is free (no other agents are on it at this time)
                if not is_edge_free(current, neighbor, reserved_edges):
                    continue
                new_cost = cost + 1
                priority = new_cost + heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor, path))

    return None


# Reservation table builder (tracks only current and future nodes and edges)
def build_reservations(paths, completed_agents):
    reserved_nodes = {}
    reserved_edges = {}  # Track edges as well

    for path in paths:
        for t, node in enumerate(path):
            # Skip reservations for completed agents
            if node not in completed_agents:
                reserved_nodes[(node, t)] = True
                if t < len(path) - 1:
                    # Reserve the edge from node to the next node
                    start = path[t]
                    goal = path[t + 1]
                    reserved_edges[(start, goal)] = True
                    reserved_edges[(goal, start)] = True  # Since edges are bidirectional
    return reserved_nodes, reserved_edges


# Agents and start/goal
agents = [
    {"color": (255, 0, 0), "start": (0, 0), "goal": (4, 4)},  # Red (priority 1)
    {"color": (255, 255, 0), "start": (0, 4), "goal": (4, 0)},  # Yellow (priority 2)
]

# Prioritized planning
planned_paths = []
completed_agents = set()  # Track which agents are completed

for i, agent in enumerate(agents):
    reserved_nodes, reserved_edges = build_reservations(planned_paths, completed_agents)
    path = a_star(G, agent["start"], agent["goal"], reserved_nodes, reserved_edges)
    if not path:
        print(f"Agent {i + 1} could not find a valid path.")
        path = [agent["start"]]
    planned_paths.append(path)

# Convert paths to pixel coordinates
pixel_paths = [[list(pos[node]) for node in path] for path in planned_paths]
agent_positions = [list(path[0]) for path in pixel_paths]
agent_next_indices = [1 for _ in agents]
agent_speed = 5


# --- Drawing function ---
def draw_graph():
    screen.fill((255, 255, 255))

    # Draw edges
    for edge in G.edges():
        pygame.draw.line(screen, (200, 200, 200), pos[edge[0]], pos[edge[1]], 1)

    # Draw nodes with labels
    for node in G.nodes():
        pygame.draw.circle(screen, (173, 216, 230), pos[node], 12)
        label = font.render(str(node_id_map[node]), True, (0, 0, 0))
        screen.blit(label, (pos[node][0] - 6, pos[node][1] - 6))


# --- Main simulation loop ---
running = True
while running:
    clock.tick(30)
    draw_graph()

    # Move agents
    for i, agent in enumerate(agents):
        path = pixel_paths[i]
        index = agent_next_indices[i]

        if index < len(path):
            current = agent_positions[i]
            target = path[index]
            dx, dy = target[0] - current[0], target[1] - current[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist < agent_speed:
                agent_positions[i] = list(target)
                agent_next_indices[i] += 1
                if agent_next_indices[i] >= len(path):
                    completed_agents.add(i)  # Mark this agent as completed
            else:
                agent_positions[i][0] += agent_speed * dx / dist
                agent_positions[i][1] += agent_speed * dy / dist

        pygame.draw.circle(screen, agent["color"], (int(agent_positions[i][0]), int(agent_positions[i][1])), 5)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
