"""
Quick script to check if dashboard is running and accessible.
"""

import requests
import time
import sys

def check_dashboard():
    """Check if dashboard is running."""
    # Try port 5001 first (default), then 5000
    ports = [5001, 5000]
    url = None
    
    for port in ports:
        test_url = f"http://127.0.0.1:{port}"
        try:
            response = requests.get(test_url, timeout=2)
            if response.status_code == 200:
                url = test_url
                break
        except:
            continue
    
    if not url:
        url = "http://127.0.0.1:5001"  # Default to 5001
    
    print("=" * 70)
    print("🔍 Checking Dashboard Status")
    print("=" * 70)
    
    # Check main page
    print(f"\n1. Checking main page: {url}")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Dashboard is running! (Status: {response.status_code})")
        else:
            print(f"   ⚠️  Dashboard responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Dashboard is not running")
        print("\n   💡 Start the dashboard with: python dashboard.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Check API endpoint
    print(f"\n2. Checking API endpoint: {url}/api/runs")
    try:
        response = requests.get(f"{url}/api/runs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API is working! Found {len(data)} runs")
            if data:
                sample = data[0]
                print(f"   Sample run: {sample.get('strategy', 'N/A')}")
                print(f"   Has F1-F4: {'F1' in sample and 'F2' in sample}")
        else:
            print(f"   ⚠️  API responded with status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API error: {e}")
        return False
    
    # Check bots endpoint
    print(f"\n3. Checking bots endpoint: {url}/api/bots")
    try:
        response = requests.get(f"{url}/api/bots", timeout=5)
        if response.status_code == 200:
            bots = response.json()
            print(f"   ✅ Bots endpoint working! Found {len(bots)} bots")
            for bot in bots:
                print(f"   - {bot.get('name')}: {bot.get('kpi_focus')}")
        else:
            print(f"   ⚠️  Bots endpoint status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Bots endpoint error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Dashboard is accessible!")
    print("=" * 70)
    print(f"\n🌐 Open in browser: {url}")
    print("\n✨ You can now:")
    print("   • View all simulation runs")
    print("   • Click on runs to see agent evaluations")
    print("   • Compare different strategies")
    print("   • View KPI charts")
    
    return True


if __name__ == '__main__':
    # Wait a moment for server to start if just launched
    if len(sys.argv) > 1 and sys.argv[1] == '--wait':
        print("⏳ Waiting 3 seconds for server to start...")
        time.sleep(3)
    
    success = check_dashboard()
    sys.exit(0 if success else 1)

