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

# Import our bot classes and data extractor
import sys
sys.path.append(os.path.dirname(__file__))
from multi_agent_demo_mock import ExecutiveBot, BoardRoom, generate_mock_runs
from forio_data_extractor import ForioDataExtractor

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

# Initialize data extractor
extractor = ForioDataExtractor()

# Load configuration
def load_config():
    """Load extraction configuration from forio_config.json."""
    if os.path.exists('forio_config.json'):
        with open('forio_config.json', 'r') as f:
            return json.load(f)
    return {
        'variables': {
            'kpis': ['accumulated_profit', 'compromised_systems', 'systems_availability'],
            'budgets': ['prevention_budget', 'detection_budget', 'response_budget']
        },
        'groups': None,
        'model_name': None
    }


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


def load_manual_data():
    """Load manually entered simulation data."""
    # Try automated dataset first, then simulation_data.json
    if os.path.exists('automated_dataset.json'):
        with open('automated_dataset.json', 'r') as f:
            data = json.load(f)
            # Convert list to dict if needed
            if isinstance(data, list):
                return {item.get('id', f"auto_{i}"): item for i, item in enumerate(data)}
            return data
    elif os.path.exists('simulation_data.json'):
        with open('simulation_data.json', 'r') as f:
            return json.load(f)
    return {}

def fetch_forio_runs(limit=10):
    """Fetch run data from Forio using enhanced extraction with variables."""
    config = load_config()
    
    # Combine all variables we want to extract
    all_variables = []
    if 'variables' in config:
        all_variables.extend(config['variables'].get('kpis', []))
        all_variables.extend(config['variables'].get('budgets', []))
        all_variables.extend(config['variables'].get('additional', []))
    
    # If no variables configured, use defaults
    if not all_variables:
        all_variables = [
            'accumulated_profit', 'compromised_systems', 'systems_availability',
            'prevention_budget', 'detection_budget', 'response_budget'
        ]
    
    try:
        # Try enhanced extraction with variables
        runs = extractor.fetch_runs_with_variables(
            variables=all_variables,
            model_name=config.get('model_name'),
            groups=config.get('groups'),
            start_record=0,
            end_record=limit
        )
        
        if runs:
            # Load manual data for fallback
            manual_data = load_manual_data()
            
            # Check if runs have variables, merge with manual data if needed
            for run in runs:
                run_id = run['id']
                has_vars = bool(run.get('variables'))
                
                if has_vars:
                    # Extract variables to top level for easier access
                    for var in all_variables:
                        if var in run.get('variables', {}):
                            run[var] = run['variables'][var]
                    run['has_data'] = True
                elif run_id in manual_data:
                    # Fall back to manual data
                    run.update(manual_data[run_id])
                    run['has_data'] = True
                else:
                    run['has_data'] = False
            
            return runs
    except Exception as e:
        print(f"Enhanced extraction failed: {e}")
    
    # Fallback to basic metadata fetch
    try:
        runs = extractor.fetch_all_runs_metadata(start_record=0, end_record=limit)
        manual_data = load_manual_data()
        
        for run in runs:
            run_id = run['id']
            if run_id in manual_data:
                run.update(manual_data[run_id])
                run['has_data'] = True
            else:
                run['has_data'] = False
        
        return runs
    except:
        return []


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/runs')
def api_runs():
    """Get simulation runs (manual data if available, otherwise mock)."""
    # Try to fetch real runs with manual data
    real_runs = fetch_forio_runs(10)
    
    # Filter to only runs with data
    runs_with_data = [r for r in real_runs if r.get('has_data')]
    
    if runs_with_data:
        # Use real runs with manual data
        return jsonify(runs_with_data)
    else:
        # Fall back to mock data for demonstration
        mock_runs = generate_mock_runs(5)
        
        # If we have real run metadata, use it
        if real_runs:
            for i, (mock, real) in enumerate(zip(mock_runs, real_runs[:5])):
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
    """Check Forio connection status with enhanced extraction details."""
    # Test connection using extractor
    status = extractor.test_connection()
    
    if not status['authenticated']:
        return jsonify({
            'connected': False, 
            'error': 'Authentication failed',
            'details': status
        })
    
    # Get config info
    config = load_config()
    
    return jsonify({
        'connected': True,
        'authenticated': status['authenticated'],
        'runs_found': status['runs_found'],
        'variables_recorded': status['variables_recorded'],
        'sample_run': status.get('sample_run'),
        'config': {
            'variables': config.get('variables', {}),
            'groups': config.get('groups'),
            'model_name': config.get('model_name')
        },
        'extraction_method': 'enhanced' if status['variables_recorded'] else 'manual_fallback'
    })


@app.route('/api/forio/extract', methods=['POST'])
def api_forio_extract():
    """Manually trigger data extraction with custom parameters."""
    data = request.json
    variables = data.get('variables', [])
    groups = data.get('groups')
    model_name = data.get('model_name')
    limit = data.get('limit', 10)
    
    if not variables:
        return jsonify({'error': 'No variables specified'}), 400
    
    try:
        runs = extractor.fetch_runs_with_variables(
            variables=variables,
            model_name=model_name,
            groups=groups,
            start_record=0,
            end_record=limit
        )
        
        # Extract just the variables
        extracted = extractor.extract_variables_from_runs(runs, variables)
        
        return jsonify({
            'success': True,
            'runs_fetched': len(runs),
            'data': extracted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
