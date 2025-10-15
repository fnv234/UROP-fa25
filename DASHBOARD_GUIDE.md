# 🎨 Web Dashboard Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
python dashboard.py
```

### 3. Open in Browser
Navigate to: **http://localhost:5000**

---

## Features

### 🤖 Bot Personality Cards
- View all 3 executive bots (CFO, CRO, COO)
- See their KPI focus and personality traits
- Visual progress bars for risk tolerance and ambition

### 📊 Recent Runs List
- Browse recent simulation runs
- Click any run to analyze it
- Shows budget allocation preview

### 📈 KPI Comparison Chart
- Bar chart comparing profit and compromised systems
- Updates automatically when runs are loaded
- Color-coded for easy interpretation

### 💬 Board Meeting Analysis
- Click a run to see bot evaluations
- Personality-driven feedback from each bot
- Strategic recommendations
- Board dynamics summary

### 🎯 Strategy Comparison
- Stacked bar chart showing budget allocation
- Compare prevention, detection, and response spending
- Identify optimal strategies

### 🔌 Forio Connection Status
- Real-time connection indicator in header
- Shows number of available runs
- Auto-refreshes every 30 seconds

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  🤖 Multi-Agent Dashboard      [Connection Status]      │
└─────────────────────────────────────────────────────────┘

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  CFO Bot     │ │  CRO Bot     │ │  COO Bot     │
│  Card        │ │  Card        │ │  Card        │
└──────────────┘ └──────────────┘ └──────────────┘

┌──────────────┐ ┌─────────────────────────────────────┐
│              │ │  KPI Comparison Chart               │
│  Recent      │ │                                     │
│  Runs        │ └─────────────────────────────────────┘
│  List        │ ┌─────────────────────────────────────┐
│              │ │  Board Meeting Analysis             │
│              │ │  • Bot Evaluations                  │
│              │ │  • Recommendations                  │
└──────────────┘ └─────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Strategy Comparison (Budget Allocation)                │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

The dashboard provides a REST API:

### `GET /api/runs`
Returns list of simulation runs (mock data currently)

**Response:**
```json
[
  {
    "id": "mock_run_1",
    "strategy": "Strategy A",
    "prevention_budget": 56,
    "detection_budget": 37,
    "response_budget": 20,
    "accumulated_profit": 1651901,
    "compromised_systems": 6,
    "systems_availability": 0.98
  }
]
```

### `POST /api/evaluate`
Evaluate a run with personality bots

**Request:**
```json
{
  "run": {
    "accumulated_profit": 1500000,
    "compromised_systems": 8,
    "systems_availability": 0.95
  }
}
```

**Response:**
```json
{
  "feedback": [
    "CFO sees accumulated_profit=1,500,000, status=on target",
    "CRO sees compromised_systems=8, status=on target",
    "COO sees systems_availability=0.95, status=on target"
  ],
  "recommendations": [
    "CFO: Maintain current strategy",
    "CRO: Maintain current strategy",
    "COO: Maintain current strategy"
  ],
  "interaction": "Bots align toward compromise and shared strategy."
}
```

### `GET /api/bots`
Get bot configuration

**Response:**
```json
[
  {
    "name": "CFO",
    "kpi_focus": "accumulated_profit",
    "target": {"min": 1200000},
    "personality": {
      "risk_tolerance": 0.3,
      "friendliness": 0.6,
      "ambition": 0.8
    }
  }
]
```

### `GET /api/forio/status`
Check Forio API connection

**Response:**
```json
{
  "connected": true,
  "runs_available": true,
  "run_count": 6,
  "note": "Variables not recorded in Vensim model"
}
```

---

## Customization

### Adding New Bots

Edit `dashboard.py`:

```python
new_bot = ExecutiveBot(
    "CTO",
    "system_performance",
    target={"min": 0.95},
    personality={"risk_tolerance": 0.7, "friendliness": 0.8, "ambition": 0.9}
)

board = BoardRoom([cfo, cro, coo, new_bot])
```

### Changing Port

```python
app.run(debug=True, port=8080)  # Change from 5000 to 8080
```

### Adding Custom KPIs

Modify `generate_mock_runs()` in `multi_agent_demo_mock.py` to include new metrics.

---

## Using Real Forio Data

### Current Status
- ✅ OAuth authentication working
- ✅ Can fetch run metadata (ID, user, timestamp, group)
- ❌ Variables not recorded (Vensim model configuration needed)

### To Enable Real Data

1. **Configure Vensim Model** to save variables:
   - Add variables to model export configuration
   - Or use Forio facilitator interface to configure saved variables

2. **Update Dashboard** once variables are available:
   ```python
   # In dashboard.py, modify fetch_forio_runs():
   def fetch_forio_runs(limit=10):
       # ... existing code ...
       
       # Fetch variables for each run
       for run in runs:
           var_url = f"https://api.forio.com/v2/model/run/{run['id']}/variables"
           var_resp = requests.get(var_url, headers=headers)
           if var_resp.status_code == 200:
               run['variables'] = var_resp.json()
       
       return runs
   ```

3. **Remove mock data fallback** in `/api/runs` endpoint

---

## Troubleshooting

### Dashboard won't start
```bash
# Install Flask
pip install flask

# Check if port 5000 is in use
lsof -i :5000

# Use different port
python dashboard.py  # Edit file to change port
```

### Charts not showing
- Check browser console for JavaScript errors
- Ensure Chart.js CDN is accessible
- Try refreshing the page

### No runs displayed
- Check Forio connection status in header
- Verify `.env` file has correct credentials
- Check browser console for API errors

### Styling issues
- Ensure Tailwind CSS CDN is accessible
- Check browser console for CSS loading errors
- Try hard refresh (Cmd+Shift+R / Ctrl+Shift+F5)

---

## Development Mode

Flask runs in debug mode by default, which provides:
- Auto-reload on code changes
- Detailed error pages
- Interactive debugger

To disable debug mode for production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## Next Steps

### Phase 1: Enhanced UI
- [ ] Add dark mode toggle
- [ ] Export analysis to PDF
- [ ] Save favorite strategies
- [ ] Historical comparison view

### Phase 2: Real-time Features
- [ ] WebSocket for live updates
- [ ] Real-time bot negotiations
- [ ] Collaborative analysis sessions
- [ ] Chat interface with bots

### Phase 3: Advanced Analytics
- [ ] Machine learning predictions
- [ ] Strategy optimization engine
- [ ] Monte Carlo simulations
- [ ] Risk assessment dashboard

---

## Screenshots

### Main Dashboard
- Bot personality cards at top
- Runs list on left
- Analysis panels on right
- Charts below

### Board Meeting Analysis
- Selected run details
- Bot evaluations with personality commentary
- Strategic recommendations
- Board dynamics summary

### Strategy Comparison
- Stacked bar chart of budget allocation
- Color-coded by category
- Interactive tooltips

---

## Support

- **Documentation**: See README.md
- **API Reference**: This file
- **Issues**: Check browser console for errors
- **Forio Docs**: https://forio.com/epicenter/docs/

---

**Dashboard Status**: ✅ Ready to use with mock data  
**Real Data**: ⚠️ Requires Vensim model configuration
