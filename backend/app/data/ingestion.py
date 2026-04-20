import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def download_pune_network(save_path="data/raw/pune_network.graphml"):
    """Download the road network for a smaller area in Pune, India for demonstration."""
    print("Downloading Pune road network (smaller area)...")
    # Central Pune (Shaniwar Wada area)
    lat, lon = 18.51957, 73.85529
    
    # Get drive network within 5km of center
    G = ox.graph_from_point((lat, lon), dist=5000, network_type="drive")
    
    # Add speeds and travel times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    
    # Save the network
    ox.save_graphml(G, filepath=save_path)
    print(f"Network saved to {save_path}")
    return G

def generate_simulated_ems_data(G, num_events=1000, save_path="data/raw/historical_ems.csv"):
    """Generate simulated historical EMS events."""
    print("Generating simulated EMS data...")
    nodes = list(G.nodes())
    
    events = []
    start_date = datetime(2025, 1, 1)
    
    for _ in range(num_events):
        node_id = np.random.choice(nodes)
        node_data = G.nodes[node_id]
        
        # Random timestamp within the last year
        random_days = np.random.randint(0, 365)
        random_hours = np.random.randint(0, 24)
        random_minutes = np.random.randint(0, 60)
        timestamp = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        events.append({
            "timestamp": timestamp,
            "lat": node_data['y'],
            "lon": node_data['x'],
            "node_id": node_id,
            "priority": np.random.choice(["high", "medium", "low"], p=[0.2, 0.5, 0.3])
        })
    
    df = pd.DataFrame(events)
    df.to_csv(save_path, index=False)
    print(f"Simulated EMS data saved to {save_path}")
    return df

def generate_traffic_data(G, save_path="data/raw/traffic_data.csv"):
    """Generate simulated traffic data (time-dependent edge weights)."""
    print("Generating simulated traffic data...")
    edges = list(G.edges(data=True))
    traffic_data = []
    
    # Generate for 24 hours
    for hour in range(24):
        # Traffic multiplier based on hour (peak hours: 8-10 AM, 5-8 PM)
        if 8 <= hour <= 10 or 17 <= hour <= 20:
            multiplier_range = (1.5, 3.0)
        else:
            multiplier_range = (1.0, 1.5)
            
        for u, v, data in edges:
            multiplier = np.random.uniform(*multiplier_range)
            traffic_data.append({
                "hour": hour,
                "u": u,
                "v": v,
                "multiplier": multiplier,
                "travel_time": data.get('travel_time', 1.0) * multiplier
            })
            
    df = pd.DataFrame(traffic_data)
    df.to_csv(save_path, index=False)
    print(f"Simulated traffic data saved to {save_path}")
    return df

if __name__ == "__main__":
    # Ensure data directories exist
    os.makedirs("data/raw", exist_ok=True)
    
    # Run ingestion
    G = download_pune_network()
    generate_simulated_ems_data(G)
    generate_traffic_data(G)
