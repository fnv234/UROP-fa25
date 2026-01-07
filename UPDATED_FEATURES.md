# Updated Features: F1-F4 Inputs and Additional Outputs

## Overview

The codebase has been updated to support the complete simulation interface with:

### Inputs (F1-F4)
- **F1**: Prevention budget (% of IT budget)
- **F2**: Detection budget (% of IT budget)
- **F3**: Response budget (% of IT budget)
- **F4**: Recovery budget (% of IT budget)

### Main Outputs
- **Compromised systems**: Number of systems compromised by attacks
- **Profits**: Current period profits
- **Accumulated Profits**: Total profits over simulation period

### Additional Outputs (for advanced settings)
- **Systems at risk**: Systems that contain vulnerabilities and may show less performance
- **Fraction to make profits**: Fraction of resources available to generate profit (overshoot of security investments affects this)
- **Impact on business**: Business disturbance caused by adverse events

## Updated Files

### 1. `forio_config.json`
- Added `recovery_budget` to budgets
- Added `additional_outputs` section with new KPIs
- Added `input_mapping` to map F1-F4 to descriptive names

### 2. `scripts/manual_data_entry.py`
- Updated to collect F1-F4 inputs
- Added prompts for additional outputs
- Maintains backward compatibility with descriptive names

### 3. `data/forio_client.py`
- Updated to fetch and flatten F4 (recovery_budget)
- Added support for additional output variables
- Maps F1-F4 from variables automatically

### 4. `data/data_loader.py`
- Updated `generate_mock_runs()` to include F1-F4
- Generates realistic mock data for all new outputs
- Ensures F1-F4 sum to 100%

### 5. `config/agent_config.json`
- Added optional agents for additional outputs:
  - **IT_Manager**: Focuses on `systems_at_risk`
  - **CHRO**: Focuses on `fraction_to_make_profits`
  - **COO_Business**: Focuses on `impact_on_business`

### 6. `automated_simulation_runner.py`
- Updated to support F1-F4 inputs
- Enhanced result extraction to include all new outputs
- Updated strategy examples to use F1-F4 format

### 7. `simulation_runner.py` (NEW)
- New script for programmatic simulation runs
- Supports F1-F4 budget allocation
- Fetches complete results including additional outputs

## Usage Examples

### Manual Data Entry

```bash
python scripts/manual_data_entry.py
```

This will prompt for:
- F1-F4 budget allocations
- Main outputs (compromised systems, profits, accumulated profits)
- Additional outputs (systems at risk, fraction to make profits, impact on business)

### Automated Simulation Runner

```bash
python automated_simulation_runner.py
```

Define strategies with F1-F4:
```python
strategies = [
    {'F1': 30, 'F2': 30, 'F3': 25, 'F4': 15, 'name': 'Balanced'},
    {'F1': 50, 'F2': 25, 'F3': 15, 'F4': 10, 'name': 'Prevention-Heavy'},
]
```

### Using Mock Data

```python
from data.data_loader import load_runs

# Load mock runs with F1-F4 and all outputs
runs = load_runs(prefer_source='mock', limit=5)

for run in runs:
    print(f"F1={run['F1']}%, F2={run['F2']}%, F3={run['F3']}%, F4={run['F4']}%")
    print(f"Accumulated Profit: ${run['accumulated_profit']:,.0f}")
    print(f"Compromised Systems: {run['compromised_systems']}")
    print(f"Systems at Risk: {run['systems_at_risk']}")
    print(f"Fraction to Make Profits: {run['fraction_to_make_profits']:.2f}")
    print(f"Impact on Business: {run['impact_on_business']}")
```

### Agent Configuration

The agent system now supports additional executives:

```json
{
  "IT_Manager": {
    "kpi": "systems_at_risk",
    "target": {"max": 10}
  },
  "CHRO": {
    "kpi": "fraction_to_make_profits",
    "target": {"min": 0.6}
  },
  "COO_Business": {
    "kpi": "impact_on_business",
    "target": {"max": 5}
  }
}
```

## Environment Variables

Create a `.env` file with:

```env
PUBLIC_KEY=your_public_key_here
PRIVATE_KEY=your_private_key_here
FORIO_ORG=mitcams
FORIO_PROJECT=cyberriskmanagement-ransomeware-2023
FORIO_USERNAME=MIT@2025002
FORIO_PASSWORD=your_password_here
```

## Data Structure

Each simulation run now includes:

```json
{
  "id": "run_123",
  "F1": 30,
  "F2": 30,
  "F3": 25,
  "F4": 15,
  "prevention_budget": 30,
  "detection_budget": 30,
  "response_budget": 25,
  "recovery_budget": 15,
  "accumulated_profit": 1500000,
  "profits": 1200000,
  "compromised_systems": 8,
  "systems_availability": 0.94,
  "systems_at_risk": 12,
  "fraction_to_make_profits": 0.75,
  "impact_on_business": 3.5
}
```

## Next Steps

1. **Configure .env file** with your Forio credentials
2. **Test connection**: `python data/forio_client.py`
3. **Enter data manually** or use automated runner
4. **Run analysis**: `python multi_agent_demo.py`
5. **View dashboard**: `python dashboard.py`

## Notes

- F1-F4 should sum to approximately 100% (representing total IT budget allocation)
- The system maintains backward compatibility with legacy parameter names
- Additional outputs are optional and may not be available in all simulation runs
- For facilitator projects, direct API run creation may not be supported - use web interface or Selenium automation

