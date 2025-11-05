#!/usr/bin/env python3
"""
Simple Planet Study Script - Send 3 Morties to one planet repeatedly
Logs results and creates visualization
"""

import requests
import json
import time
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def study_single_planet(token, planet_id, max_trips=100):
    """Study a single planet by sending 1 Morties repeatedly"""
    
    base_url = "https://challenge.sphinxhq.com"
    headers = {"Authorization": f"Bearer {token}"}
    
    planet_names = ["On a Cob", "Cronenberg", "Purge"]
    planet_name = planet_names[planet_id]
    
    print(f"\n{'='*60}")
    print(f"STUDYING PLANET {planet_id}: {planet_name}")
    print(f"{'='*60}")
    
    # Start new episode
    print("Starting new episode...")
    resp = requests.post(f"{base_url}/api/mortys/start/", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to start episode: {resp.status_code}")
        return None
    
    initial_status = resp.json()
    print(f"Initial Morties: {initial_status['morties_in_citadel']}")
    
    # Data collection
    results = []
    trip_number = 0
    morties_remaining = initial_status['morties_in_citadel']
    
    print(f"\nSending groups of 3 Morties to {planet_name}...")
    print("Trip | Result | Saved | Lost | Remaining")
    print("-" * 45)
    
    while trip_number < max_trips and morties_remaining >= 1:
        trip_number += 1
        
        # Send 3 Morties
        try:
            resp = requests.post(
                f"{base_url}/api/mortys/portal/",
                headers=headers,
                json={"planet": planet_id, "morty_count": 1},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                survived = data.get("survived", False)
                morties_saved = data.get("morties_on_planet_jessica", 0)
                morties_lost = data.get("morties_lost", 0)
                morties_remaining = data.get("morties_in_citadel", 0)
                
                # Log result
                results.append({
                    'trip': trip_number,
                    'survived': 1 if survived else 0,
                    'total_saved': morties_saved,
                    'total_lost': morties_lost,
                    'remaining': morties_remaining
                })
                
                symbol = "✅" if survived else "❌"
                print(f"{trip_number:4d} | {symbol:^6} | {morties_saved:5d} | {morties_lost:4d} | {morties_remaining:9d}")
                
            elif resp.status_code == 500:
                print(f"\n⚠️ Server error at trip {trip_number}")
                # Try to get status
                status_resp = requests.get(f"{base_url}/api/mortys/status/", headers=headers)
                if status_resp.status_code == 200:
                    status = status_resp.json()
                    if status.get("morties_in_citadel", 0) == 0:
                        print("All Morties have been processed!")
                break
            else:
                print(f"\n❌ Error {resp.status_code} at trip {trip_number}")
                break
                
            # Small delay to avoid rate limiting
            time.sleep(0.01)
            
        except Exception as e:
            print(f"\n❌ Exception at trip {trip_number}: {e}")
            break
    
    if not results:
        print("No data collected!")
        return None
    
    # Save raw data
    filename = f"./planet0_logs/json/planet_{planet_id}_{planet_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump({
            'planet_id': planet_id,
            'planet_name': planet_name,
            'results': results
        }, f, indent=2)
    print(f"\n📁 Data saved to: {filename}")
    
    return results, planet_name

def visualize_results(results, planet_name):
    """Create visualization of planet performance"""
    
    if not results:
        return
    
    trips = [r['trip'] for r in results]
    survived = [r['survived'] for r in results]
    
    # Calculate running success rate
    cumulative_success = np.cumsum(survived)
    cumulative_trips = np.arange(1, len(survived) + 1)
    running_rate = cumulative_success / cumulative_trips
    
    # Calculate moving average (window of 10)
    window = 10
    moving_avg = []
    for i in range(len(survived)):
        start = max(0, i - window + 1)
        window_data = survived[start:i + 1]
        moving_avg.append(sum(window_data) / len(window_data))
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Planet Study: {planet_name}', fontsize=16, fontweight='bold')
    
    # 1. Individual trip results
    axes[0, 0].bar(trips, survived, color=['red' if s == 0 else 'green' for s in survived], alpha=0.6)
    axes[0, 0].set_title('Individual Trip Results')
    axes[0, 0].set_xlabel('Trip Number')
    axes[0, 0].set_ylabel('Success (1) / Failure (0)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Running success rate
    axes[0, 1].plot(trips, running_rate, 'b-', linewidth=2, label='Cumulative Rate')
    axes[0, 1].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50% line')
    axes[0, 1].fill_between(trips, 0, running_rate, alpha=0.3)
    axes[0, 1].set_title('Cumulative Success Rate')
    axes[0, 1].set_xlabel('Trip Number')
    axes[0, 1].set_ylabel('Success Rate')
    axes[0, 1].set_ylim([0, 1])
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    
    # 3. Moving average
    axes[1, 0].plot(trips, moving_avg, 'purple', linewidth=2, label=f'{window}-trip moving avg')
    axes[1, 0].scatter(trips, survived, alpha=0.3, s=20, color='gray', label='Actual results')
    axes[1, 0].set_title(f'Moving Average (Window={window})')
    axes[1, 0].set_xlabel('Trip Number')
    axes[1, 0].set_ylabel('Success Rate')
    axes[1, 0].set_ylim([-0.1, 1.1])
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    
    # 4. Statistics summary
    axes[1, 1].axis('off')
    stats_text = f"""
    Summary Statistics for {planet_name}:
    
    Total Trips: {len(results)}
    Successes: {sum(survived)}
    Failures: {len(survived) - sum(survived)}
    
    Overall Success Rate: {sum(survived)/len(survived):.1%}
    
    First 10 trips: {sum(survived[:10])/min(10, len(survived)):.1%}
    Last 10 trips: {sum(survived[-10:])/min(10, len(survived)):.1%}
    
    Best streak: {max((sum(1 for _ in g) for k, g in __import__('itertools').groupby(survived) if k), default=0)} successes
    Worst streak: {max((sum(1 for _ in g) for k, g in __import__('itertools').groupby(survived) if not k), default=0)} failures
    """
    axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center', fontfamily='monospace')
    
    plt.tight_layout()
    
    # Save figure
    filename = f"./planet0_logs/png/planet_{planet_name.replace(' ', '_')}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    print(f"📊 Visualization saved to: {filename}")
    
    plt.show()
    
    return running_rate[-1] if running_rate else 0

def main():
    print("="*60)
    print("PLANET BEHAVIOR STUDY TOOL")
    print("="*60)
    
    token = "5cc6cdce490fbfb99d2b61775826a8125be47bce"
    # Get token
    print("\n🪐 Select planet to study:")
    print("0 - On a Cob Planet")
    print("1 - Cronenberg World")
    print("2 - The Purge Planet")
    planet_id = int(input("Planet (0-2): ").strip())
    
    if not token or planet_id not in [0, 1, 2]:
        print("❌ Invalid input!")
        return
    
    print("\n📊 How many trips to make? (default: 100)")
    max_trips = input("Number of trips (press Enter for 100): ").strip()
    max_trips = int(max_trips) if max_trips else 100
    
    # Study the planet
    result = study_single_planet(token, planet_id, max_trips)
    
    if result:
        results, planet_name = result
        final_rate = visualize_results(results, planet_name)
        
        print("\n" + "="*60)
        print(f"STUDY COMPLETE: {planet_name}")
        print(f"Final Success Rate: {final_rate:.1%}")
        print("="*60)

if __name__ == "__main__":
    main()