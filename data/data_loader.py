"""
Unified Data Loader
Single interface for loading simulation data from any source.
Priority: Manual Data > Forio API > Mock Data
"""

import os
import json
import random
from typing import List, Dict, Optional
from datetime import datetime

def generate_mock_runs(n: int = 5) -> List[Dict]:
    """Generate mock simulation data for demonstration."""
    runs = []
    for i in range(n):
        prevention = random.randint(30, 70)
        detection = random.randint(20, 50)
        response = random.randint(10, 30)
        
        profit = 1000000 + (prevention * 15000) + random.randint(-200000, 200000)
        compromised = max(0, 20 - (prevention // 5) - (detection // 10) + random.randint(-3, 3))
        availability = min(1.0, 0.85 + (prevention * 0.002) + (detection * 0.001) + random.uniform(-0.05, 0.05))
        
        runs.append({
            "id": f"mock_run_{i+1}",
            "strategy": f"Strategy {chr(65+i)}",
            "prevention_budget": prevention,
            "detection_budget": detection,
            "response_budget": response,
            "accumulated_profit": profit,
            "compromised_systems": compromised,
            "systems_availability": availability,
            "created": datetime.now().isoformat(),
            "user": "Mock User",
            "group": "demo",
            "source": "mock"
        })
    
    return runs


def load_manual_data() -> Optional[List[Dict]]:
    """Load manually entered data from JSON files."""
    candidates = [
        'simulation_data.json',
        'automated_dataset.json',
        'automated_simulation_data.json'
    ]
    
    for filename in candidates:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Convert dict to list if needed
                if isinstance(data, dict):
                    runs = list(data.values())
                else:
                    runs = data
                
                # Add source marker
                for run in runs:
                    run['source'] = 'manual'
                
                if runs:
                    print(f"✓ Loaded {len(runs)} runs from {filename}")
                    return runs
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    return None


def load_forio_data() -> Optional[List[Dict]]:
    """Try to load data from Forio API."""
    try:
        from data.forio_client import ForioClient
        
        client = ForioClient()
        if not client.is_configured():
            return None
        
        runs = client.fetch_runs(limit=20)
        
        # Check if runs have actual data
        runs_with_data = [r for r in runs if has_simulation_data(r)]
        
        if runs_with_data:
            for run in runs_with_data:
                run['source'] = 'forio'
            print(f"✓ Loaded {len(runs_with_data)} runs from Forio")
            return runs_with_data
        
    except Exception as e:
        print(f"Warning: Could not load from Forio: {e}")
    
    return None


def has_simulation_data(run: Dict) -> bool:
    """Check if a run has the required simulation data."""
    required_fields = [
        'accumulated_profit',
        'compromised_systems',
        'systems_availability'
    ]
    
    for field in required_fields:
        if field not in run or run[field] is None:
            return False
    
    return True


def load_runs(prefer_source: str = None, limit: int = 20) -> List[Dict]:
    """
    Load simulation runs from any available source.
    
    Args:
        prefer_source: 'manual', 'forio', or 'mock' to prefer specific source
        limit: Maximum number of runs to return
    
    Returns:
        List of simulation run dictionaries
    """
    
    if prefer_source == 'mock':
        print("Using mock data (as requested)")
        return generate_mock_runs(limit)
    
    # Priority 1: Manual data
    if prefer_source != 'forio':
        manual_data = load_manual_data()
        if manual_data:
            return manual_data[:limit]
    
    # Priority 2: Forio API
    if prefer_source != 'manual':
        forio_data = load_forio_data()
        if forio_data:
            return forio_data[:limit]
    
    # Priority 3: Mock data
    print("No manual or Forio data available, using mock data")
    return generate_mock_runs(limit)


def get_data_source_info() -> Dict:
    """Get information about available data sources."""
    info = {
        'manual': {
            'available': False,
            'count': 0,
            'files': []
        },
        'forio': {
            'available': False,
            'configured': False,
            'authenticated': False
        },
        'mock': {
            'available': True
        }
    }
    
    # Check manual data
    candidates = ['simulation_data.json', 'automated_dataset.json', 'automated_simulation_data.json']
    for filename in candidates:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                runs = list(data.values()) if isinstance(data, dict) else data
                info['manual']['available'] = True
                info['manual']['count'] += len(runs)
                info['manual']['files'].append(filename)
            except:
                pass
    
    # Check Forio
    try:
        from data.forio_client import ForioClient
        client = ForioClient()
        info['forio']['configured'] = client.is_configured()
        if info['forio']['configured']:
            status = client.test_connection()
            info['forio']['authenticated'] = status.get('authenticated', False)
            info['forio']['available'] = status.get('authenticated', False)
    except:
        pass
    
    return info


def save_manual_data(runs: List[Dict], filename: str = 'simulation_data.json') -> bool:
    """Save runs to manual data file."""
    try:
        # Convert list to dict with run IDs as keys
        data = {run['id']: run for run in runs}
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✓ Saved {len(runs)} runs to {filename}")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False


if __name__ == '__main__':
    print("=" * 70)
    print("Data Loader Test")
    print("=" * 70)
    
    # Check available sources
    print("\n1. Checking available data sources...")
    info = get_data_source_info()
    
    print(f"\nManual Data: {'✓' if info['manual']['available'] else '✗'}")
    if info['manual']['available']:
        print(f"  Files: {', '.join(info['manual']['files'])}")
        print(f"  Total runs: {info['manual']['count']}")
    
    print(f"\nForio API: {'✓' if info['forio']['available'] else '✗'}")
    if info['forio']['configured']:
        print(f"  Configured: ✓")
        print(f"  Authenticated: {'✓' if info['forio']['authenticated'] else '✗'}")
    
    print(f"\nMock Data: ✓ (always available)")
    
    # Load runs
    print("\n2. Loading runs...")
    runs = load_runs(limit=5)
    
    print(f"\nLoaded {len(runs)} runs from source: {runs[0]['source']}")
    print("\nSample run:")
    sample = runs[0]
    print(f"  ID: {sample['id']}")
    print(f"  Profit: ${sample['accumulated_profit']:,.0f}")
    print(f"  Compromised: {sample['compromised_systems']}")
    print(f"  Availability: {sample['systems_availability']:.1%}")