import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox

class AmbulanceFleetEnv(gym.Env):
    """A simplified environment for ambulance fleet optimization."""
    def __init__(self, G, num_ambulances=5, hotspots=None):
        super(AmbulanceFleetEnv, self).__init__()
        self.G = G
        self.num_ambulances = num_ambulances
        self.hotspots = hotspots if hotspots is not None else []
        self.nodes = list(G.nodes())
        
        # State: [amb_1_node, amb_1_status, ..., amb_n_node, amb_n_status, emergency_node, emergency_status]
        # Status: 0 = idle, 1 = busy (dispatched)
        self.observation_space = spaces.Box(
            low=0, 
            high=max(self.nodes), 
            shape=(num_ambulances * 2 + 2,), 
            dtype=np.float32
        )
        
        # Action: Dispatch ambulance index (0 to num_ambulances-1)
        self.action_space = spaces.Discrete(num_ambulances)
        
        # Initialize state
        self.state = None
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Randomly place ambulances
        self.ambulance_locations = np.random.choice(self.nodes, self.num_ambulances)
        self.ambulance_status = np.zeros(self.num_ambulances) # 0 for idle
        
        # Randomly pick an emergency location
        self.emergency_location = np.random.choice(self.nodes)
        self.emergency_status = 1 # Active
        
        # Build state vector
        state_list = []
        for i in range(self.num_ambulances):
            state_list.extend([self.ambulance_locations[i], self.ambulance_status[i]])
        state_list.extend([self.emergency_location, self.emergency_status])
        
        self.state = np.array(state_list, dtype=np.float32)
        return self.state, {}

    def step(self, action):
        """Dispatch ambulance 'action' to 'emergency_location'."""
        amb_idx = action
        
        # If the ambulance is already busy, high negative reward
        if self.ambulance_status[amb_idx] == 1:
            reward = -100
            done = False
            return self.state, reward, done, False, {"error": "Ambulance busy"}
        
        # Calculate travel time (response time)
        try:
            # Shortest path time between ambulance and emergency
            response_time = nx.shortest_path_length(self.G, 
                                                    self.ambulance_locations[amb_idx], 
                                                    self.emergency_location, 
                                                    weight='travel_time')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            response_time = 3600 # Assume 1 hour if no path
            
        # Reward: negative response time (Golden Hour: minimize)
        reward = -response_time / 60.0 # Reward in minutes
        
        # If response time < 8 mins (Golden Hour goal), positive reward bonus
        if response_time < 480: # 8 mins
            reward += 10
            
        # Update ambulance status
        self.ambulance_locations[amb_idx] = self.emergency_location
        self.ambulance_status[amb_idx] = 1 # Mark as busy (will reset later in simulation)
        
        # New emergency
        self.emergency_location = np.random.choice(self.nodes)
        self.emergency_status = 1
        
        # Update state
        state_list = []
        for i in range(self.num_ambulances):
            state_list.extend([self.ambulance_locations[i], self.ambulance_status[i]])
        state_list.extend([self.emergency_location, self.emergency_status])
        self.state = np.array(state_list, dtype=np.float32)
        
        done = False # Continuous environment
        return self.state, reward, done, False, {"response_time": response_time}

    def render(self):
        print(f"Ambulances: {self.ambulance_locations}, Status: {self.ambulance_status}")
        print(f"Next Emergency: {self.emergency_location}")

if __name__ == "__main__":
    # Example usage
    try:
        G = ox.load_graphml("data/raw/pune_network.graphml")
        env = AmbulanceFleetEnv(G)
        obs, _ = env.reset()
        action = env.action_space.sample()
        obs, reward, done, _, info = env.step(action)
        print(f"Reward: {reward}, Info: {info}")
    except FileNotFoundError:
        print("Network graph not found. Please run ingestion script first.")
