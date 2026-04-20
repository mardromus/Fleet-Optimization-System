import networkx as nx
import osmnx as ox
import pandas as pd
import numpy as np

class AStarRouter:
    def __init__(self, G):
        self.G = G

    def get_fastest_route(self, origin_node, destination_node, traffic_multipliers=None):
        """Find the fastest route between two nodes using A* with traffic data."""
        # Define the weight function
        def weight_func(u, v, d):
            base_time = d.get('travel_time', 1.0)
            if traffic_multipliers is not None:
                multiplier = traffic_multipliers.get((u, v), 1.0)
                return base_time * multiplier
            return base_time

        # Heuristic: simple distance-based heuristic (e.g., Euclidean distance / max speed)
        def heuristic(u, v):
            # Coordinates
            u_y, u_x = self.G.nodes[u]['y'], self.G.nodes[u]['x']
            v_y, v_x = self.G.nodes[v]['y'], self.G.nodes[v]['x']
            # Great circle distance
            dist = ox.distance.great_circle(u_y, u_x, v_y, v_x)
            # Max speed in Pune (rough estimate 60km/h = 16.6 m/s)
            return dist / 16.6

        try:
            route = nx.astar_path(self.G, origin_node, destination_node, weight=weight_func, heuristic=heuristic)
            return route
        except nx.NetworkXNoPath:
            print(f"No path found between {origin_node} and {destination_node}")
            return None

    def calculate_eta(self, route, traffic_multipliers=None):
        """Calculate the Estimated Time of Arrival (ETA) for a given route."""
        if not route:
            return float('inf')
            
        total_time = 0
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            edge_data = self.G.get_edge_data(u, v)
            if edge_data:
                # Handle multi-edges
                if isinstance(edge_data, dict):
                    # Pick the first edge if multi-edge
                    if 0 in edge_data:
                        edge_data = edge_data[0]
                    else:
                        # If it's a direct dictionary (not multi-edge)
                        pass
                
                base_time = edge_data.get('travel_time', 1.0)
                multiplier = traffic_multipliers.get((u, v), 1.0) if traffic_multipliers else 1.0
                total_time += base_time * multiplier
        
        return total_time

if __name__ == "__main__":
    # Example usage
    try:
        G = ox.load_graphml("data/raw/pune_network.graphml")
        router = AStarRouter(G)
        nodes = list(G.nodes())
        origin = nodes[0]
        destination = nodes[10]
        
        route = router.get_fastest_route(origin, destination)
        eta = router.calculate_eta(route)
        print(f"Route: {route}")
        print(f"ETA: {eta} seconds")
    except FileNotFoundError:
        print("Network graph not found. Please run ingestion script first.")
