#!/usr/bin/env env python3
"""
Planet Trend Alignment and Averaging Script

This script processes multiple runs of planet data, aligns them to account for
different starting positions in cycles, and produces averaged trend curves.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import signal, interpolate
from typing import List, Dict, Tuple
import argparse


class PlanetTrendAnalyzer:
    """Analyzes and aligns planet trend data from multiple runs."""
    
    def __init__(self, planet_id: int, planet_name: str, expected_cycle_length: int = None):
        self.planet_id = planet_id
        self.planet_name = planet_name
        self.expected_cycle_length = expected_cycle_length
        self.runs = []
        self.aligned_runs = []
        self.averaged_trend = None
        self.cycle_length = None
        
    def load_run(self, filepath: str):
        """Load a single run JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if data['planet_id'] != self.planet_id:
            raise ValueError(f"Planet ID mismatch: expected {self.planet_id}, got {data['planet_id']}")
        
        self.runs.append({
            'results': np.array(data['results']),
            'success_rate': data['success_rate'],
            'total_trips': data['total_trips'],
            'run_number': data.get('run_number', len(self.runs) + 1),
            'timestamp': data.get('timestamp', 'unknown')
        })
        
        print(f"Loaded {self.planet_name} run #{len(self.runs)}: {len(data['results'])} trips, {data['success_rate']*100:.1f}% success")
    
    def detect_cycle_length(self, max_lag: int = 100) -> int:
        """Detect cycle length using autocorrelation on the first run."""
        if len(self.runs) == 0:
            raise ValueError("No runs loaded")
        
        data = self.runs[0]['results']
        
        # Compute autocorrelation
        autocorr = np.correlate(data - np.mean(data), data - np.mean(data), mode='full')
        autocorr = autocorr[len(autocorr)//2:]  # Take only positive lags
        autocorr = autocorr / autocorr[0]  # Normalize
        
        # Find peaks in autocorrelation (excluding the peak at lag=0)
        peaks, properties = signal.find_peaks(autocorr[1:max_lag], height=0.1, distance=5)
        
        if len(peaks) > 0:
            # The first significant peak is likely the cycle length
            detected_cycle = peaks[0] + 1  # +1 because we excluded lag=0
            print(f"Detected cycle length: {detected_cycle}")
            return detected_cycle
        else:
            print(f"Could not detect cycle, using expected: {self.expected_cycle_length}")
            return self.expected_cycle_length if self.expected_cycle_length else 50
    
    def align_runs_cross_correlation(self):
        """Align all runs using cross-correlation to find best offset."""
        if len(self.runs) == 0:
            raise ValueError("No runs loaded")
        
        # Use first run as reference
        reference = self.runs[0]['results']
        
        # Detect cycle length if not set
        if self.cycle_length is None:
            self.cycle_length = self.detect_cycle_length()
        
        self.aligned_runs = []
        
        for i, run in enumerate(self.runs):
            data = run['results']
            
            if i == 0:
                # Reference run - no alignment needed
                self.aligned_runs.append({
                    'data': data,
                    'offset': 0,
                    'run_info': run
                })
                continue
            
            # Find best alignment using cross-correlation
            # We'll try different circular shifts and find the one with highest correlation
            best_offset = 0
            best_correlation = -np.inf
            
            # Only search within one cycle length
            search_range = min(self.cycle_length, len(data))
            
            for offset in range(search_range):
                # Circular shift
                shifted = np.roll(data, offset)
                
                # Compute correlation with reference (using overlapping region)
                overlap_len = min(len(reference), len(shifted))
                corr = np.corrcoef(reference[:overlap_len], shifted[:overlap_len])[0, 1]
                
                if corr > best_correlation:
                    best_correlation = corr
                    best_offset = offset
            
            aligned_data = np.roll(data, best_offset)
            
            self.aligned_runs.append({
                'data': aligned_data,
                'offset': best_offset,
                'correlation': best_correlation,
                'run_info': run
            })
            
            print(f"  Run {i+1}: offset={best_offset}, correlation={best_correlation:.3f}")
    
    def average_aligned_runs(self, window_size: int = 5):
        """Average all aligned runs and apply smoothing."""
        if len(self.aligned_runs) == 0:
            raise ValueError("No aligned runs available")
        
        # Find minimum length
        min_length = min(len(run['data']) for run in self.aligned_runs)
        
        # Truncate all runs to same length and stack
        aligned_data = np.vstack([run['data'][:min_length] for run in self.aligned_runs])
        
        # Compute mean at each position
        mean_trend = np.mean(aligned_data, axis=0)
        std_trend = np.std(aligned_data, axis=0)
        
        # Apply moving average for smoothing
        if window_size > 1:
            kernel = np.ones(window_size) / window_size
            mean_trend_smooth = np.convolve(mean_trend, kernel, mode='same')
            std_trend_smooth = np.convolve(std_trend, kernel, mode='same')
        else:
            mean_trend_smooth = mean_trend
            std_trend_smooth = std_trend
        
        self.averaged_trend = {
            'mean': mean_trend_smooth,
            'std': std_trend_smooth,
            'raw_mean': mean_trend,
            'length': min_length,
            'num_runs': len(self.aligned_runs)
        }
        
        print(f"Averaged trend created: {min_length} positions, {len(self.aligned_runs)} runs")
        print(f"  Mean success rate: {np.mean(mean_trend)*100:.1f}%")
        print(f"  Min: {np.min(mean_trend)*100:.1f}%, Max: {np.max(mean_trend)*100:.1f}%")
    
    def visualize_alignment(self, save_path: str = None):
        """Create comprehensive visualization of alignment process."""
        fig = plt.figure(figsize=(18, 10))
        
        # 1. Original runs (overlaid)
        ax1 = plt.subplot(2, 3, 1)
        for i, run in enumerate(self.runs):
            # Compute moving average for visualization
            window = 10
            ma = np.convolve(run['results'], np.ones(window)/window, mode='same')
            ax1.plot(ma, alpha=0.5, label=f"Run {run['run_number']}")
        ax1.set_title(f"{self.planet_name}: Original Runs (MA-10)")
        ax1.set_xlabel("Trip Number")
        ax1.set_ylabel("Success Rate")
        ax1.set_ylim(-0.05, 1.05)
        ax1.legend(loc='best', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # 2. Aligned runs (overlaid)
        ax2 = plt.subplot(2, 3, 2)
        for i, aligned in enumerate(self.aligned_runs):
            window = 10
            ma = np.convolve(aligned['data'], np.ones(window)/window, mode='same')
            offset_info = f" (offset={aligned['offset']})" if 'offset' in aligned else ""
            ax2.plot(ma, alpha=0.5, label=f"Run {i+1}{offset_info}")
        ax2.set_title(f"{self.planet_name}: Aligned Runs (MA-10)")
        ax2.set_xlabel("Aligned Position")
        ax2.set_ylabel("Success Rate")
        ax2.set_ylim(-0.05, 1.05)
        ax2.legend(loc='best', fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 3. Averaged trend with confidence bands
        ax3 = plt.subplot(2, 3, 3)
        if self.averaged_trend:
            positions = np.arange(self.averaged_trend['length'])
            mean = self.averaged_trend['mean']
            std = self.averaged_trend['std']
            
            ax3.plot(positions, mean, 'b-', linewidth=2, label='Mean')
            ax3.fill_between(positions, mean - std, mean + std, alpha=0.3, label='±1 STD')
            ax3.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50% line')
            ax3.set_title(f"{self.planet_name}: Averaged Trend")
            ax3.set_xlabel("Position in Cycle")
            ax3.set_ylabel("Success Probability")
            ax3.set_ylim(-0.05, 1.05)
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. Autocorrelation of averaged trend
        ax4 = plt.subplot(2, 3, 4)
        if self.averaged_trend:
            data = self.averaged_trend['mean']
            autocorr = np.correlate(data - np.mean(data), data - np.mean(data), mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            autocorr = autocorr / autocorr[0]
            
            ax4.plot(autocorr[:min(100, len(autocorr))], 'b-')
            ax4.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            if self.cycle_length:
                ax4.axvline(x=self.cycle_length, color='red', linestyle='--', 
                           label=f'Detected cycle: {self.cycle_length}')
                ax4.legend()
            ax4.set_title("Autocorrelation of Averaged Trend")
            ax4.set_xlabel("Lag")
            ax4.set_ylabel("Autocorrelation")
            ax4.grid(True, alpha=0.3)
        
        # 5. Trend quality metrics
        ax5 = plt.subplot(2, 3, 5)
        if self.aligned_runs and len(self.aligned_runs) > 1:
            correlations = [run.get('correlation', 0) for run in self.aligned_runs[1:]]
            ax5.bar(range(1, len(correlations)+1), correlations)
            ax5.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Target: 0.5')
            ax5.set_title("Alignment Quality (Correlation)")
            ax5.set_xlabel("Run Number")
            ax5.set_ylabel("Correlation with Reference")
            ax5.set_ylim(0, 1)
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        
        # 6. Statistics summary
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        stats_text = f"{self.planet_name} Statistics\n" + "="*40 + "\n\n"
        stats_text += f"Total Runs: {len(self.runs)}\n"
        stats_text += f"Detected Cycle Length: {self.cycle_length}\n\n"
        
        if self.averaged_trend:
            stats_text += f"Averaged Trend:\n"
            stats_text += f"  Length: {self.averaged_trend['length']} positions\n"
            stats_text += f"  Mean Success: {np.mean(self.averaged_trend['mean'])*100:.1f}%\n"
            stats_text += f"  Min: {np.min(self.averaged_trend['mean'])*100:.1f}%\n"
            stats_text += f"  Max: {np.max(self.averaged_trend['mean'])*100:.1f}%\n"
            stats_text += f"  Std Dev: {np.mean(self.averaged_trend['std'])*100:.1f}%\n\n"
            
            # Find best and worst windows
            window = 10
            ma_trend = np.convolve(self.averaged_trend['mean'], np.ones(window)/window, mode='valid')
            best_idx = np.argmax(ma_trend)
            worst_idx = np.argmin(ma_trend)
            
            stats_text += f"Best Window (MA-{window}):\n"
            stats_text += f"  Position {best_idx}-{best_idx+window}: {ma_trend[best_idx]*100:.1f}%\n\n"
            stats_text += f"Worst Window (MA-{window}):\n"
            stats_text += f"  Position {worst_idx}-{worst_idx+window}: {ma_trend[worst_idx]*100:.1f}%\n"
        
        ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to {save_path}")
        
        plt.show()
    
    def save_averaged_trend(self, output_path: str):
        """Save the averaged trend to a JSON file."""
        if self.averaged_trend is None:
            raise ValueError("No averaged trend available")
        
        output_data = {
            'planet_id': self.planet_id,
            'planet_name': self.planet_name,
            'cycle_length': int(self.cycle_length) if self.cycle_length else None,
            'num_runs_used': self.averaged_trend['num_runs'],
            'trend_length': self.averaged_trend['length'],
            'mean_success_rate': float(np.mean(self.averaged_trend['mean'])),
            'trend': self.averaged_trend['mean'].tolist(),
            'std': self.averaged_trend['std'].tolist(),
            'raw_trend': self.averaged_trend['raw_mean'].tolist()
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Saved averaged trend to {output_path}")


def process_planet_data(planet_id: int, planet_name: str, 
                       input_files: List[str], 
                       expected_cycle: int = None,
                       output_dir: str = ".",
                       smoothing_window: int = 5):
    """Process all data for a single planet."""
    
    print(f"\n{'='*60}")
    print(f"Processing {planet_name} (Planet {planet_id})")
    print(f"{'='*60}")
    
    analyzer = PlanetTrendAnalyzer(planet_id, planet_name, expected_cycle)
    
    # Load all runs
    for filepath in input_files:
        try:
            analyzer.load_run(filepath)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    if len(analyzer.runs) == 0:
        print(f"No valid runs loaded for {planet_name}")
        return None
    
    # Detect cycle if not provided
    if expected_cycle is None:
        analyzer.cycle_length = analyzer.detect_cycle_length()
    else:
        analyzer.cycle_length = expected_cycle
    
    # Align runs
    print("\nAligning runs...")
    analyzer.align_runs_cross_correlation()
    
    # Average
    print("\nAveraging aligned runs...")
    analyzer.average_aligned_runs(window_size=smoothing_window)
    
    # Visualize
    print("\nGenerating visualization...")
    viz_path = f"{output_dir}/{planet_name.lower().replace(' ', '_')}_analysis.png"
    analyzer.visualize_alignment(save_path=viz_path)
    
    # Save averaged trend
    trend_path = f"{output_dir}/planet_{planet_id}_trend.json"
    analyzer.save_averaged_trend(trend_path)
    
    return analyzer


def main():
    parser = argparse.ArgumentParser(description='Align and average planet trend data')
    parser.add_argument('--planet-0-files', nargs='+', help='JSON files for Planet 0 (On a Cob)')
    parser.add_argument('--planet-1-files', nargs='+', help='JSON files for Planet 1 (Cronenberg)')
    parser.add_argument('--planet-2-files', nargs='+', help='JSON files for Planet 2 (Purge)')
    parser.add_argument('--cycle-0', type=int, default=7, help='Expected cycle for Planet 0')
    parser.add_argument('--cycle-1', type=int, default=12, help='Expected cycle for Planet 1')
    parser.add_argument('--cycle-2', type=int, default=None, help='Expected cycle for Planet 2')
    parser.add_argument('--output-dir', type=str, default='/mnt/user-data/outputs', help='Output directory')
    parser.add_argument('--smoothing', type=int, default=5, help='Smoothing window size')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Process each planet
    if args.planet_0_files:
        results[0] = process_planet_data(0, "On a Cob", args.planet_0_files, 
                                        args.cycle_0, args.output_dir, args.smoothing)
    
    if args.planet_1_files:
        results[1] = process_planet_data(1, "Cronenberg", args.planet_1_files,
                                        args.cycle_1, args.output_dir, args.smoothing)
    
    if args.planet_2_files:
        results[2] = process_planet_data(2, "Purge", args.planet_2_files,
                                        args.cycle_2, args.output_dir, args.smoothing)
    
    print("\n" + "="*60)
    print("Processing complete!")
    print("="*60)
    
    return results


if __name__ == "__main__":
    main()