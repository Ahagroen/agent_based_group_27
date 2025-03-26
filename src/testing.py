from ground_control import groundControl
from environment import Airport
import networkx as nx
import matplotlib.pyplot as plt

"""
class Node:
    def __init__(self, edges, x_pos, y_pos):
        self.edges = edges
        self.x_pos = x_pos
        self.y_pos = y_pos

nodes = {
    1: Node([2, 4], 0, 0),
    2: Node([1, 3], 1, 0.5),
    3: Node([2, 6], 2, 0),
    4: Node([1, 5], 0, 1),
    5: Node([4, 6], 1, 1),
    6: Node([3, 5], 2, 1)
}
"""


# Importing Node Data
# -------------------
airport = Airport("../baseline_airport.json")
# print(airport.nodes)
nodes = airport.nodes
nodes = {int(key): value for key, value in nodes.items()}
print(nodes)

# print(nodes["1"])

gc = groundControl(nodes)
start = 38
end = 98
route = gc.determine_route(start, end)
print("Test Route:", route)

# Plotting the path
# -----------------

# Create a graph object
G = nx.Graph()

# Add nodes and edges
for node_id, node in nodes.items():
    G.add_node(node_id, pos=(node.x_pos, -(node.y_pos)))  # for some reason I need to flip the y values
    for neighbor in node.edges:
        G.add_edge(node_id, neighbor)  # Add edges between nodes

# Extract positions from the graph
pos = nx.get_node_attributes(G, 'pos')

# Define the color for the nodes
node_colors = ['red' if node_id in route else 'skyblue' for node_id in G.nodes]

# Plot the graph
plt.figure(figsize=(8, 6))
nx.draw(G, pos, with_labels=True, node_size=700, node_color=node_colors, font_size=12, font_weight='bold',
        edge_color='gray')
plt.title("Node Graph Visualization", fontsize=16)
plt.show()





