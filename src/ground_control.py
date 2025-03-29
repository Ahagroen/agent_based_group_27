import heapq
import math



class groundControl:
    def __init__(self, nodes):
        # convert dictionary keys from strings to integers
        nodes = {int(key): value for key, value in nodes.items()}
        self.nodes = nodes

    def heuristic(self, node1: int, node2: int) -> float:
        """Calculate Euclidean distance heuristic."""
        x1, y1 = self.nodes[node1].x_pos, self.nodes[node1].y_pos
        x2, y2 = self.nodes[node2].x_pos, self.nodes[node2].y_pos
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def determine_route(self, start_pos: int, end_pos: int,invalid_nodes:list) -> list[int]:
        """Determine the route using A* pathfinding algorithm.

        Args:
            start_pos (int): starting node
            end_pos (int): ending node
            invalid_nodes: list of list of nodes that are occupied at any one time - how do we handle edges?

        Returns:
            list[int]: list of nodes to travel to
        """
        # initialize open set (priority queue)
        open_set = []
        heapq.heappush(open_set, (0, start_pos))

        # Dictionary to store the best previous node for each visited node
        came_from = {}

        # Dictionary to store the cost from start to each node (g-score)
        g_score = {node: float('inf') for node in self.nodes}
        g_score[start_pos] = 0

        # Dictionary to store estimated total cost (f-score = g-score + heuristic)
        f_score = {node: float('inf') for node in self.nodes}
        f_score[start_pos] = self.heuristic(start_pos, end_pos)

        while open_set:
            # Get the node with the lowest f-score
            _, current = heapq.heappop(open_set)

            # If the goal is reached, reconstruct the path
            if current == end_pos:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_pos)
                return path[::-1]  # Return reversed path from start to end

            # Explore neighbors
            for neighbor in self.nodes[current].edges:
                temp_g_score = g_score[current] + self.heuristic(current, neighbor)

                # If this path to neighbor is better update the records
                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + self.heuristic(neighbor, end_pos)

                    # Push updated neighbor into the open set
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []  # No path found, nodes might not be connected
