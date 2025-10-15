# Solution Summary: Multi-Agent Personality Bot System

## Problem Statement

You wanted to:
1. Extract data from Forio cyber-risk simulations
2. Develop a multi-agent system with "personality" bots
3. Compare and contrast strategies of different agents
4. Produce plots visualizing the results

## Root Cause of Original Issues

The original `multi-agent_setup.py` failed because:

1. **Wrong API endpoint pattern**: Used facilitator HTML URL instead of REST API endpoints
2. **Wrong authentication**: Used custom headers instead of OAuth Bearer tokens
3. **Wrong project type assumption**: Tried to CREATE new runs programmatically, but your project is a **facilitator-based simulation** that doesn't support API-based run creation
4. **Model file confusion**: The project doesn't expose model files via API

## Solution Architecture

### Working Approach: Fetch & Analyze Existing Runs

Since the Forio project is facilitator-based, the solution:
1. ✅ Uses OAuth to authenticate (`https://api.forio.com/v2/oauth/token`)
2. ✅ Fetches existing saved runs (`https://forio.com/v2/run/{org}/{project}/`)
3. ✅ Has personality bots evaluate the results
4. ✅ Generates comparison plots

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `multi_agent_demo.py` | **Main working demo** - fetches & analyzes runs | ✅ Ready to use |
| `multi-agent_setup.py` | Original attempt to create runs via API | ⚠️ Won't work (facilitator project) |
| `data_extractor_example.py` | Reference implementation (Annette Chau's code) | ℹ️ Reference only |
| `status_test.py` | OAuth connectivity test | ✅ Working |
| `README.md` | Setup and usage instructions | ✅ Complete |

## How to Use

### 1. Setup Environment

Create `.env` file:
```bash
PUBLIC_KEY=your_key_here
PRIVATE_KEY=your_secret_here
FORIO_ORG=mitcams
FORIO_PROJECT=cyberriskmanagement-ransomeware-2023
```

### 2. Run Simulations (Web Interface)

Before analyzing, you need saved runs:
1. Visit: `https://forio.com/app/mitcams/cyberriskmanagement-ransomeware-2023/`
2. Login as: `MIT@2025002` (participant) or `MIT@2025001` (facilitator)
3. Complete simulation runs
4. **Important**: Save the runs

### 3. Analyze with Personality Bots

```bash
python multi_agent_demo.py
```

This will:
- Fetch your saved runs
- Have 3 executive bots (CFO, CRO, COO) evaluate each run
- Generate KPI comparison plots
- Save results to `kpi_comparison.png`

## Multi-Agent System Design

### ExecutiveBot Class

Each bot has:
- **KPI Focus**: Which metric they care about (e.g., `accumulated_profit`)
- **Targets**: Min/max acceptable values
- **Personality Traits**:
  - `risk_tolerance` (0.0-1.0): Willingness to take risks
  - `friendliness` (0.0-1.0): Collaborative vs. competitive
  - `ambition` (0.0-1.0): Drive for improvement

Example:
```python
aggressive_cfo = ExecutiveBot(
    "CFO", 
    "accumulated_profit",
    target={"min": 2000000},
    personality={
        "risk_tolerance": 0.9,  # High risk tolerance
        "friendliness": 0.3,     # Competitive
        "ambition": 0.95         # Very ambitious
    }
)
```

### BoardRoom Class

Simulates meetings where bots:
- Evaluate simulation results
- Provide feedback based on their personality
- Interact with different dynamics (collaborative/hostile/neutral)

## Available KPIs

From the cyber-risk simulation:
- `accumulated_profit`: Total profit
- `compromised_systems`: Number of breached systems
- `systems_availability`: System uptime percentage
- `prevention_budget`: Prevention spending
- `detection_budget`: Detection spending
- `response_budget`: Incident response spending

## Plotting Capabilities

The system generates:
- **Bar charts**: Compare KPIs across multiple runs
- **Side-by-side comparison**: See how different strategies perform
- **Extensible**: Easy to add time-series, scatter plots, etc.

## Strategy Comparison Example

```python
# Fetch runs with different strategies
runs = fetcher.fetch_runs(include_vars=kpis, limit=10)

# Have bots evaluate each strategy
for run in runs:
    feedback = board.run_meeting(run)
    # Bots provide personality-driven commentary

# Plot comparison
plot_kpis_comparison(runs, kpis, labels=["Strategy A", "Strategy B", ...])
```

## Future Enhancements

### Short-term (Easy to Add)
1. **CSV Export**: Save bot evaluations and KPIs to CSV
2. **More KPIs**: Add additional metrics from the simulation
3. **Personality Variations**: Create more bot archetypes
4. **Time-series Plots**: Show KPI evolution over simulation time

### Medium-term (Moderate Effort)
1. **Strategy Optimization**: Use bot feedback to suggest better strategies
2. **Monte Carlo Simulation**: Run multiple bot personalities and aggregate results
3. **Negotiation Protocols**: Have bots negotiate and reach consensus
4. **Group Analysis**: Compare runs by participant group

### Long-term (Advanced)
1. **LLM Integration**: Use GPT-4 for richer personality simulation
2. **Reinforcement Learning**: Train bots to optimize strategies
3. **Real-time Analysis**: Connect to live simulation sessions
4. **Multi-simulation Comparison**: Compare across different Forio projects

## Technical Notes

### Why Facilitator Projects Are Different

Facilitator-based Forio projects:
- ❌ Don't support `POST /v2/model/run/` (create new runs via API)
- ✅ Support `GET /v2/run/{org}/{project}/` (fetch existing runs)
- ✅ Support web-based facilitated sessions
- ✅ Support participant/facilitator user roles

### Authentication Flow

1. **OAuth Token Request**:
   ```
   POST https://api.forio.com/v2/oauth/token
   Authorization: Basic {base64(public_key:private_key)}
   Content-Type: application/x-www-form-urlencoded
   Body: grant_type=client_credentials
   ```

2. **Fetch Runs**:
   ```
   GET https://forio.com/v2/run/{org}/{project}/;saved=true
   Authorization: Bearer {access_token}
   ```

### Data Structure

Runs returned from Forio contain:
```json
{
  "id": "00000199e7211460...",
  "account": "mitcams",
  "project": "cyberriskmanagement-ransomeware-2023",
  "created": "2025-10-15T...",
  "saved": true,
  "variables": {
    "accumulated_profit": 1500000,
    "compromised_systems": 8,
    "systems_availability": 0.96
  }
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No saved runs found" | Run simulations via web interface and save them |
| "OAuth error 401" | Check PUBLIC_KEY and PRIVATE_KEY in .env |
| "Project not found" | Verify FORIO_ORG and FORIO_PROJECT spelling |
| "Missing model" error | Don't use multi-agent_setup.py; use multi_agent_demo.py |
| Plots not showing | Install matplotlib: `pip install matplotlib` |

## Contact & Support

- Forio Documentation: https://forio.com/epicenter/docs/
- Project URL: https://forio.com/app/mitcams/cyberriskmanagement-ransomeware-2023/
- Facilitator: MIT@2025001
- Participant: MIT@2025002
