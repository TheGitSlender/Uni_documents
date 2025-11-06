#!/usr/bin/env python3
"""
Hybrid Thompson Sampling Solver
Uses trend data as priors, updates with reality, forces diversity
"""

import requests
import json
import numpy as np


# ============================================================================
# PARAMETERS
# ============================================================================
API_TOKEN = "5cc6cdce490fbfb99d2b61775826a8125be47bce"
BASE_URL = "https://challenge.sphinxhq.com"

# Decision thresholds
CONFIDENCE_THRESHOLD = 0.65  # Send 3 if sampled >= this
MEDIUM_THRESHOLD = 0.50      # Send 2 if sampled >= this

# Diversity enforcement - CRITICAL to not get stuck!
MAX_CONSECUTIVE_SAME_PLANET = 15  # Force switch after this many trips
FORCE_EXPLORE_EVERY = 30  # Try other planets every N trips

# Planet-specific strategies
PLANET_STRATEGIES = {
    0: {  # On a Cob - use sparingly, it's baseline ~50%
        'max_consecutive': 10,
        'min_expected': 0.55,  # Only use if above 55%
        'priority': 0.8  # Lower priority multiplier
    },
    1: {  # Cronenberg - volatile, use at peaks
        'max_consecutive': 12,
        'min_expected': 0.60,  # Only use if above 60%
        'priority': 1.0
    },
    2: {  # Purge - HIGH PRIORITY, best rewards
        'max_consecutive': 25,
        'min_expected': 0.45,  # More tolerant
        'priority': 1.2  # BOOST priority
    }
}

# Prior strength (how much to trust trends initially)
PRIOR_STRENGTH = 5  # Pseudo-observations per position

# Trend files
TREND_FILES = {
    0: "output_graph_data/planet_0_trend.json",
    1: "output_graph_data/planet_1_trend.json",
    2: "output_graph_data/planet_2_trend.json"
}


# ============================================================================
# SOLVER
# ============================================================================
class HybridSolver:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {API_TOKEN}"}
        
        # Bayesian beliefs: Beta(α, β) per position per planet
        self.alpha = {0: [], 1: [], 2: []}  # Successes
        self.beta = {0: [], 1: [], 2: []}   # Failures
        
        # Positions and stats
        self.positions = {0: 0, 1: 0, 2: 0}
        self.total_sent = 0
        self.total_survived = 0
        self.trips = {0: 0, 1: 0, 2: 0}
        
        # Diversity tracking
        self.consecutive_planet = None
        self.consecutive_count = 0
        self.last_forced_explore = 0
        
        # Load trends and initialize priors
        self._load_trends()
    
    def _load_trends(self):
        """Load trends and convert to Beta priors."""
        print("Loading trends and initializing Bayesian priors...\n")
        
        for pid, filepath in TREND_FILES.items():
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            trend = data['trend']
            
            # Convert each probability to Beta(α, β)
            # Higher prob → higher α, lower β
            for prob in trend:
                α = prob * PRIOR_STRENGTH + 1  # +1 to avoid zero
                β = (1 - prob) * PRIOR_STRENGTH + 1
                self.alpha[pid].append(α)
                self.beta[pid].append(β)
            
            print(f"Planet {pid}: {len(trend)} positions, "
                  f"mean={data['mean_success_rate']:.2f}, "
                  f"cycle={data['cycle_length']}")
    
    def sample_expected(self, planet_id):
        """Thompson Sampling: sample from Beta posterior."""
        pos = self.positions[planet_id] % len(self.alpha[planet_id])
        α = self.alpha[planet_id][pos]
        β = self.beta[planet_id][pos]
        
        # Sample from Beta(α, β)
        sample = np.random.beta(α, β)
        
        # Apply planet-specific priority boost
        priority = PLANET_STRATEGIES[planet_id]['priority']
        return sample * priority
    
    def get_mean_expected(self, planet_id):
        """Get mean (non-sampled) expected value."""
        pos = self.positions[planet_id] % len(self.alpha[planet_id])
        α = self.alpha[planet_id][pos]
        β = self.beta[planet_id][pos]
        return α / (α + β)
    
    def update_belief(self, planet_id, survived, count):
        """Update Bayesian belief with observation."""
        pos = self.positions[planet_id] % len(self.alpha[planet_id])
        
        if survived:
            self.alpha[planet_id][pos] += count
        else:
            self.beta[planet_id][pos] += count
    
    def should_force_diversity(self, current_choice):
        """Check if we should force switching for diversity."""
        # Force explore periodically
        if self.total_sent - self.last_forced_explore >= FORCE_EXPLORE_EVERY:
            return True
        
        # Too many consecutive on same planet
        if self.consecutive_planet == current_choice:
            max_allowed = PLANET_STRATEGIES[current_choice]['max_consecutive']
            if self.consecutive_count >= max_allowed:
                return True
        
        return False
    
    def select_planet(self):
        """
        Select planet using Thompson Sampling + diversity enforcement.
        This is the KEY: we don't just pick max, we force diversity!
        """
        # Sample all planets
        samples = []
        for pid in range(3):
            sample = self.sample_expected(pid)
            mean = self.get_mean_expected(pid)
            min_exp = PLANET_STRATEGIES[pid]['min_expected']
            
            # Filter out planets below minimum threshold
            if mean >= min_exp:
                samples.append((pid, sample))
        
        # If no planet meets minimum, relax and pick best
        if not samples:
            samples = [(pid, self.sample_expected(pid)) for pid in range(3)]
        
        # Sort by sampled value
        samples.sort(key=lambda x: x[1], reverse=True)
        best_planet = samples[0][0]
        
        # Check diversity enforcement
        if self.should_force_diversity(best_planet):
            print(f"  [DIVERSITY] Forcing switch from planet {self.consecutive_planet}")
            
            # Pick best planet that's NOT the current one
            for pid, sample in samples:
                if pid != self.consecutive_planet:
                    best_planet = pid
                    break
            
            self.last_forced_explore = self.total_sent
        
        # Update consecutive counter
        if best_planet == self.consecutive_planet:
            self.consecutive_count += 1
        else:
            self.consecutive_planet = best_planet
            self.consecutive_count = 1
        
        return best_planet
    
    def send(self, planet_id, count):
        """Send Morties, update beliefs, print status."""
        resp = requests.post(
            f"{BASE_URL}/api/mortys/portal/",
            headers=self.headers,
            json={"planet": planet_id, "morty_count": count}
        )
        
        data = resp.json()
        survived = data.get('survived', False)
        
        # Update beliefs with observation
        self.update_belief(planet_id, survived, count)
        
        # Update stats
        self.positions[planet_id] += 1
        self.trips[planet_id] += 1
        self.total_sent += count
        if survived:
            self.total_survived += count
        
        # Print
        rate = self.total_survived / self.total_sent
        mean_exp = self.get_mean_expected(planet_id)
        
        print(f"Trip {self.total_sent:4d} | P{planet_id} | "
              f"Sent:{count} | {'WIN' if survived else 'LOSS'} | "
              f"Exp:{mean_exp:.3f} | "
              f"Rate:{rate:.3f} ({self.total_survived}/{self.total_sent})")
        
        return survived
    
    def run(self):
        """Main execution - Thompson Sampling with diversity."""
        # Start episode
        requests.post(f"{BASE_URL}/api/mortys/start/", headers=self.headers)
        print("\n=== EPISODE START ===")
        print("Strategy: Thompson Sampling + Forced Diversity\n")
        
        trip_num = 0
        
        while self.total_sent < 1000:
            trip_num += 1
            
            # Select planet using Thompson Sampling
            planet_id = self.select_planet()
            mean_exp = self.get_mean_expected(planet_id)
            
            # Determine how many to send based on expected value
            if mean_exp >= CONFIDENCE_THRESHOLD:
                count = 3
            elif mean_exp >= MEDIUM_THRESHOLD:
                count = 2
            else:
                count = 1
            
            count = min(count, 1000 - self.total_sent)
            
            # Print decision reasoning every 20 trips
            if trip_num % 20 == 1:
                print(f"\n--- Trip {trip_num} Decision ---")
                for pid in range(3):
                    exp = self.get_mean_expected(pid)
                    print(f"  P{pid}: exp={exp:.3f}, trips={self.trips[pid]}")
                print(f"  → Selected P{planet_id} (send {count})")
            
            # Send
            self.send(planet_id, count)
        
        # Final results
        rate = self.total_survived / self.total_sent
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        print(f"Success Rate: {rate:.3f} ({self.total_survived}/{self.total_sent})")
        print(f"\nPlanet Usage:")
        for pid in range(3):
            pct = self.trips[pid] / sum(self.trips.values()) * 100
            print(f"  Planet {pid}: {self.trips[pid]:3d} trips ({pct:.1f}%)")
        
        # Grade diversity
        max_trips = max(self.trips.values())
        min_trips = min(self.trips.values())
        
        if max_trips > 250:
            print(f"\n⚠️  Imbalanced: One planet used too much ({max_trips} trips)")
        elif min_trips < 50:
            print(f"\n⚠️  Underused: One planet barely used ({min_trips} trips)")
        else:
            print(f"\n✓ Good diversity!")
        
        # Save
        results = {
            'success_rate': rate,
            'total_sent': self.total_sent,
            'total_survived': self.total_survived,
            'trips': self.trips,
            'final_beliefs': {
                pid: {
                    'alpha': [float(a) for a in self.alpha[pid]],
                    'beta': [float(b) for b in self.beta[pid]]
                }
                for pid in range(3)
            }
        }
        
        with open('hybrid_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\nSaved to hybrid_results.json")


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("="*60)
    print("HYBRID THOMPSON SAMPLING SOLVER")
    print("="*60)
    print("\nFeatures:")
    print("  • Bayesian learning (trends as priors)")
    print("  • Thompson Sampling (natural exploration)")
    print("  • Forced diversity (no getting stuck!)")
    print("  • Planet-specific strategies")
    print("="*60)
    
    solver = HybridSolver()
    solver.run()