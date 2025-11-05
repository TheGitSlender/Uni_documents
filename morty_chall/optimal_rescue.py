#!/usr/bin/env python3
"""
Optimal Morty Rescue System - Uses learned planet trends to maximize saves
"""

import requests
import numpy as np
import json
import pickle
import time
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import sys

class OptimalRescuer:
    def __init__(self, token, trends_file='planet_trends.pkl'):
        self.token = token
        self.base_url = "https://challenge.sphinxhq.com"
        self.headers = {"Authorization": f"Bearer {token}"}
        self.planet_names = ["On a Cob", "Cronenberg", "Purge"]
        
        # Load learned trends
        self.load_trends(trends_file)
        
        # Track state for each planet
        self.planet_trips = {0: 0, 1: 0, 2: 0}  # Trips taken to each planet
        self.planet_successes = {0: 0, 1: 0, 2: 0}
        self.planet_failures = {0: 0, 1: 0, 2: 0}
        self.recent_results = {0: [], 1: [], 2: []}  # Recent history
        
        # Hyperparameters (can be tuned)
        self.failure_thresholds = {
            0: 3,  # Failures before switching from Cob
            1: 3,  # Failures before switching from Cronenberg  
            2: 4   # Failures before switching from Purge
        }
        self.lookahead_trips = 20  # How far to look ahead
        self.confidence_threshold = 0.7  # Min predicted rate to send 3 Morties
        self.exploration_bonus = 0.1  # Bonus for underexplored planets
        
    def load_trends(self, filename):
        """Load learned trend patterns"""
        try:
            with open(filename, 'rb') as f:
                self.trends = pickle.load(f)
            print(f"✅ Loaded trends from {filename}")
            
            # Create interpolation functions for each planet
            self.predictors = {}
            for planet_id, trend in self.trends.items():
                x = np.array(trend['predictor_x'])
                y = np.array(trend['predictor_y'])
                self.predictors[planet_id] = interp1d(x, y, 
                                                     kind='cubic',
                                                     fill_value='extrapolate',
                                                     bounds_error=False)
                
        except FileNotFoundError:
            print(f"❌ Trends file {filename} not found!")
            print("Run learn_trends.py first to learn planet patterns")
            sys.exit(1)
    
    def predict_success_rate(self, planet_id, trip_offset=0):
        """Predict success rate for a planet at a future trip"""
        current_trip = self.planet_trips[planet_id]
        future_trip = current_trip + trip_offset
        
        if planet_id not in self.predictors:
            return 0.5  # Default if no trend data
        
        # Get pattern from learned trend
        pattern = self.trends[planet_id]['avg_pattern_smooth']
        cycle_length = self.trends[planet_id].get('cycle_length')
        
        if cycle_length:
            # Use cyclic pattern
            position = future_trip % cycle_length
            if position < len(pattern):
                predicted = pattern[position]
            else:
                predicted = self.predictors[planet_id](position % len(pattern))
        else:
            # Use linear pattern
            if future_trip < len(pattern):
                predicted = pattern[future_trip]
            else:
                # Extrapolate or use last known value
                predicted = pattern[-1]
        
        # Clip to valid range
        return np.clip(predicted, 0, 1)
    
    def calculate_expected_value(self, planet_id, morty_count, lookahead=20):
        """Calculate expected Morties saved in next N trips"""
        expected_saves = 0
        
        for offset in range(lookahead):
            predicted_rate = self.predict_success_rate(planet_id, offset)
            
            # Adjust for uncertainty if planet is underexplored
            total_trips = self.planet_trips[planet_id]
            if total_trips < 10:
                # Add exploration bonus for underexplored planets
                predicted_rate += self.exploration_bonus * (1 - total_trips/10)
            
            expected_saves += predicted_rate * morty_count
        
        return expected_saves / lookahead
    
    def select_best_planet(self, morties_remaining):
        """Select optimal planet based on predicted future performance"""
        scores = {}
        
        for planet_id in range(3):
            # Get current predicted rate
            current_rate = self.predict_success_rate(planet_id, 0)
            
            # Calculate average rate over lookahead window
            future_rates = []
            for offset in range(self.lookahead_trips):
                future_rates.append(self.predict_success_rate(planet_id, offset))
            avg_future_rate = np.mean(future_rates)
            
            # Calculate score combining current and future performance
            score = 0.3 * current_rate + 0.7 * avg_future_rate
            
            # Penalty for recent failures
            recent = self.recent_results[planet_id][-10:]
            if len(recent) >= 3:
                recent_rate = sum(recent) / len(recent)
                # If recent performance is much worse than predicted, penalize
                if recent_rate < current_rate - 0.2:
                    score *= 0.8
            
            # Exploration bonus for underexplored planets
            if self.planet_trips[planet_id] < 5:
                score += self.exploration_bonus
            
            scores[planet_id] = score
        
        # Select best planet
        best_planet = max(scores, key=scores.get)
        
        return best_planet, scores
    
    def determine_group_size(self, planet_id, morties_remaining):
        """Determine optimal group size based on confidence"""
        if morties_remaining <= 0:
            return 0
        
        # Get predicted success rate
        predicted_rate = self.predict_success_rate(planet_id, 0)
        
        # Get recent actual performance
        recent = self.recent_results[planet_id][-10:]
        if len(recent) >= 5:
            recent_rate = sum(recent) / len(recent)
            # Weight recent performance
            combined_rate = 0.4 * predicted_rate + 0.6 * recent_rate
        else:
            combined_rate = predicted_rate
        
        # Determine group size based on confidence
        if combined_rate >= 0.8 and self.planet_trips[planet_id] >= 10:
            return min(3, morties_remaining)
        elif combined_rate >= 0.65 and self.planet_trips[planet_id] >= 5:
            return min(2, morties_remaining)
        else:
            return 1
    
    def should_switch_planet(self, current_planet):
        """Determine if we should switch to a different planet"""
        # Count recent consecutive failures
        recent = self.recent_results[current_planet][-5:]
        if recent:
            consecutive_failures = 0
            for result in reversed(recent):
                if result == 0:
                    consecutive_failures += 1
                else:
                    break
            
            # Check if we hit the failure threshold
            if consecutive_failures >= self.failure_thresholds[current_planet]:
                return True
        
        # Check if another planet is significantly better
        current_score = self.calculate_expected_value(current_planet, 1, self.lookahead_trips)
        for planet_id in range(3):
            if planet_id != current_planet:
                other_score = self.calculate_expected_value(planet_id, 1, self.lookahead_trips)
                if other_score > current_score * 1.5:  # 50% better
                    return True
        
        return False
    
    def run_rescue_mission(self):
        """Execute the optimal rescue mission"""
        print("\n" + "="*60)
        print("🚀 STARTING OPTIMAL RESCUE MISSION")
        print("="*60)
        
        # Start episode
        resp = requests.post(f"{self.base_url}/api/mortys/start/", headers=self.headers)
        if resp.status_code != 200:
            print(f"❌ Failed to start episode: {resp.status_code}")
            return 0
        
        status = resp.json()
        morties_remaining = status["morties_in_citadel"]
        morties_saved = 0
        morties_lost = 0
        total_trips = 0
        
        print(f"📊 Initial Morties: {morties_remaining}")
        print(f"📈 Using learned trends from {sum(t['num_runs'] for t in self.trends.values())} total runs")
        print("-"*60)
        
        current_planet = None
        consecutive_on_planet = 0
        
        while morties_remaining > 0:
            # Select planet and group size
            if current_planet is None or self.should_switch_planet(current_planet):
                new_planet, scores = self.select_best_planet(morties_remaining)
                if new_planet != current_planet:
                    if current_planet is not None:
                        print(f"\n🔄 Switching from {self.planet_names[current_planet]} to {self.planet_names[new_planet]}")
                        print(f"   Scores: {', '.join(f'{self.planet_names[i]}: {s:.2f}' for i, s in scores.items())}")
                    current_planet = new_planet
                    consecutive_on_planet = 0
            
            group_size = self.determine_group_size(current_planet, morties_remaining)
            
            # Send Morties
            try:
                resp = requests.post(
                    f"{self.base_url}/api/mortys/portal/",
                    headers=self.headers,
                    json={"planet": current_planet, "morty_count": group_size},
                    timeout=10
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    survived = data.get("survived", False)
                    
                    # Update statistics
                    self.planet_trips[current_planet] += 1
                    consecutive_on_planet += 1
                    
                    if survived:
                        self.planet_successes[current_planet] += 1
                        self.recent_results[current_planet].append(1)
                    else:
                        self.planet_failures[current_planet] += 1
                        self.recent_results[current_planet].append(0)
                    
                    # Keep recent history limited
                    if len(self.recent_results[current_planet]) > 20:
                        self.recent_results[current_planet].pop(0)
                    
                    # Update counts
                    morties_remaining = data.get("morties_in_citadel", 0)
                    morties_saved = data.get("morties_on_planet_jessica", 0)
                    morties_lost = data.get("morties_lost", 0)
                    total_trips += 1
                    
                    # Progress update
                    if total_trips % 25 == 0:
                        self.print_progress(total_trips, morties_saved, morties_lost, morties_remaining)
                    
                elif resp.status_code == 500:
                    print(f"\n⚠️ Server error at trip {total_trips}")
                    break
                else:
                    print(f"\n❌ Error {resp.status_code}")
                    break
                
                # Small delay
                if total_trips % 10 == 0:
                    time.sleep(0.05)
                    
            except Exception as e:
                print(f"\n❌ Exception: {e}")
                break
        
        # Final results
        self.print_final_results(morties_saved, morties_lost, total_trips)
        
        return morties_saved
    
    def print_progress(self, trips, saved, lost, remaining):
        """Print progress update"""
        print(f"\n📍 Trip {trips}:")
        print(f"  ✅ Saved: {saved} ({saved/10:.1%})")
        print(f"  ❌ Lost: {lost}")
        print(f"  📦 Remaining: {remaining}")
        
        # Planet statistics
        for planet_id in range(3):
            total = self.planet_successes[planet_id] + self.planet_failures[planet_id]
            if total > 0:
                rate = self.planet_successes[planet_id] / total
                predicted = self.predict_success_rate(planet_id, 0)
                print(f"  {self.planet_names[planet_id]}: {rate:.1%} actual, {predicted:.1%} predicted ({total} trips)")
    
    def print_final_results(self, saved, lost, trips):
        """Print final mission results"""
        print("\n" + "="*60)
        print("🏁 MISSION COMPLETE!")
        print("="*60)
        
        success_rate = saved / 1000
        print(f"\n🎯 FINAL SCORE: {saved} Morties saved ({success_rate:.1%})")
        print(f"❌ Morties lost: {lost}")
        print(f"📊 Total trips: {trips}")
        
        print("\n🪐 PLANET USAGE:")
        for planet_id in range(3):
            total = self.planet_trips[planet_id]
            if total > 0:
                success = self.planet_successes[planet_id]
                rate = success / total
                print(f"  {self.planet_names[planet_id]}:")
                print(f"    Trips: {total}")
                print(f"    Success rate: {rate:.1%}")
                print(f"    Contribution: {success*3}/{saved} = {success*3/saved:.1%} of saves")
        
        # Performance rating
        print("\n🏆 PERFORMANCE RATING:")
        if success_rate >= 0.95:
            print("  ⭐⭐⭐⭐⭐ LEGENDARY! (95%+)")
        elif success_rate >= 0.90:
            print("  ⭐⭐⭐⭐ EXCELLENT! (90-95%)")
        elif success_rate >= 0.85:
            print("  ⭐⭐⭐ GREAT! (85-90%)")
        elif success_rate >= 0.80:
            print("  ⭐⭐ GOOD! (80-85%)")
        else:
            print("  ⭐ KEEP OPTIMIZING!")
    
    def set_hyperparameters(self, failure_thresholds=None, lookahead=None, confidence=None):
        """Adjust hyperparameters for optimization"""
        if failure_thresholds:
            self.failure_thresholds.update(failure_thresholds)
        if lookahead:
            self.lookahead_trips = lookahead
        if confidence:
            self.confidence_threshold = confidence
        
        print(f"\n⚙️ Hyperparameters updated:")
        print(f"  Failure thresholds: {self.failure_thresholds}")
        print(f"  Lookahead: {self.lookahead_trips} trips")
        print(f"  Confidence threshold: {self.confidence_threshold}")

def main():
    print("="*60)
    print("OPTIMAL MORTY RESCUE SYSTEM")
    print("="*60)
    
    # Get token
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("\n🔑 Enter your API token:")
        token = input("> ").strip()
    
    if not token:
        print("❌ Token required!")
        return
    
    # Check for trends file
    print("\n📊 Enter trends file (default: planet_trends.pkl):")
    trends_file = input("> ").strip() or 'planet_trends.pkl'
    
    # Initialize rescuer
    rescuer = OptimalRescuer(token, trends_file)
    
    # Optional: Adjust hyperparameters
    print("\n⚙️ Adjust hyperparameters? (y/n, default: n)")
    if input("> ").strip().lower() == 'y':
        print("\nFailure thresholds (comma-separated for planets 0,1,2):")
        print("Current:", rescuer.failure_thresholds)
        thresholds = input("> ").strip()
        if thresholds:
            vals = [int(x) for x in thresholds.split(',')]
            rescuer.set_hyperparameters(
                failure_thresholds={i: vals[i] for i in range(min(3, len(vals)))}
            )
        
        print("\nLookahead trips (default: 20):")
        lookahead = input("> ").strip()
        if lookahead:
            rescuer.set_hyperparameters(lookahead=int(lookahead))
    
    # Run the mission
    saved = rescuer.run_rescue_mission()
    
    print(f"\n🎉 Mission complete! Final score: {saved} Morties saved!")

if __name__ == "__main__":
    main()