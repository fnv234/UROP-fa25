# Multi-Agent Personality Bot System for Forio Simulations

This project implements a multi-agent system to simulate "personality" bots that evaluate cyber-risk simulation results from Forio Epicenter.

## 🚀 Quick Start

**Run the working demo with mock data:**
```bash
python multi_agent_demo_mock.py
```

This demonstrates the full system with 5 strategies, 3 personality bots, and comparison plots.

**Test your Forio connection:**
```bash
python test_connection.py
```

## Setup

### 1. Environment Variables

Create a `.env` file in the project root with your Forio credentials:

```bash
# API Credentials (for OAuth)
PUBLIC_KEY=your_public_key_here
PRIVATE_KEY=your_private_key_here

# Project Details
FORIO_ORG=mitcams
FORIO_PROJECT=cyberriskmanagement-ransomeware-2023

# Optional: Participant credentials if needed
FORIO_USERNAME=MIT@2025002
FORIO_PASSWORD=your_password_here
```

### 2. Install Dependencies

```bash
pip install requests python-dotenv matplotlib pandas
```

### 3. Understanding the Forio Project Structure

This project uses a **facilitator-based simulation** where:
- Facilitator user: `MIT@2025001` (creates/manages sessions)
- Participant user: `MIT@2025002` (runs simulations)
- Model: Python-based cyber-risk management simulation
- Access: Via web interface at `https://forio.com/app/mitcams/cyberriskmanagement-ransomeware-2023/`

## Usage

### Fetch and Analyze Existing Runs

The main workflow fetches existing saved runs and has personality bots evaluate them:

```bash
python multi_agent_demo.py
```

This will:
1. Authenticate with Forio OAuth
2. Fetch recent saved simulation runs
3. Have executive bots (CFO, CRO, COO) evaluate each run based on their KPI focus
4. Generate comparison plots

### Key Components

#### `ForioDataFetcher`
- Handles OAuth authentication
- Fetches existing saved runs from the Forio project
- Supports filtering by group and including specific variables

#### `ExecutiveBot`
- Represents an executive with a specific KPI focus
- Has personality traits (risk_tolerance, friendliness, ambition)
- Evaluates simulation results based on targets and personality

#### `BoardRoom`
- Manages a collection of bots
- Simulates board meetings where bots discuss results
- Can model different interaction dynamics (collaborative, hostile, neutral)

### Example: Creating Custom Bots

```python
from multi_agent_demo import ExecutiveBot, BoardRoom

# Create bots with different personalities
aggressive_cfo = ExecutiveBot(
    "CFO", 
    "accumulated_profit",
    target={"min": 2000000},
    personality={"risk_tolerance": 0.9, "friendliness": 0.3, "ambition": 0.95}
)

conservative_cro = ExecutiveBot(
    "CRO",
    "compromised_systems",
    target={"max": 5},
    personality={"risk_tolerance": 0.1, "friendliness": 0.8, "ambition": 0.4}
)

board = BoardRoom([aggressive_cfo, conservative_cro])
```

## KPIs Available

Common KPIs from the cyber-risk simulation:
- `accumulated_profit`: Total profit over simulation period
- `compromised_systems`: Number of systems compromised by attacks
- `systems_availability`: Percentage of systems available
- `prevention_budget`: Budget allocated to prevention
- `detection_budget`: Budget allocated to detection
- `response_budget`: Budget allocated to incident response

## Plotting and Analysis

The system generates:
- Bar charts comparing KPIs across multiple runs
- Saved to `kpi_comparison.png`
- Can be extended to show personality-driven decision patterns

## Files

- `multi_agent_demo.py`: Main demo script (works with existing runs)
- `multi-agent_setup.py`: Original setup (for direct API run creation - not supported by facilitator projects)
- `data_extractor_example.py`: Reference implementation for fetching Forio data
- `status_test.py`: OAuth and API connectivity test
- `model_test.py`: Model listing test

## Troubleshooting

### No runs found
Run the simulation through the Forio web interface first:
1. Visit `https://forio.com/app/mitcams/cyberriskmanagement-ransomeware-2023/`
2. Log in as facilitator (`MIT@2025001`) or participant (`MIT@2025002`)
3. Complete at least one simulation run
4. Make sure to **save** the run

### Authentication errors
- Verify `PUBLIC_KEY` and `PRIVATE_KEY` in `.env`
- Check that keys have access to the project

### Model file errors
Facilitator projects don't support creating new runs via API. Use `multi_agent_demo.py` to analyze existing runs instead.

## Future Enhancements

- [ ] Add LLM-based personality simulation for richer bot interactions
- [ ] Implement negotiation protocols between bots
- [ ] Add strategy optimization based on bot feedback
- [ ] Export results to CSV for further analysis
- [ ] Create time-series plots showing KPI evolution
- [ ] Add Monte Carlo simulation of bot decision-making
