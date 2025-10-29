"""
Test accessing variables from a specific run
This checks if variables are available when accessing the run directly
"""

import os
import base64
import requests
import json
from dotenv import load_dotenv

load_dotenv()
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
FORIO_ORG = os.getenv("FORIO_ORG", "mitcams")
FORIO_PROJECT = os.getenv("FORIO_PROJECT", "cyberriskmanagement-ransomeware-2023")

print("=" * 70)
print("🔍 TESTING RUN VARIABLE ACCESS")
print("=" * 70)

# Get OAuth token
print("\n1️⃣ Getting OAuth token...")
creds = base64.b64encode(f"{PUBLIC_KEY}:{PRIVATE_KEY}".encode()).decode()
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {creds}"
}
data = {"grant_type": "client_credentials"}
r = requests.post("https://api.forio.com/v2/oauth/token", headers=headers, data=data)
r.raise_for_status()
token = r.json()["access_token"]
print("✅ Token obtained")

# Fetch runs
print("\n2️⃣ Fetching runs...")
headers = {"Authorization": f"Bearer {token}"}
url = f"https://forio.com/v2/run/{FORIO_ORG}/{FORIO_PROJECT}/;saved=true;trashed=false"
url += "?sort=created&direction=desc&startRecord=0&endRecord=3"

resp = requests.get(url, headers=headers)
runs = resp.json()
print(f"✅ Found {len(runs)} runs")

if not runs:
    print("❌ No runs found")
    exit(1)

# Test first run
run = runs[0]
run_id = run['id']
user = run.get('user', {}).get('userName', 'Unknown')

print(f"\n3️⃣ Testing run: {run_id}")
print(f"   User: {user}")
print(f"   Created: {run.get('created', 'Unknown')}")

# Check what's in the run object
print(f"\n4️⃣ Run object keys:")
print(f"   {list(run.keys())}")

# Check if variables are in the run object
if 'variables' in run:
    print(f"\n5️⃣ Variables in run object:")
    print(f"   Count: {len(run['variables'])}")
    if run['variables']:
        print(f"   Keys: {list(run['variables'].keys())[:10]}")
    else:
        print("   ⚠️  Variables dict is empty")
else:
    print(f"\n5️⃣ No 'variables' key in run object")

# Try different API endpoints to access variables
print(f"\n6️⃣ Trying different variable endpoints...")

endpoints = [
    # Standard variable endpoint
    f"https://api.forio.com/v2/run/{FORIO_ORG}/{FORIO_PROJECT}/{run_id}/variables",
    
    # Model run endpoint
    f"https://api.forio.com/v2/model/run/{run_id}",
    
    # Direct run endpoint
    f"https://api.forio.com/v2/run/{FORIO_ORG}/{FORIO_PROJECT}/{run_id}",
    
    # Operations endpoint
    f"https://api.forio.com/v2/run/{FORIO_ORG}/{FORIO_PROJECT}/{run_id}/operations",
    
    # Data endpoint
    f"https://api.forio.com/v2/data/{FORIO_ORG}/{FORIO_PROJECT}/{run_id}",
]

for i, endpoint in enumerate(endpoints, 1):
    print(f"\n   Test {i}: {endpoint}")
    try:
        var_resp = requests.get(endpoint, headers=headers)
        print(f"   Status: {var_resp.status_code}")
        
        if var_resp.status_code == 200:
            try:
                data = var_resp.json()
                if isinstance(data, dict):
                    print(f"   ✅ Response is dict with keys: {list(data.keys())[:10]}")
                    
                    # Check for variables
                    if 'variables' in data:
                        print(f"   ✅ Found 'variables' key!")
                        print(f"   Variable count: {len(data['variables'])}")
                        if data['variables']:
                            print(f"   Sample variables: {list(data['variables'].keys())[:5]}")
                    
                    # Check for other data keys
                    for key in ['result', 'data', 'state', 'model']:
                        if key in data:
                            print(f"   ✅ Found '{key}' key!")
                            if isinstance(data[key], dict):
                                print(f"      Keys: {list(data[key].keys())[:5]}")
                elif isinstance(data, list):
                    print(f"   Response is list with {len(data)} items")
                else:
                    print(f"   Response type: {type(data)}")
            except:
                print(f"   Response (first 200 chars): {var_resp.text[:200]}")
        elif var_resp.status_code == 404:
            print(f"   ⚠️  Endpoint not found")
        elif var_resp.status_code == 403:
            print(f"   ⚠️  Access forbidden")
        else:
            print(f"   ⚠️  Error: {var_resp.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("🎯 ANALYSIS COMPLETE")
print("=" * 70)

# Check if this is a multi-player setup
if 'users' in run or 'roles' in run:
    print("\n💡 This appears to be a MULTI-PLAYER run!")
    print("   Variables might be stored per-user/per-role")
    if 'users' in run:
        print(f"   Users in run: {run['users']}")
    if 'roles' in run:
        print(f"   Roles in run: {run['roles']}")

print("\n📝 Next steps:")
print("   • If variables found: Update dashboard to use correct endpoint")
print("   • If no variables: Confirm Vensim model configuration needed")
print("   • If multi-player: May need to access specific user's perspective")
print()
