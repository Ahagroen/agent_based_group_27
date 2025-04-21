import heapq
import math
from typing import Any
from copy import deepcopy
import src.datatypes as dt
class groundControl:
    def __init__(self, nodes,total_time:int):
        # convert dictionary keys from strings to integers
        nodes = {int(key): value for key, value in nodes.items()}
        self.nodes = nodes
        self.total_time = total_time

    
    def create_current_network(self,invalid_nodes:dict[int,list[int]])->dict[int,Any]:
        working_copy = deepcopy(self.nodes)
        for key,value in working_copy.items():    
            if key in invalid_nodes.keys():
                working_copy[key] = dt.NodePathfinding(value,invalid_nodes[key])
            else:
                working_copy[key] = dt.NodePathfinding(value,[])
        return working_copy

    def determine_route(self, start_pos: int, end_pos: int,invalid_nodes:dict[int,list[int]],start_time:int) -> list[tuple[int,int]]:
        """Determine the route using A* pathfinding algorithm.

        Args:
            start_pos (int): starting node
            end_pos (int): ending node
            invalid_nodes: list of list of nodes that are occupied at any one time - how do we handle edges?

        Returns:
            list[int]: list of nodes to travel to
        """
        # initialize open set (priority queue)
        nodes = self.create_current_network(invalid_nodes)
        open_set = []
        heapq.heappush(open_set, (0, start_pos,start_time))

        # Dictionary to store the best previous node for each visited node
        came_from = {}

        # Dictionary to store the cost from start to each node (g-score)
        g_score = {node: float('inf') for node in nodes}
        g_score[start_pos] = 0

        # Dictionary to store estimated total cost (f-score = g-score + heuristic)
        f_score = {node: float('inf') for node in nodes}
        f_score[start_pos] = heuristic(nodes,start_pos, end_pos)

        while open_set:
            # Get the node with the lowest f-score
            _ , current_node,current_time = heapq.heappop(open_set)

            # If the goal is reached, reconstruct the path
            if current_node == end_pos:
                path = []
                path.append((current_node,current_time))
                while current_node in came_from.keys():
                    path.append(came_from[current_node])
                    current_node = came_from[current_node][0]
                return path[::-1]  # Return reversed path from start to end

            # Explore neighbors
            found = False
            while found != True:
                for neighbor in nodes[current_node].node.edges:
                    arrival_time = current_time+15
                    if any([x in nodes[neighbor].blocked_times for x in range(arrival_time-30,arrival_time+30)]):
                        continue
                    temp_g_score = g_score[current_node] + heuristic(nodes,current_node, neighbor)
                    found = True
                    # If this path to neighbor is better update the records
                    if temp_g_score < g_score[neighbor]:
                        came_from[neighbor] = (current_node,current_time)
                        g_score[neighbor] = temp_g_score
                        f_score[neighbor] = temp_g_score + heuristic(nodes,neighbor, end_pos)

                    # Push updated neighbor into the open set
                        heapq.heappush(open_set, (f_score[neighbor], neighbor, arrival_time))
                if not found:
                    print("No Legal Paths")
                    current_time = arrival_time
     
        return []  # No path found, nodes might not be connected

def heuristic(node_map, node1: int, node2: int) -> float:
        """Calculate Euclidean distance heuristic."""
        x1, y1 = node_map[node1].node.x_pos, node_map[node1].node.y_pos
        x2, y2 = node_map[node2].node.x_pos, node_map[node2].node.y_pos
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

