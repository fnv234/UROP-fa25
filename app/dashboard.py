"""
Multi-Agent Dashboard - Cleaned and Simplified
Uses unified data loader for all data sources.
"""

from flask import Flask, render_template, jsonify, request
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.agents import ExecutiveBot, BoardRoom, load_agent_config
from data.data_loader import load_runs, get_data_source_info

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

# Initialize bots from config
agent_config = load_agent_config()
bots = []

for name, config in agent_config.items():
    bot = ExecutiveBot(
        name=name,
        kpi_focus=config['kpi'],
        target=config['target'],
        personality=config['personality']
    )
    bots.append(bot)

board = BoardRoom(bots)


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/data-sources')
def api_data_sources():
    """Get information about available data sources."""
    return jsonify(get_data_source_info())


@app.route('/api/runs')
def api_runs():
    """Get simulation runs from best available source."""
    limit = request.args.get('limit', 20, type=int)
    source = request.args.get('source', None)
    
    runs = load_runs(prefer_source=source, limit=limit)
    return jsonify(runs)


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


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare multiple runs."""
    data = request.json
    run_ids = data.get('run_ids', [])
    
    # Load all runs and filter by IDs
    all_runs = load_runs()
    selected_runs = [r for r in all_runs if r['id'] in run_ids]
    
    if not selected_runs:
        return jsonify({'error': 'No matching runs found'}), 404
    
    comparison = {
        'runs': selected_runs,
        'best_profit': max(selected_runs, key=lambda r: r.get('accumulated_profit', 0)),
        'best_security': min(selected_runs, key=lambda r: r.get('compromised_systems', float('inf'))),
        'best_availability': max(selected_runs, key=lambda r: r.get('systems_availability', 0))
    }
    
    return jsonify(comparison)


@app.route('/api/health')
def api_health():
    """Health check endpoint."""
    sources = get_data_source_info()
    
    # Determine primary data source
    if sources['manual']['available']:
        primary = 'manual'
        status = 'ok'
    elif sources['forio']['available']:
        primary = 'forio'
        status = 'ok'
    else:
        primary = 'mock'
        status = 'warning'
    
    return jsonify({
        'status': status,
        'primary_source': primary,
        'sources': sources,
        'bots': len(board.bots)
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Multi-Agent Dashboard Starting")
    print("=" * 70)
    
    # Check data sources
    sources = get_data_source_info()
    
    print("\n📊 Data Sources:")
    print(f"   Manual: {'✓' if sources['manual']['available'] else '✗'}")
    if sources['manual']['available']:
        print(f"      Files: {', '.join(sources['manual']['files'])}")
        print(f"      Runs: {sources['manual']['count']}")
    
    print(f"   Forio: {'✓' if sources['forio']['available'] else '✗'}")
    if sources['forio']['configured']:
        print(f"      Configured: ✓")
        print(f"      Authenticated: {'✓' if sources['forio']['authenticated'] else '✗'}")
    
    print(f"   Mock: ✓")
    
    # Determine what will be used
    if sources['manual']['available']:
        print("\n✓ Using manual data")
    elif sources['forio']['available']:
        print("\n✓ Using Forio data")
    else:
        print("\n⚠️  Using mock data (no real data available)")
        print("   To add real data:")
        print("   1. Run: python scripts/manual_data_entry.py")
        print("   2. Or configure Forio credentials in .env")
    
    print(f"\n🤖 Loaded {len(board.bots)} agents")
    for bot in board.bots:
        print(f"   • {bot.name}: {bot.kpi_focus}")
    
    print("\n🌐 Dashboard URL: http://localhost:5000")
    print("=" * 70)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)