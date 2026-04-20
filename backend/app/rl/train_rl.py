import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import osmnx as ox
try:
    from .ambulance_env import AmbulanceFleetEnv
except ImportError:
    from ambulance_env import AmbulanceFleetEnv
import os

class PolicyNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.fc(x)

def train_simplified_rl(G, num_episodes=100):
    """A very simplified training loop for the ambulance dispatch policy."""
    env = AmbulanceFleetEnv(G)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    policy = PolicyNetwork(state_dim, action_dim)
    optimizer = optim.Adam(policy.parameters(), lr=0.001)
    
    print("Starting simplified RL training...")
    for episode in range(num_episodes):
        state, _ = env.reset()
        episode_reward = 0
        
        # Run for 10 steps per episode
        for _ in range(10):
            state_tensor = torch.FloatTensor(state)
            probs = policy(state_tensor)
            
            # Sample action
            action = torch.multinomial(probs, 1).item()
            
            next_state, reward, done, _, info = env.step(action)
            
            # Simplified policy gradient loss
            log_prob = torch.log(probs[action])
            loss = -log_prob * reward # Basic REINFORCE
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            state = next_state
            episode_reward += reward
            
        if (episode + 1) % 10 == 0:
            print(f"Episode {episode+1}, Reward: {episode_reward:.2f}")
            
    # Save model
    os.makedirs("data/processed", exist_ok=True)
    torch.save(policy.state_dict(), "data/processed/ambulance_policy.pth")
    print("RL model saved.")

if __name__ == "__main__":
    try:
        G = ox.load_graphml("data/raw/pune_network.graphml")
        train_simplified_rl(G)
    except FileNotFoundError:
        print("Network graph not found. Please run ingestion script first.")
