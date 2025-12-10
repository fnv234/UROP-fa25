"""
Manual data entry system for simulation results.
Since Vensim model doesn't save variables, this allows you to:
1. Fetch run metadata from Forio
2. Manually enter results for each run
3. Save to local JSON file
4. Use in dashboard
"""

import os
import base64
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
FORIO_ORG = os.getenv("FORIO_ORG", "mitcams")
FORIO_PROJECT = os.getenv("FORIO_PROJECT", "cyberriskmanagement-ransomeware-2023")

def get_forio_token():
    creds = base64.b64encode(f"{PUBLIC_KEY}:{PRIVATE_KEY}".encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {creds}"
    }
    data = {"grant_type": "client_credentials"}
    r = requests.post("https://api.forio.com/v2/oauth/token", headers=headers, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def fetch_runs(limit=10):
    token = get_forio_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://forio.com/v2/run/{FORIO_ORG}/{FORIO_PROJECT}/;saved=true;trashed=false"
    url += f"?sort=created&direction=desc&startRecord=0&endRecord={limit}"
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    return []

def load_existing_data():
    """Load previously entered data."""
    if os.path.exists('simulation_data.json'):
        with open('simulation_data.json', 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save data to JSON file."""
    with open('simulation_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ Data saved to simulation_data.json")

def enter_data_for_run(run):
    """Interactive data entry for a single run."""
    run_id = run['id']
    user = run.get('user', {}).get('userName', 'Unknown')
    created = run.get('created', 'Unknown')
    
    print(f"\n{'='*70}")
    print(f"Run ID: {run_id}")
    print(f"User: {user}")
    print(f"Created: {created}")
    print(f"{'='*70}")
    
    data = {}
    
    # Settings (from facilitator interface)
    print("\n📋 Simulation Settings:")
    data['simulation_level'] = input("  Simulation level (1 or 2): ").strip() or "1"
    data['attack_type'] = input("  Attack type (other/ransomware): ").strip() or "other"
    data['ransom_policy'] = input("  Ransom policy (pay/not_pay): ").strip() or "not_pay"
    data['run_limit'] = input("  Run limit (1-10 or unlimited): ").strip() or "unlimited"
    
    # Budget allocation
    print("\n💰 Budget Allocation:")
    data['prevention_budget'] = float(input("  Prevention budget: ") or "0")
    data['detection_budget'] = float(input("  Detection budget: ") or "0")
    data['response_budget'] = float(input("  Response budget: ") or "0")
    
    # Results/Outcomes
    print("\n📊 Simulation Results:")
    data['accumulated_profit'] = float(input("  Accumulated profit ($): ") or "0")
    data['compromised_systems'] = int(input("  Compromised systems: ") or "0")
    data['systems_availability'] = float(input("  Systems availability (0-1): ") or "1.0")
    data['total_attacks'] = int(input("  Total attacks: ") or "0")
    data['successful_attacks'] = int(input("  Successful attacks: ") or "0")
    
    # Metadata
    data['run_id'] = run_id
    data['user'] = user
    data['created'] = created
    data['group'] = run.get('scope', {}).get('group', 'default')
    data['entered_at'] = datetime.now().isoformat()
    
    return data

def main():
    print("=" * 70)
    print("🎯 Manual Data Entry for Forio Simulation Runs")
    print("=" * 70)
    
    # Fetch runs from Forio
    print("\n📡 Fetching runs from Forio...")
    runs = fetch_runs(10)
    
    if not runs:
        print("❌ No runs found. Check your Forio connection.")
        return
    
    print(f"✅ Found {len(runs)} runs")
    
    # Load existing data
    existing_data = load_existing_data()
    print(f"📂 Loaded {len(existing_data)} previously entered runs")
    
    # Show runs and let user choose
    print(f"\n{'='*70}")
    print("Available Runs:")
    print(f"{'='*70}")
    
    for i, run in enumerate(runs):
        run_id = run['id']
        user = run.get('user', {}).get('userName', 'Unknown')
        created = run.get('created', 'Unknown')[:10]
        status = "✓ Data entered" if run_id in existing_data else "○ No data"
        print(f"{i+1}. {status} | {user} | {created} | {run_id[:20]}...")
    
    print(f"\n{'='*70}")
    choice = input("\nEnter run number to add/edit data (or 'q' to quit): ").strip()
    
    if choice.lower() == 'q':
        print("👋 Goodbye!")
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(runs):
            run = runs[idx]
            run_id = run['id']
            
            # Check if data already exists
            if run_id in existing_data:
                print(f"\n⚠️  Data already exists for this run:")
                print(json.dumps(existing_data[run_id], indent=2))
                overwrite = input("\nOverwrite? (y/n): ").strip().lower()
                if overwrite != 'y':
                    print("Cancelled.")
                    return
            
            # Enter data
            data = enter_data_for_run(run)
            
            # Confirm
            print(f"\n{'='*70}")
            print("Review entered data:")
            print(f"{'='*70}")
            print(json.dumps(data, indent=2))
            
            confirm = input("\nSave this data? (y/n): ").strip().lower()
            if confirm == 'y':
                existing_data[run_id] = data
                save_data(existing_data)
                print("\n✅ Data saved successfully!")
                print("\nYou can now use this data in the dashboard.")
                print("Run: python dashboard.py")
            else:
                print("❌ Data not saved.")
        else:
            print("Invalid run number.")
    except ValueError:
        print("Invalid input.")

if __name__ == "__main__":
    main()
