#!/usr/bin/env python3
"""
Study All Planets - Send 3 Morties to each planet and compare
"""

import requests
import json
import time
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def study_all_planets(token, trips_per_planet=30):
    """Study all three planets in one episode"""
    
    base_url = "https://challenge.sphinxhq.com"
    headers = {"Authorization": f"Bearer {token}"}
    
    planet_names = ["On a Cob", "Cronenberg", "Purge"]
    
    print(f"\n{'='*60}")
    print(f"STUDYING ALL PLANETS - {trips_per_planet} trips each")
    print(f"{'='*60}")
    
    # Start new episode
    print("\nStarting new episode...")
    resp = requests.post(f"{base_url}/api/mortys/start/", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to start episode: {resp.status_code}")
        return None
    
    initial_status = resp.json()
    print(f"Initial Morties: {initial_status['morties_in_citadel']}")
    
    # Data collection for all planets
    all_results = {0: [], 1: [], 2: []}
    
    print(f"\nSending groups of 3 Morties to each planet...")
    print("\nTrip | Planet      | Result | Saved | Lost | Remaining")
    print("-" * 60)
    
    overall_trip = 0
    morties_remaining = initial_status['morties_in_citadel']
    
    # Study each planet
    while morties_remaining > 0:
        for planet_id in range(3):
            print(f"\n--- Testing {planet_names[planet_id]} ---")
            
            for trip in range(trips_per_planet):
                    
                
                # Send only 1 Morty this time
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
                        all_results[planet_id].append({
                            'trip': trip + 1,
                            'overall_trip': 1000 - morties_remaining,
                            'survived': 1 if survived else 0,
                            'total_saved': morties_saved,
                            'total_lost': morties_lost,
                            'remaining': morties_remaining
                        })
                        
                        symbol = "✅" if survived else "❌"
                        print(f"{overall_trip:4d} | {planet_names[planet_id]:11} | {symbol:^6} | {morties_saved:5d} | {morties_lost:4d} | {morties_remaining:9d}")
                        
                    elif resp.status_code == 500:
                        print(f"\n⚠️ Server error at trip {overall_trip}")
                        break
                    else:
                        print(f"\n❌ Error {resp.status_code} at trip {overall_trip}")
                        break
                        
                    # Small delay
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"\n❌ Exception at trip {overall_trip}: {e}")
                    break
        
    # Save all data
    filename = f"./all_planets/json/all_planets_study_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump({
            'trips_per_planet': trips_per_planet,
            'results': {
                planet_names[i]: all_results[i] for i in range(3)
            }
        }, f, indent=2)
    print(f"\n📁 Data saved to: {filename}")
    
    return all_results, planet_names

def visualize_comparison(all_results, planet_names):
    """Create comparison visualization of all planets"""
    
    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Planet Comparison Study - Sending 3 Morties per Trip', fontsize=16, fontweight='bold')
    
    colors = ['red', 'blue', 'green']
    
    for idx, planet_id in enumerate([0, 1, 2]):
        results = all_results[planet_id]
        
        if not results:
            continue
            
        survived = [r['survived'] for r in results]
        trips = list(range(1, len(survived) + 1))
        
        # Calculate metrics
        cumulative_success = np.cumsum(survived)
        cumulative_trips = np.arange(1, len(survived) + 1)
        running_rate = cumulative_success / cumulative_trips
        
        # Top row - Individual results
        ax = axes[0, idx]
        ax.bar(trips, survived, color=['red' if s == 0 else 'green' for s in survived], alpha=0.6)
        ax.set_title(f'{planet_names[planet_id]}')
        ax.set_xlabel('Trip Number')
        ax.set_ylabel('Success (1) / Fail (0)')
        ax.grid(True, alpha=0.3)
        
        # Add success rate text
        success_rate = sum(survived) / len(survived) if survived else 0
        ax.text(0.5, 0.95, f'Success Rate: {success_rate:.1%}', 
                transform=ax.transAxes, ha='center', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Bottom left - Moving average comparison (10-trip window)
    ax = axes[1, 0]
    window = 10
    
    for planet_id in range(3):
        results = all_results[planet_id]
        if results:
            survived = [r['survived'] for r in results]
            
            # Calculate moving average
            moving_avg = []
            for i in range(len(survived)):
                start = max(0, i - window + 1)
                window_data = survived[start:i + 1]
                moving_avg.append(sum(window_data) / len(window_data))
            
            trips = list(range(1, len(survived) + 1))
            ax.plot(trips, moving_avg, colors[planet_id], linewidth=2, 
                   label=f'{planet_names[planet_id]}', marker='o', markersize=3, alpha=0.7)
    
    ax.set_title(f'Moving Average Success Rates ({window}-trip window)')
    ax.set_xlabel('Trip Number')
    ax.set_ylabel('Success Rate')
    ax.set_ylim([0, 1])
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50% baseline')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Bottom middle - Bar comparison
    ax = axes[1, 1]
    success_rates = []
    for planet_id in range(3):
        results = all_results[planet_id]
        if results:
            survived = [r['survived'] for r in results]
            rate = sum(survived) / len(survived) if survived else 0
            success_rates.append(rate)
        else:
            success_rates.append(0)
    
    bars = ax.bar(planet_names, [r*100 for r in success_rates], color=colors, alpha=0.7)
    ax.set_title('Overall Success Rates')
    ax.set_ylabel('Success Rate (%)')
    ax.set_ylim([0, 100])
    
    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1%}', ha='center', va='bottom', fontweight='bold')
    
    # Bottom right - Summary statistics
    ax = axes[1, 2]
    ax.axis('off')
    
    summary_text = "Summary Statistics:\n\n"
    for planet_id in range(3):
        results = all_results[planet_id]
        if results:
            survived = [r['survived'] for r in results]
            rate = sum(survived) / len(survived) if survived else 0
            summary_text += f"{planet_names[planet_id]}:\n"
            summary_text += f"  Trips: {len(survived)}\n"
            summary_text += f"  Success: {sum(survived)}/{len(survived)} = {rate:.1%}\n"
            
            if len(survived) >= 10:
                first_10 = sum(survived[:10]) / 10
                last_10 = sum(survived[-10:]) / min(10, len(survived[-10:]))
                summary_text += f"  First 10: {first_10:.1%}\n"
                summary_text += f"  Last 10: {last_10:.1%}\n"
                
                if last_10 > first_10 + 0.1:
                    trend = "📈 Improving"
                elif last_10 < first_10 - 0.1:
                    trend = "📉 Declining"
                else:
                    trend = "➡️ Stable"
                summary_text += f"  Trend: {trend}\n"
            summary_text += "\n"
    
    ax.text(0.1, 0.5, summary_text, fontsize=11, verticalalignment='center', 
            fontfamily='monospace', transform=ax.transAxes)
    
    plt.tight_layout()
    
    # Save figure
    filename = f"./all_planets/png/all_planets_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    print(f"📊 Visualization saved to: {filename}")
    
    plt.show()

def main():
    print("="*60)
    print("ALL PLANETS BEHAVIOR STUDY")
    print("="*60)
    
    # Get token
    token = "5cc6cdce490fbfb99d2b61775826a8125be47bce"
    
    print("\n📊 How many trips per planet? (default: 30)")
    trips = input("Trips per planet (press Enter for 30): ").strip()
    trips_per_planet = int(trips) if trips else 30
    
    # Study all planets
    result = study_all_planets(token, trips_per_planet)
    
    if result:
        all_results, planet_names = result
        visualize_comparison(all_results, planet_names)
        
        print("\n" + "="*60)
        print("STUDY COMPLETE")
        
        # Print final comparison
        for planet_id in range(3):
            results = all_results[planet_id]
            if results:
                survived = [r['survived'] for r in results]
                rate = sum(survived) / len(survived) if survived else 0
                print(f"{planet_names[planet_id]}: {rate:.1%} success rate")
        print("="*60)

if __name__ == "__main__":
    main()