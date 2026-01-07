"""
Quick test script to verify dashboard data is accessible.
Tests the API endpoints without starting the full server.
"""

import json
import os
from flask import Flask
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_data_files():
    """Test that data files exist and are readable."""
    print("=" * 70)
    print("📊 Testing Dashboard Data Files")
    print("=" * 70)
    
    files_to_check = [
        'simulation_data.json',
        'automated_dataset.json'
    ]
    
    all_good = True
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        count = len(data)
                        print(f"✅ {filename}: {count} runs (dict format)")
                    elif isinstance(data, list):
                        count = len(data)
                        print(f"✅ {filename}: {count} runs (list format)")
                    else:
                        print(f"⚠️  {filename}: Unknown format")
                        all_good = False
                    
                    # Check sample run structure
                    if data:
                        sample = list(data.values())[0] if isinstance(data, dict) else data[0]
                        required_fields = ['F1', 'F2', 'F3', 'F4', 'accumulated_profit', 'compromised_systems']
                        missing = [f for f in required_fields if f not in sample]
                        if missing:
                            print(f"   ⚠️  Missing fields: {missing}")
                            all_good = False
                        else:
                            print(f"   ✓ All required fields present")
            except Exception as e:
                print(f"❌ {filename}: Error reading - {e}")
                all_good = False
        else:
            print(f"❌ {filename}: File not found")
            all_good = False
    
    return all_good


def test_api_endpoints():
    """Test API endpoints by importing dashboard module."""
    print("\n" + "=" * 70)
    print("🔌 Testing API Endpoints")
    print("=" * 70)
    
    try:
        # Import dashboard functions
        from dashboard import load_manual_data, fetch_forio_runs
        
        # Test loading manual data
        print("\n1. Testing load_manual_data()...")
        manual_data = load_manual_data()
        if manual_data:
            print(f"   ✅ Loaded {len(manual_data)} runs from manual data")
            sample_id = list(manual_data.keys())[0]
            sample = manual_data[sample_id]
            print(f"   Sample run ID: {sample_id}")
            print(f"   Sample strategy: {sample.get('strategy', 'N/A')}")
        else:
            print("   ⚠️  No manual data found")
        
        # Test fetching Forio runs (may fail if not connected)
        print("\n2. Testing fetch_forio_runs()...")
        try:
            forio_runs = fetch_forio_runs(limit=5)
            if forio_runs:
                print(f"   ✅ Fetched {len(forio_runs)} runs from Forio")
            else:
                print("   ⚠️  No Forio runs found (this is OK if not connected)")
        except Exception as e:
            print(f"   ⚠️  Forio fetch failed (expected if not connected): {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_structure():
    """Test that data has the correct structure for dashboard."""
    print("\n" + "=" * 70)
    print("📋 Testing Data Structure")
    print("=" * 70)
    
    try:
        with open('simulation_data.json', 'r') as f:
            data = json.load(f)
        
        if not data:
            print("❌ No data found")
            return False
        
        # Get first run
        first_run = list(data.values())[0]
        
        # Check required fields
        required = {
            'inputs': ['F1', 'F2', 'F3', 'F4', 'prevention_budget', 'detection_budget', 'response_budget', 'recovery_budget'],
            'main_outputs': ['accumulated_profit', 'profits', 'compromised_systems', 'systems_availability'],
            'additional_outputs': ['systems_at_risk', 'fraction_to_make_profits', 'impact_on_business'],
            'metadata': ['id', 'strategy', 'created']
        }
        
        all_present = True
        for category, fields in required.items():
            missing = [f for f in fields if f not in first_run]
            if missing:
                print(f"⚠️  {category}: Missing {missing}")
                all_present = False
            else:
                print(f"✅ {category}: All fields present")
        
        # Show sample values
        print(f"\n📊 Sample Run Data:")
        print(f"   Strategy: {first_run.get('strategy')}")
        print(f"   F1-F4: {first_run.get('F1')}%, {first_run.get('F2')}%, {first_run.get('F3')}%, {first_run.get('F4')}%")
        print(f"   Accumulated Profit: ${first_run.get('accumulated_profit', 0):,.0f}")
        print(f"   Compromised Systems: {first_run.get('compromised_systems')}")
        print(f"   Systems Availability: {first_run.get('systems_availability', 0):.1%}")
        
        return all_present
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🧪 Dashboard Data Verification")
    print("=" * 70)
    
    # Test 1: Data files
    files_ok = test_data_files()
    
    # Test 2: Data structure
    structure_ok = test_data_structure()
    
    # Test 3: API endpoints
    api_ok = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"Data Files: {'✅ OK' if files_ok else '❌ FAILED'}")
    print(f"Data Structure: {'✅ OK' if structure_ok else '❌ FAILED'}")
    print(f"API Endpoints: {'✅ OK' if api_ok else '⚠️  WARNINGS'}")
    
    if files_ok and structure_ok:
        print("\n✅ Dashboard data is ready!")
        print("\n🚀 To start the dashboard:")
        print("   python dashboard.py")
        print("\n🌐 Then open: http://localhost:5000")
    else:
        print("\n⚠️  Some issues found. Please check the errors above.")


if __name__ == '__main__':
    main()

