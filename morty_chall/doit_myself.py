import requests, json, numpy as np

token = "5cc6cdce490fbfb99d2b61775826a8125be47bce"

base_url = "https://challenge.sphinxhq.com"
headers = {"Authorization": f"Bearer {token}"}
planet_names = ["On a Cob", "Cronenberg", "Purge"]

positions = {0: 0, 1: 0, 2: 0}

total_sent = 0
total_survived = 0
trips = {0: 0, 1: 0, 2: 0}

def start_episode():
    resp = requests.post(f"{base_url}/api/mortys/start/", headers=headers)
    data = resp.json()
    print(f"\n🚀 Episode started!")

    return data

def send_mortys(planet_id, count, position):
    resp = requests.post(f"{base_url}/api/mortys/send/", headers=headers,json={
        "planet_id": planet_id,
        "morty_count": count,})
    
    data = resp.json()
    survived = data.get("survived", False)
    positions[planet_id] = position + 1
    
