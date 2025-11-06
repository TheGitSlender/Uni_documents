#!/usr/bin/env python3
"""
Trend Learning Script - Modified for Purge Planet
Sends 1 Morty per trip for better granularity on long-cycle planets
"""

import requests
import numpy as np
import json
import time
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
import pickle

class TrendLearner:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://challenge.sphinxhq.com"
        self.headers = {"Authorization": f"Bearer {token}"}
        self.planet_names = ["On a Cob", "Cronenberg", "Purge"]
    
    def load_previous_runs(self, directory_pattern=None):
        """Load previously saved runs from JSON files"""
        import os
        import glob
        
        if directory_pattern:
            # Use specific pattern
            directories = glob.glob(directory_pattern)
        else:
            # Find all planet run directories
            directories = glob.glob("planet_*_runs_*/")
        
        loaded_data = {0: [], 1: [], 2: []}
        
        for directory in directories:
            # Extract planet_id from directory name
            parts = directory.split('_')
            if len(parts) >= 2 and parts[0] == 'planet':
                try:
                    planet_id = int(parts[1])
                except ValueError:
                    continue
                
                # Load all JSON files in this directory
                json_files = glob.glob(os.path.join(directory, "run_*.json"))
                
                for json_file in json_files:
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if 'results' in data:
                                loaded_data[planet_id].append(data['results'])
                                print(f"  Loaded: {json_file}")
                    except Exception as e:
                        print(f"  Error loading {json_file}: {e}")
        
        # Summary
        for planet_id in range(3):
            if loaded_data[planet_id]:
                print(f"\n{self.planet_names[planet_id]}: Loaded {len(loaded_data[planet_id])} previous runs")
        
        return loaded_data
        
    def study_single_planet(self, planet_id, trips=333, morty_count=1, verbose=True):
        """
        Study a single planet for one complete episode
        
        Args:
            planet_id: 0, 1, or 2
            trips: Number of trips to make
            morty_count: Number of Morties to send per trip (1 for fine-grained data, 3 for speed)
            verbose: Print progress
        """
        if verbose:
            print(f"\n{'='*50}")
            print(f"Studying {self.planet_names[planet_id]} - {trips} trips")
            print(f"Sending {morty_count} Morty/Morties per trip")
        
        # Start new episode
        resp = requests.post(f"{self.base_url}/api/mortys/start/", headers=self.headers)
        if resp.status_code != 200:
            print(f"Failed to start episode: {resp.status_code}")
            return None
            
        results = []
        trip_count = 0
        
        # Send Morties to map the pattern
        for i in range(trips):
            try:
                resp = requests.post(
                    f"{self.base_url}/api/mortys/portal/",
                    headers=self.headers,
                    json={"planet": planet_id, "morty_count": morty_count},
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    survived = 1 if data.get("survived", False) else 0
                    
                    # Record result for each Morty sent
                    for _ in range(morty_count):
                        results.append(survived)
                    
                    trip_count += 1
                    
                    if verbose and trip_count % 50 == 0:
                        recent_rate = sum(results[-10:]) / min(10, len(results[-10:]))
                        print(f"  Trip {trip_count}: Recent rate = {recent_rate:.1%}")
                        
                elif resp.status_code == 500:
                    if verbose:
                        print(f"  Server error at trip {trip_count}")
                    break
                else:
                    if verbose:
                        print(f"  Error {resp.status_code} at trip {trip_count}")
                    break
                     
                
            except Exception as e:
                if verbose:
                    print(f"  Exception at trip {trip_count}: {e}")
                break
        
        return results
    
    def learn_planet_trends(self, planet_id, num_runs=10, morty_count=1):
        """
        Learn the trend pattern for a specific planet over multiple runs
        
        Args:
            planet_id: 0, 1, or 2
            num_runs: Number of episodes to run
            morty_count: Morties per trip (1 for Purge, 3 for others)
        """
        print(f"\n{'='*60}")
        print(f"LEARNING TREND FOR {self.planet_names[planet_id].upper()}")
        print(f"Running {num_runs} episodes with {morty_count} Morty/Morties per trip...")
        print(f"{'='*60}")
        
        # Create directory for saving runs
        import os
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_dir = f"planet_{planet_id}_{self.planet_names[planet_id].replace(' ', '_')}_runs_{timestamp}"
        os.makedirs(save_dir, exist_ok=True)
        print(f"📁 Saving runs to directory: {save_dir}/")
        
        all_runs = []
        
        # Calculate trips needed based on Morty count
        # For 1000 Morties total:
        # - morty_count=1: need 1000 trips
        # - morty_count=3: need 333 trips
        trips_per_run = 1000 // morty_count if morty_count > 0 else 333
        
        for run in range(num_runs):
            print(f"\nRun {run + 1}/{num_runs}:")
            results = self.study_single_planet(planet_id, trips=trips_per_run, morty_count=morty_count, verbose=True)
            
            if results and len(results) > 50:  # Minimum viable data
                all_runs.append(results)
                success_rate = sum(results) / len(results)
                print(f"  Overall success rate: {success_rate:.1%}")
                
                # Save this run immediately
                run_data = {
                    'planet_id': planet_id,
                    'planet_name': self.planet_names[planet_id],
                    'run_number': run + 1,
                    'timestamp': datetime.now().isoformat(),
                    'results': results,
                    'success_rate': success_rate,
                    'total_trips': len(results),
                    'morty_count_per_trip': morty_count
                }
                
                # Save as JSON
                run_filename = f"{save_dir}/run_{run + 1:03d}.json"
                with open(run_filename, 'w') as f:
                    json.dump(run_data, f, indent=2)
                print(f"  ✅ Run saved to: {run_filename}")
                
            else:
                print(f"  Run failed or insufficient data")
            
            # Small delay between runs
        
        if not all_runs:
            print("No successful runs!")
            return None
        
        # Analyze the patterns
        trend_data = self.analyze_trends(all_runs, planet_id)
        
        return trend_data
    
    def analyze_trends(self, all_runs, planet_id):
        """Analyze runs to extract the cyclic pattern"""
        print(f"\n{'='*50}")
        print(f"ANALYZING PATTERNS FOR {self.planet_names[planet_id]}")
        
        # Calculate moving averages for each run
        window = 10
        moving_averages = []
        
        for run in all_runs:
            ma = []
            for i in range(len(run)):
                start = max(0, i - window + 1)
                window_data = run[start:i + 1]
                ma.append(sum(window_data) / len(window_data))
            moving_averages.append(ma)
        
        # Find the average pattern by aligning runs
        # We'll use cross-correlation to find best alignment
        reference = moving_averages[0]
        aligned_runs = [reference]
        
        for ma in moving_averages[1:]:
            # Find best offset using cross-correlation
            best_offset = 0
            best_corr = -1
            
            for offset in range(-50, 51):  # Search range for alignment
                if offset < 0:
                    ref_slice = reference[-offset:]
                    ma_slice = ma[:len(ref_slice)]
                else:
                    ref_slice = reference[:len(ma) - offset]
                    ma_slice = ma[offset:]
                
                if len(ref_slice) > 20 and len(ma_slice) > 20:
                    min_len = min(len(ref_slice), len(ma_slice))
                    corr = np.corrcoef(ref_slice[:min_len], ma_slice[:min_len])[0, 1]
                    
                    if corr > best_corr:
                        best_corr = corr
                        best_offset = offset
            
            # Apply best offset
            if best_offset < 0:
                aligned = [0.5] * abs(best_offset) + ma
            else:
                aligned = ma[best_offset:]
            aligned_runs.append(aligned)
        
        # Calculate average pattern
        max_len = max(len(run) for run in aligned_runs)
        avg_pattern = []
        std_pattern = []
        
        for i in range(max_len):
            values = [run[i] for run in aligned_runs if i < len(run)]
            if values:
                avg_pattern.append(np.mean(values))
                std_pattern.append(np.std(values))
        
        # Smooth the pattern
        if len(avg_pattern) > 15:
            avg_pattern_smooth = savgol_filter(avg_pattern, 
                                              window_length=min(15, len(avg_pattern)//2*2-1), 
                                              polyorder=3)
        else:
            avg_pattern_smooth = avg_pattern
        
        # Detect cycle length using autocorrelation
        autocorr = np.correlate(avg_pattern_smooth - np.mean(avg_pattern_smooth), 
                               avg_pattern_smooth - np.mean(avg_pattern_smooth), 
                               mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find peaks in autocorrelation (potential cycle lengths)
        cycle_candidates = []
        for i in range(20, min(150, len(autocorr)-1)):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                cycle_candidates.append((i, autocorr[i]))
        
        cycle_length = None
        if cycle_candidates:
            cycle_candidates.sort(key=lambda x: x[1], reverse=True)
            cycle_length = cycle_candidates[0][0]
            print(f"  Detected cycle length: {cycle_length} trips")
        
        # Create interpolation function for prediction
        x = np.arange(len(avg_pattern_smooth))
        predictor = interp1d(x, avg_pattern_smooth, 
                           kind='cubic', 
                           fill_value='extrapolate',
                           bounds_error=False)
        
        # Package the trend data
        trend_data = {
            'planet_id': planet_id,
            'planet_name': self.planet_names[planet_id],
            'raw_runs': all_runs,
            'moving_averages': moving_averages,
            'avg_pattern': avg_pattern,
            'avg_pattern_smooth': avg_pattern_smooth.tolist(),
            'std_pattern': std_pattern,
            'cycle_length': cycle_length,
            'predictor_x': x.tolist(),
            'predictor_y': avg_pattern_smooth.tolist(),
            'num_runs': len(all_runs)
        }
        
        # Print statistics
        overall_avg = np.mean([sum(run)/len(run) for run in all_runs])
        print(f"  Overall average success rate: {overall_avg:.1%}")
        print(f"  Pattern length: {len(avg_pattern)} trips")
        print(f"  Max success rate in pattern: {max(avg_pattern_smooth):.1%}")
        print(f"  Min success rate in pattern: {min(avg_pattern_smooth):.1%}")
        
        return trend_data
    
    def visualize_trends(self, trend_data):
        """Visualize the learned trend patterns"""
        if not trend_data:
            return
            
        planet_name = trend_data['planet_name']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Trend Analysis: {planet_name}', fontsize=16, fontweight='bold')
        
        # Plot 1: All runs overlaid
        ax = axes[0, 0]
        for i, ma in enumerate(trend_data['moving_averages']):
            ax.plot(ma, alpha=0.3, linewidth=1)
        ax.set_title('All Runs (Moving Averages)')
        ax.set_xlabel('Trip Number')
        ax.set_ylabel('Success Rate')
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Average pattern with std deviation
        ax = axes[0, 1]
        avg = np.array(trend_data['avg_pattern'])
        std = np.array(trend_data['std_pattern'])
        smooth = np.array(trend_data['avg_pattern_smooth'])
        
        x = np.arange(len(avg))
        ax.plot(x, avg, 'b-', alpha=0.5, label='Raw average')
        ax.plot(x, smooth, 'r-', linewidth=2, label='Smoothed pattern')
        ax.fill_between(x, smooth - std, smooth + std, alpha=0.2, color='blue')
        ax.set_title('Learned Pattern (with std deviation)')
        ax.set_xlabel('Trip Number')
        ax.set_ylabel('Success Rate')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Cycle detection
        ax = axes[1, 0]
        if trend_data['cycle_length']:
            cycle_len = trend_data['cycle_length']
            # Show multiple cycles
            extended = []
            for i in range(len(smooth) + cycle_len):
                extended.append(smooth[i % len(smooth)])
            
            ax.plot(extended, 'g-', linewidth=2)
            
            # Mark cycle boundaries
            for i in range(0, len(extended), cycle_len):
                ax.axvline(x=i, color='red', linestyle='--', alpha=0.5)
            
            ax.set_title(f'Detected Cycle (Length = {cycle_len} trips)')
        else:
            ax.plot(smooth, 'g-', linewidth=2)
            ax.set_title('Pattern (No clear cycle detected)')
        
        ax.set_xlabel('Trip Number')
        ax.set_ylabel('Success Rate')
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Statistics
        ax = axes[1, 1]
        ax.axis('off')
        
        cycle_text = f"Cycle found: {trend_data['cycle_length']} trips" if trend_data['cycle_length'] else 'No clear cycle detected'
        
        stats_text = f"""
        Trend Statistics for {planet_name}:
        
        Number of runs analyzed: {trend_data['num_runs']}
        Pattern length: {len(trend_data['avg_pattern'])} trips
        
        Success Rate Range:
          Maximum: {max(smooth):.1%}
          Minimum: {min(smooth):.1%}
          Average: {np.mean(smooth):.1%}
        
        Cycle Detection:
          {cycle_text}
        
        Predictability Score: {self.calculate_predictability(trend_data):.1%}
        """
        
        ax.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                fontfamily='monospace', transform=ax.transAxes)
        
        plt.tight_layout()
        
        # Save figure
        filename = f"trend_{planet_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        print(f"\n📊 Visualization saved to: {filename}")
        plt.show()
    
    def calculate_predictability(self, trend_data):
        """Calculate how predictable a planet's pattern is"""
        moving_averages = trend_data['moving_averages']
        
        if len(moving_averages) < 2:
            return 0
        
        # Calculate correlation between runs
        correlations = []
        for i in range(len(moving_averages)):
            for j in range(i+1, len(moving_averages)):
                min_len = min(len(moving_averages[i]), len(moving_averages[j]))
                if min_len > 20:
                    corr = np.corrcoef(moving_averages[i][:min_len], 
                                       moving_averages[j][:min_len])[0, 1]
                    correlations.append(corr)
        
        return np.mean(correlations) * 100 if correlations else 0
    
    def save_trends(self, all_trends, filename='planet_trends.pkl'):
        """Save learned trends to file"""
        with open(filename, 'wb') as f:
            pickle.dump(all_trends, f)
        print(f"\n📁 Trends saved to: {filename}")
        
        # Also save as JSON (without raw data for readability)
        json_data = {}
        for planet_id, trend in all_trends.items():
            json_data[planet_id] = {
                'planet_name': trend['planet_name'],
                'avg_pattern_smooth': trend['avg_pattern_smooth'],
                'cycle_length': trend['cycle_length'],
                'num_runs': trend['num_runs']
            }
        
        json_filename = filename.replace('.pkl', '.json')
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"📁 Summary saved to: {json_filename}")

def main():
    print("="*60)
    print("PLANET TREND LEARNING SYSTEM")
    print("Optimized for Purge (Planet 2) - Sends 1 Morty per trip")
    print("="*60)
    
    # Get token
    token = "5cc6cdce490fbfb99d2b61775826a8125be47bce"
    
    learner = TrendLearner(token)
    
    # Focus on Purge planet only
    print("\n🎯 Collecting data for PURGE PLANET (Planet 2)")
    print("This will send 1 Morty per trip for better granularity")
    
    print("\n📊 How many runs? (default: 10)")
    runs = input("> ").strip()
    runs_per_planet = int(runs) if runs else 10
    
    # Learn trends for Purge with 1 Morty per trip
    planet_id = 2  # Purge
    trend_data = learner.learn_planet_trends(planet_id, runs_per_planet, morty_count=1)
    
    if trend_data:
        learner.visualize_trends(trend_data)
        
        # Save trend
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'purge_trend_{timestamp}.pkl'
        learner.save_trends({planet_id: trend_data}, filename)
        
        print("\n" + "="*60)
        print("PURGE TREND LEARNING COMPLETE")
        print("="*60)
        print(f"\n{trend_data['planet_name']}:")
        print(f"  Total runs analyzed: {trend_data['num_runs']}")
        print(f"  Pattern length: {len(trend_data['avg_pattern'])}")
        if trend_data['cycle_length']:
            print(f"  Cycle length: {trend_data['cycle_length']} trips")
        print(f"  Predictability: {learner.calculate_predictability(trend_data):.1%}")
    else:
        print("\n❌ Failed to collect Purge trend data")

if __name__ == "__main__":
    main()