"""
Web Dashboard for Multi-Agent Personality Bot System
Flask-based interface with interactive visualizations
"""

from flask import Flask, render_template, jsonify, request
import os
import base64
import requests
from dotenv import load_dotenv
import json
from datetime import datetime
import random

# Import our bot classes
import sys
sys.path.append(os.path.dirname(__file__))
from multi_agent_demo_mock import ExecutiveBot, BoardRoom, generate_mock_runs

load_dotenv()
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
FORIO_ORG = os.getenv("FORIO_ORG", "mitcams")
FORIO_PROJECT = os.getenv("FORIO_PROJECT", "cyberriskmanagement-ransomeware-2023")

app = Flask(__name__)

# Initialize bots
cfo = ExecutiveBot(
    "CFO", 
    "accumulated_profit", 
    target={"min": 1200000},
    personality={"risk_tolerance": 0.3, "friendliness": 0.6, "ambition": 0.8}
)

cro = ExecutiveBot(
    "CRO", 
    "compromised_systems", 
    target={"max": 10},
    personality={"risk_tolerance": 0.2, "friendliness": 0.5, "ambition": 0.6}
)

coo = ExecutiveBot(
    "COO", 
    "systems_availability", 
    target={"min": 0.92},
    personality={"risk_tolerance": 0.5, "friendliness": 0.7, "ambition": 0.7}
)

board = BoardRoom([cfo, cro, coo])


def get_forio_token():
    """Get OAuth token from Forio."""
    try:
        creds = base64.b64encode(f"{PUBLIC_KEY}:{PRIVATE_KEY}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {creds}"
        }
        data = {"grant_type": "client_credentials"}
        r = requests.post("https://api.forio.com/v2/oauth/token", headers=headers, data=data)
        r.raise_for_status()
        return r.json()["access_token"]
    except:
        return None


def fetch_forio_runs(limit=10):
    """Fetch run metadata from Forio (no variables available yet)."""
    token = get_forio_token()
    if not token:
        return []
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://forio.com/v2/run/{FORIO_ORG}/{FORIO_PROJECT}/;saved=true;trashed=false"
    url += f"?sort=created&direction=desc&startRecord=0&endRecord={limit}"
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/runs')
def api_runs():
    """Get simulation runs (mock data for now)."""
    # Try to fetch real runs for metadata
    real_runs = fetch_forio_runs(5)
    
    # Generate mock data with realistic structure
    mock_runs = generate_mock_runs(5)
    
    # If we have real runs, use their metadata
    if real_runs:
        for i, (mock, real) in enumerate(zip(mock_runs, real_runs)):
            mock['id'] = real.get('id', f'mock_{i}')
            mock['created'] = real.get('created', datetime.now().isoformat())
            mock['user'] = real.get('user', {}).get('userName', 'Unknown')
            mock['group'] = real.get('scope', {}).get('group', 'default')
    
    return jsonify(mock_runs)


@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """Evaluate a run with personality bots."""
    data = request.json
    run_data = data.get('run', {})
    
    # Get bot evaluations
    feedback = board.run_meeting(run_data)
    recommendations = board.negotiate_strategy(run_data)
    interaction = board.simulate_interaction('collaborative')
    
    return jsonify({
        'feedback': feedback,
        'recommendations': recommendations,
        'interaction': interaction
    })


@app.route('/api/bots')
def api_bots():
    """Get bot information."""
    bots_info = []
    for bot in board.bots:
        bots_info.append({
            'name': bot.name,
            'kpi_focus': bot.kpi_focus,
            'target': bot.target,
            'personality': bot.personality
        })
    return jsonify(bots_info)


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare multiple runs."""
    data = request.json
    run_ids = data.get('run_ids', [])
    
    # For now, generate comparison data
    # In production, this would fetch real runs
    runs = generate_mock_runs(len(run_ids))
    
    comparison = {
        'runs': runs,
        'best_profit': max(runs, key=lambda r: r['accumulated_profit']),
        'best_security': min(runs, key=lambda r: r['compromised_systems']),
        'best_availability': max(runs, key=lambda r: r['systems_availability'])
    }
    
    return jsonify(comparison)


@app.route('/api/forio/status')
def api_forio_status():
    """Check Forio connection status."""
    token = get_forio_token()
    if not token:
        return jsonify({'connected': False, 'error': 'Authentication failed'})
    
    runs = fetch_forio_runs(1)
    return jsonify({
        'connected': True,
        'runs_available': len(runs) > 0,
        'run_count': len(runs),
        'note': 'Variables not recorded in Vensim model'
    })


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("=" * 70)
    print("🚀 Multi-Agent Dashboard Starting...")
    print("=" * 70)
    print("\n📊 Dashboard will be available at: http://localhost:5000")
    print("\n✨ Features:")
    print("  • Real-time run analysis")
    print("  • Interactive bot evaluations")
    print("  • Strategy comparison")
    print("  • Personality bot insights")
    print("\n⚠️  Note: Using mock data until Vensim model records variables")
    print("\n" + "=" * 70)
    
    app.run(debug=True, port=5000)
