"""
Liliput Benchmark CLI
====================

Performance benchmarking tools for quantum circuits.
"""

import time
import json
import statistics
from typing import Dict, List, Any, Optional

def benchmark_circuit(engine, file_path: str, backend: str = "simulator", 
                     runs: int = 5, shots: int = 1024) -> Dict[str, Any]:
    """Benchmark a single circuit."""
    execution_times = []
    gate_counts = []
    
    for i in range(runs):
        try:
            result = engine.run_file(file_path, backend=backend, shots=shots)
            if result.success:
                execution_times.append(result.execution_time)
                gate_counts.append(result.metadata.get('total_gates', 0))
            else:
                print(f"⚠️  Run {i+1} failed: {result.results.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️  Run {i+1} error: {e}")
    
    if not execution_times:
        return {'error': 'All benchmark runs failed'}
    
    return {
        'file': file_path,
        'backend': backend,
        'runs': len(execution_times),
        'shots': shots,
        'execution_times': execution_times,
        'avg_time': statistics.mean(execution_times),
        'min_time': min(execution_times),
        'max_time': max(execution_times),
        'std_time': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
        'total_gates': gate_counts[0] if gate_counts else 0,
        'throughput_ops_per_sec': gate_counts[0] / statistics.mean(execution_times) if gate_counts and execution_times else 0
    }

def print_benchmark_results(results: Dict[str, Any]):
    """Print formatted benchmark results."""
    if 'error' in results:
        print(f"❌ {results['error']}")
        return
    
    print(f"📊 Benchmark Results for {results['file']}")
    print(f"   Backend: {results['backend']}")
    print(f"   Runs: {results['runs']}")
    print(f"   Shots per run: {results['shots']}")
    print(f"   Total gates: {results['total_gates']}")
    print()
    print(f"   Average time: {results['avg_time']:.3f}s")
    print(f"   Min time: {results['min_time']:.3f}s")
    print(f"   Max time: {results['max_time']:.3f}s")
    print(f"   Std deviation: {results['std_time']:.3f}s")
    print(f"   Throughput: {results['throughput_ops_per_sec']:.1f} gates/sec")

def run_benchmarks():
    """Run comprehensive benchmarks."""
    import sys
    import os
    
    # Add parent directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.insert(0, parent_dir)
    
    from liliput.core.engine import LiliputEngine
    
    engine = LiliputEngine()
    
    # Test files
    test_files = []
    if os.path.exists('examples/basic_quantum.gl'):
        test_files.append('examples/basic_quantum.gl')
    if os.path.exists('examples/grover.gl'):
        test_files.append('examples/grover.gl')
    
    if not test_files:
        print("❌ No test files found")
        return
    
    print("🚀 Running Liliput Benchmarks")
    print("=" * 40)
    
    all_results = []
    
    for file_path in test_files:
        print(f"\n📝 Benchmarking {file_path}")
        result = benchmark_circuit(engine, file_path, runs=3)
        all_results.append(result)
        print_benchmark_results(result)
    
    # Summary
    print("\n📈 Benchmark Summary")
    print("-" * 30)
    
    for result in all_results:
        if 'error' not in result:
            filename = result['file'].split('/')[-1]
            print(f"{filename:<20} {result['avg_time']:.3f}s avg, {result['throughput_ops_per_sec']:.0f} gates/sec")

if __name__ == '__main__':
    run_benchmarks()