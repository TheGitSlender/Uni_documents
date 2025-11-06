#!/usr/bin/env python3
"""
Morty Express - All-in-One Production Solver
Complete solution with embedded trend analysis and strategy

Based on analyzed patterns:
- Planet 0 (On a Cob): 7-position cycle, 15-85% oscillation
- Planet 1 (Cronenberg): 12-position cycle, 10-90% volatility  
- Planet 2 (Purge): 200-position cycle, 0-100% waves

Author: Claude & User
Date: November 2025
"""

import requests
import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, Tuple, List


class MortyExpressSolver:
    """
    All-in-one solver for the Morty Express Challenge.
    
    Strategy:
    1. Exploration Phase (39 Morties): Probe to localize position in each cycle
    2. Exploitation Phase (961 Morties): Greedily select best planet each step
    """
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://challenge.sphinxhq.com"
        self.headers = {"Authorization": f"Bearer {token}"}
        self.planet_names = ["On a Cob", "Cronenberg", "Purge"]
        
        # Load embedded trend data
        self._load_embedded_trends()
        
        # Cycle tracking
        self.planet_positions = {0: 0, 1: 0, 2: 0}
        self.planet_trip_counts = {0: 0, 1: 0, 2: 0}
        
        # Strategy parameters (tunable)
        self.CONFIDENCE_THRESHOLD = 0.60  # Send 3 Morties
        self.VALLEY_THRESHOLD = 0.35      # Send 1 Morty
        self.EXPLORATION_BUDGET = {0: 7, 1: 12, 2: 30}  # Increased Purge budget
        
        # Stats
        self.total_sent = 0
        self.total_survived = 0
        self.history = []
    
    def _load_embedded_trends(self):
        """Load embedded trend patterns based on collected data."""
        
        # Planet 0: On a Cob (7-position cycle)
        # Pattern: Low at 0,6, High at 3,4
        planet_0_base_cycle = np.array([
            0.15, 0.35, 0.60, 0.80, 0.75, 0.40, 0.20
        ])
        # Extend to cover 333 positions (47+ cycles)
        planet_0_trend = np.tile(planet_0_base_cycle, 48)[:333]
        
        # Planet 1: Cronenberg (12-position cycle)
        # Pattern: Highly volatile oscillations
        planet_1_base_cycle = np.array([
            0.40, 0.35, 0.45, 0.20, 0.15, 0.25, 
            0.40, 0.50, 0.70, 0.85, 0.80, 0.65
        ])
        # Extend to cover 333 positions (27+ cycles)
        planet_1_trend = np.tile(planet_1_base_cycle, 28)[:333]
        
        # Planet 2: Purge (200-position cycle)
        # Pattern: Long waves from 0% to 100%
        # Create smooth sine wave pattern
        x = np.arange(200)
        # Sine wave: starts at 0, peaks at 100 (position 50), valleys at 0, 200
        planet_2_base_cycle = 0.5 + 0.5 * np.sin(2 * np.pi * x / 200 - np.pi/2)
        # Extend to cover 1000 positions (5 cycles)
        planet_2_trend = np.tile(planet_2_base_cycle, 5)
        
        self.trends = {
            0: {
                'trend': planet_0_trend,
                'cycle_length': 7,
                'length': len(planet_0_trend),
                'planet_name': 'On a Cob',
                'mean': np.mean(planet_0_trend)
            },
            1: {
                'trend': planet_1_trend,
                'cycle_length': 12,
                'length': len(planet_1_trend),
                'planet_name': 'Cronenberg',
                'mean': np.mean(planet_1_trend)
            },
            2: {
                'trend': planet_2_trend,
                'cycle_length': 200,
                'length': len(planet_2_trend),
                'planet_name': 'Purge',
                'mean': np.mean(planet_2_trend)
            }
        }
        
        print("\n📊 Embedded Trend Patterns Loaded:")
        print("="*60)
        for pid in range(3):
            t = self.trends[pid]
            print(f"{t['planet_name']}:")
            print(f"  Cycle: {t['cycle_length']} positions")
            print(f"  Mean: {t['mean']:.1%}")
            print(f"  Range: {np.min(t['trend']):.1%} - {np.max(t['trend']):.1%}")
    
    def load_trends_from_files(self, planet_0_file: str = None, 
                               planet_1_file: str = None,
                               planet_2_file: str = None):
        """
        Load trends from JSON files (optional - overrides embedded trends).
        """
        print("\n📁 Loading External Trend Files...")
        
        for planet_id, filepath in [(0, planet_0_file), (1, planet_1_file), (2, planet_2_file)]:
            if filepath:
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    trend = np.array(data['trend'])
                    self.trends[planet_id]['trend'] = trend
                    self.trends[planet_id]['cycle_length'] = data.get('cycle_length')
                    self.trends[planet_id]['length'] = len(trend)
                    
                    print(f"✅ Loaded {self.planet_names[planet_id]} from file")
                except Exception as e:
                    print(f"⚠️ Could not load {filepath}: {e}")
                    print(f"   Using embedded trend for {self.planet_names[planet_id]}")
    
    def get_expected_probability(self, planet_id: int, position: int = None) -> float:
        """Get expected success probability at position in planet's cycle."""
        if position is None:
            position = self.planet_positions[planet_id]
        
        trend = self.trends[planet_id]['trend']
        pos_in_trend = position % len(trend)
        
        return float(trend[pos_in_trend])
    
    def start_episode(self):
        """Start a new episode."""
        resp = requests.post(f"{self.base_url}/api/mortys/start/", headers=self.headers)
        if resp.status_code != 200:
            raise Exception(f"Failed to start episode: {resp.status_code}")
        
        data = resp.json()
        print(f"\n🚀 Episode Started: {data['morties_in_citadel']} Morties ready")
        
        # Reset tracking
        self.planet_positions = {0: 0, 1: 0, 2: 0}
        self.planet_trip_counts = {0: 0, 1: 0, 2: 0}
        self.total_sent = 0
        self.total_survived = 0
        self.history = []
        
        return data
    
    def send_morties(self, planet_id: int, morty_count: int) -> Dict:
        """Send Morties through a portal."""
        resp = requests.post(
            f"{self.base_url}/api/mortys/portal/",
            headers=self.headers,
            json={"planet": planet_id, "morty_count": morty_count}
        )
        
        if resp.status_code != 200:
            raise Exception(f"Portal call failed: {resp.status_code}")
        
        data = resp.json()
        survived = data.get('survived', False)
        
        # Update tracking
        self.planet_trip_counts[planet_id] += 1
        self.planet_positions[planet_id] += 1
        self.total_sent += morty_count
        if survived:
            self.total_survived += morty_count
        
        # Record history
        self.history.append({
            'planet': planet_id,
            'planet_name': self.planet_names[planet_id],
            'morty_count': morty_count,
            'survived': survived,
            'position': self.planet_positions[planet_id] - 1,
            'expected_prob': self.get_expected_probability(planet_id, self.planet_positions[planet_id] - 1)
        })
        
        return data
    
    def probe_planet(self, planet_id: int, num_probes: int) -> List[bool]:
        """Send probe Morties to determine position in cycle."""
        print(f"\n🔍 Probing {self.planet_names[planet_id]} ({num_probes} Morties)...")
        
        results = []
        for i in range(num_probes):
            data = self.send_morties(planet_id, 1)
            results.append(data.get('survived', False))
            time.sleep(0.05)  # Small delay
        
        success_rate = sum(results) / len(results)
        print(f"   Results: {sum(results)}/{len(results)} survived ({success_rate:.1%})")
        
        return results
    
    def localize_position(self, planet_id: int, probe_results: List[bool]) -> int:
        """Estimate current position in planet's cycle using probe results."""
        trend = self.trends[planet_id]['trend']
        cycle_length = self.trends[planet_id]['cycle_length']
        
        # Convert to pattern
        probe_pattern = np.array([1.0 if r else 0.0 for r in probe_results])
        
        # Try all possible starting positions
        best_correlation = -1
        best_position = 0
        
        search_range = min(cycle_length, len(trend))
        
        for start_pos in range(search_range):
            # Extract expected pattern
            expected = []
            for i in range(len(probe_results)):
                pos = (start_pos + i) % len(trend)
                expected.append(trend[pos])
            expected = np.array(expected)
            
            # Calculate correlation
            if len(expected) > 1 and np.std(expected) > 0:
                correlation = np.corrcoef(probe_pattern, expected)[0, 1]
                if not np.isnan(correlation) and correlation > best_correlation:
                    best_correlation = correlation
                    best_position = start_pos
        
        print(f"   Estimated position: {best_position} (correlation: {best_correlation:.3f})")
        
        # Set position accounting for probes already sent
        actual_position = (best_position + len(probe_results)) % len(trend)
        self.planet_positions[planet_id] = actual_position
        
        return best_position
    
    def exploration_phase(self):
        """Probe planets to localize positions."""
        print("\n" + "="*60)
        print("EXPLORATION PHASE")
        print("="*60)
        
        for planet_id in range(3):
            budget = self.EXPLORATION_BUDGET[planet_id]
            probe_results = self.probe_planet(planet_id, budget)
            self.localize_position(planet_id, probe_results)
        
        print(f"\n✅ Exploration complete: {self.total_sent} Morties used")
        print(f"   Success rate: {self.total_survived/self.total_sent:.1%}")
    
    def select_best_planet(self) -> Tuple[int, int]:
        """Select best planet and Morty count for next trip."""
        best_planet = 0
        best_score = 0
        best_count = 1
        
        for planet_id in range(3):
            prob = self.get_expected_probability(planet_id)
            
            # Determine Morty count
            if prob >= self.CONFIDENCE_THRESHOLD:
                morty_count = 3
            elif prob >= self.VALLEY_THRESHOLD:
                morty_count = 2
            else:
                morty_count = 1
            
            # Expected value
            score = prob * morty_count
            
            if score > best_score:
                best_planet = planet_id
                best_score = score
                best_count = morty_count
        
        return best_planet, best_count
    
    def exploitation_phase(self, max_morties: int = 1000):
        """Main exploitation - greedily select best planet."""
        print("\n" + "="*60)
        print("EXPLOITATION PHASE")
        print("="*60)
        
        remaining = max_morties - self.total_sent
        print(f"\nRemaining Morties: {remaining}\n")
        
        step = 0
        last_print = 0
        
        while remaining > 0:
            # Select best
            planet_id, morty_count = self.select_best_planet()
            morty_count = min(morty_count, remaining)
            
            expected_prob = self.get_expected_probability(planet_id)
            
            # Send
            try:
                data = self.send_morties(planet_id, morty_count)
                survived = data.get('survived', False)
                remaining -= morty_count
                step += 1
                
                # Print progress
                if step - last_print >= 10 or remaining <= 0:
                    current_rate = self.total_survived / self.total_sent
                    print(f"Step {step:3d} | {self.planet_names[planet_id]:12s} | "
                          f"Sent: {morty_count} | {'✓' if survived else '✗'} | "
                          f"Exp: {expected_prob:.1%} | "
                          f"Rate: {current_rate:.1%} ({self.total_survived}/{self.total_sent}) | "
                          f"Left: {remaining}")
                    last_print = step
                
                if data.get('morties_in_citadel', 0) == 0:
                    break
                
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        print(f"\n{'='*60}")
    
    def run_episode(self) -> Dict:
        """Run complete episode."""
        self.start_episode()
        self.exploration_phase()
        self.exploitation_phase()
        
        # Results
        final_rate = self.total_survived / self.total_sent if self.total_sent > 0 else 0
        
        results = {
            'total_sent': self.total_sent,
            'total_survived': self.total_survived,
            'success_rate': final_rate,
            'planet_trip_counts': self.planet_trip_counts.copy(),
            'history': self.history,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"{'='*60}")
        print(f"Total Morties: {self.total_sent}")
        print(f"Survived: {self.total_survived}")
        print(f"Success Rate: {final_rate:.1%}")
        print(f"\nTrips per planet:")
        for pid in range(3):
            print(f"  {self.planet_names[pid]:12s}: {self.planet_trip_counts[pid]:3d} trips")
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"morty_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📁 Results saved to: {filename}")
        
        return results
    
    def print_strategy_summary(self):
        """Print strategy information."""
        print("\n" + "="*60)
        print("STRATEGY SUMMARY")
        print("="*60)
        print(f"\n🎯 Embedded Patterns:")
        for pid in range(3):
            t = self.trends[pid]
            print(f"\n{t['planet_name']} (Cycle: {t['cycle_length']})")
            print(f"  Mean: {t['mean']:.1%}")
            print(f"  Range: {np.min(t['trend']):.1%} to {np.max(t['trend']):.1%}")
            
            # Count zones
            high = np.sum(t['trend'] >= self.CONFIDENCE_THRESHOLD)
            low = np.sum(t['trend'] < self.VALLEY_THRESHOLD)
            mid = len(t['trend']) - high - low
            print(f"  High zones (≥{self.CONFIDENCE_THRESHOLD:.0%}): {high} positions")
            print(f"  Medium zones: {mid} positions")
            print(f"  Low zones (<{self.VALLEY_THRESHOLD:.0%}): {low} positions")
        
        print(f"\n⚙️  Parameters:")
        print(f"  Confidence threshold: {self.CONFIDENCE_THRESHOLD:.0%} → Send 3 Morties")
        print(f"  Valley threshold: {self.VALLEY_THRESHOLD:.0%} → Send 1 Morty")
        print(f"  Exploration budget: {self.EXPLORATION_BUDGET}")
        
        print(f"\n💡 Strategy:")
        print(f"  1. Probe {sum(self.EXPLORATION_BUDGET.values())} Morties to localize")
        print(f"  2. Greedily exploit for remaining {1000 - sum(self.EXPLORATION_BUDGET.values())} Morties")
        print(f"  3. Adapt Morty count based on expected probability")


def main():
    print("="*60)
    print("MORTY EXPRESS - ALL-IN-ONE SOLVER")
    print("="*60)
    print("\nBased on analyzed trends:")
    print("  • Planet 0 (On a Cob): 7-cycle, predictable")
    print("  • Planet 1 (Cronenberg): 12-cycle, volatile")
    print("  • Planet 2 (Purge): 200-cycle, high payoff")
    
    # Get token
    token = "5cc6cdce490fbfb99d2b61775826a8125be47bce"
    
    # Create solver
    solver = MortyExpressSolver(token)
    
    # Optional: load external trend files
    print("\n📂 Load external trend files? (y/n, default: n)")
    load_external = input("> ").strip().lower() == 'y'
    
    if load_external:
        p0 = input("Planet 0 JSON (or Enter to skip): ").strip() or None
        p1 = input("Planet 1 JSON (or Enter to skip): ").strip() or None
        p2 = input("Planet 2 JSON (or Enter to skip): ").strip() or None
        solver.load_trends_from_files(p0, p1, p2)
    
    # Optional: tune parameters
    print("\n⚙️  Tune parameters? (y/n, default: n)")
    if input("> ").strip().lower() == 'y':
        conf = input(f"Confidence threshold (default: {solver.CONFIDENCE_THRESHOLD}): ").strip()
        if conf:
            solver.CONFIDENCE_THRESHOLD = float(conf)
        
        valley = input(f"Valley threshold (default: {solver.VALLEY_THRESHOLD}): ").strip()
        if valley:
            solver.VALLEY_THRESHOLD = float(valley)
    
    # Show strategy
    solver.print_strategy_summary()
    
    # Run episode
    print("\n\n🚀 Ready to run! Press Enter to start...")
    input()
    
    try:
        results = solver.run_episode()
        
        print("\n" + "="*60)
        print("✅ EPISODE COMPLETE!")
        print("="*60)
        
        if results['success_rate'] >= 0.75:
            print("🏆 Excellent run! This is competition-worthy!")
        elif results['success_rate'] >= 0.70:
            print("👍 Good run! Keep trying for 75%+")
        else:
            print("💪 Try again! Aim for 70%+")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()