import requests
import time
import random
import multiprocessing
import uvicorn
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend', 'app'))

def run_backend():
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)

def simulate_requests():
    print("Starting request simulation in 10 seconds...")
    time.sleep(10) # Wait for backend to start
    
    # Pune bounds (approx)
    lat_min, lat_max = 18.45, 18.60
    lon_min, lon_max = 73.75, 73.95
    
    while True:
        # Create a random emergency
        lat = random.uniform(lat_min, lat_max)
        lon = random.uniform(lon_min, lon_max)
        
        try:
            print(f"Creating emergency at {lat}, {lon}...")
            resp = requests.post("http://localhost:8000/emergency", json={
                "location": [lat, lon],
                "priority": random.choice(["high", "medium", "low"])
            })
            if resp.status_code == 200:
                data = resp.json()
                print(f"Success! Ambulance {data['assigned_ambulance']} dispatched. ETA: {data['eta']:.1f}s")
            else:
                print(f"Failed to create emergency: {resp.text}")
        except Exception as e:
            print(f"Error in simulation: {e}")
            
        # Wait before next emergency
        time.sleep(random.randint(15, 30))

if __name__ == "__main__":
    # Use multiprocessing to run backend and simulation together
    backend_proc = multiprocessing.Process(target=run_backend)
    sim_proc = multiprocessing.Process(target=simulate_requests)
    
    backend_proc.start()
    sim_proc.start()
    
    try:
        backend_proc.join()
        sim_proc.join()
    except KeyboardInterrupt:
        backend_proc.terminate()
        sim_proc.terminate()
