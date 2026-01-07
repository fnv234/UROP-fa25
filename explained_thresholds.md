# Threshold Setting Explanation

## Overview

The multi-agent framework uses **threshold-based evaluation** where each executive agent has specific target values (thresholds) for their key performance indicators (KPIs). These thresholds determine whether a simulation result is acceptable, needs improvement, or exceeds expectations.

## How Thresholds Work

### Threshold Types

1. **Minimum Thresholds (Min)**: For KPIs that should be maximized
   - Example: CFO wants `accumulated_profit ≥ $1,200,000`
   - If profit is below threshold → "below target" → needs improvement
   - If profit is at or above threshold → "on target" or "above target" → acceptable

2. **Maximum Thresholds (Max)**: For KPIs that should be minimized
   - Example: CRO wants `compromised_systems ≤ 10`
   - If compromised systems exceed threshold → "above target" → needs improvement
   - If compromised systems are at or below threshold → "on target" or "below target" → acceptable

### Current Agent Thresholds

| Agent | KPI | Threshold Type | Value | Rationale |
|-------|-----|----------------|-------|-----------|
| **CFO** | Accumulated Profit | Min | $1,200,000 | Ensures profitability targets are met |
| **CRO** | Compromised Systems | Max | 10 systems | Limits acceptable security risk exposure |
| **COO** | Systems Availability | Min | 0.92 (92%) | Maintains operational continuity |
| **IT Manager** | Systems at Risk | Max | 10 systems | Controls vulnerability exposure |
| **CHRO** | Fraction to Make Profits | Min | 0.6 (60%) | Ensures sufficient resources for profit generation |
| **COO-Business** | Impact on Business | Max | 5 | Minimizes business disruption |

## Threshold Setting Methodology

### Step 1: Data Collection
Run multiple simulation strategies and collect KPI values:
- Generate 10+ different budget allocation strategies (F1-F4 combinations)
- Execute simulations and record outputs
- Build dataset of KPI distributions

### Step 2: Statistical Analysis
Calculate distribution statistics:
```python
mean = np.mean(kpi_values)
std_dev = np.std(kpi_values)
percentile_70 = np.percentile(kpi_values, 70)
percentile_30 = np.percentile(kpi_values, 30)
```

### Step 3: Threshold Calibration

**For Maximize KPIs (Profit, Availability):**
```
Threshold = Mean + k × Standard Deviation
where k = 0.3 to 0.5 (depending on ambition level)
```

**For Minimize KPIs (Compromised Systems, Risk):**
```
Threshold = Mean - k × Standard Deviation
where k = 0.5 (ensures most runs are acceptable)
```

**Example - CFO Threshold:**
- Mean profit: $1,500,000
- Standard deviation: $200,000
- Target: Mean + 0.5×σ = $1,500,000 + $100,000 = **$1,600,000**
- But we set it at **$1,200,000** (more achievable, based on organizational goals)

### Step 4: Domain Knowledge Integration
Adjust thresholds based on:
- Industry benchmarks
- Regulatory requirements
- Organizational risk appetite
- Historical performance
- Strategic objectives

## Threshold Evaluation Process

### Agent Evaluation Algorithm

```python
def evaluate(results, agent):
    kpi_value = results[agent.kpi_focus]
    
    if agent.target_type == "min":
        if kpi_value < agent.target:
            status = "below target"  # Needs improvement
        else:
            status = "on target" or "above target"  # Acceptable
    
    elif agent.target_type == "max":
        if kpi_value > agent.target:
            status = "above target"  # Needs improvement
        else:
            status = "on target" or "below target"  # Acceptable
    
    return status, recommendation
```

### Example Evaluation

**Scenario**: Simulation result with:
- Accumulated Profit: $1,583,941
- Compromised Systems: 5
- Systems Availability: 0.893

**CFO Evaluation:**
- KPI: $1,583,941
- Target: ≥ $1,200,000
- Status: ✅ **Above target** (exceeds minimum by $383,941)
- Recommendation: "Maintain strategy but explore optimization opportunities"

**CRO Evaluation:**
- KPI: 5 systems
- Target: ≤ 10 systems
- Status: ✅ **Below target** (well within acceptable range)
- Recommendation: "Maintain current strategy"

**COO Evaluation:**
- KPI: 0.893 (89.3%)
- Target: ≥ 0.92 (92%)
- Status: ❌ **Below target** (missing target by 2.7%)
- Recommendation: "Gradual increase recommended to reach target"

## Personality Impact on Thresholds

### Risk Tolerance
- **High Risk Tolerance (>0.7)**: More aggressive thresholds, willing to accept lower performance
- **Low Risk Tolerance (<0.3)**: Conservative thresholds, requires higher performance

### Ambition
- **High Ambition (>0.8)**: Sets challenging thresholds, pushes for excellence
- **Low Ambition (<0.5)**: Sets achievable thresholds, satisfied with meeting minimums

### Example: CFO Personality
- Risk Tolerance: 0.3 (Low - conservative)
- Ambition: 0.8 (High - ambitious)
- Result: Sets high profit threshold ($1.2M) but is cautious about recommendations

## Threshold Sensitivity Analysis

### Impact of Threshold Changes

**Stricter Thresholds (Higher Min, Lower Max):**
- ✅ Fewer strategies meet targets
- ✅ Higher quality standards
- ❌ May eliminate all acceptable strategies
- ❌ Creates tension between agents

**Looser Thresholds (Lower Min, Higher Max):**
- ✅ More strategies meet targets
- ✅ Easier to achieve consensus
- ❌ Lower quality standards
- ❌ May accept suboptimal performance

### Optimal Threshold Setting

The framework helps find the "sweet spot" where:
1. Thresholds are challenging but achievable
2. Multiple strategies can meet targets
3. Agent consensus is possible
4. Performance standards are maintained

## Visualizations Generated

1. **Figure 1**: Shows KPI distributions with threshold positions
2. **Figure 3**: Sensitivity analysis showing impact of threshold changes
3. **Figure 5**: Strategy evaluation showing which strategies meet which thresholds

## Best Practices

1. **Start with Data**: Use statistical analysis of simulation results
2. **Calibrate Gradually**: Adjust thresholds based on evaluation outcomes
3. **Consider Trade-offs**: Balance individual agent goals with overall consensus
4. **Document Rationale**: Explain why each threshold was chosen
5. **Review Periodically**: Update thresholds as organizational goals evolve

## Code Reference

Thresholds are defined in `config/agent_config.json`:
```json
{
  "CFO": {
    "kpi": "accumulated_profit",
    "target": {"min": 1200000}
  },
  "CRO": {
    "kpi": "compromised_systems",
    "target": {"max": 10}
  }
}
```

Threshold calibration logic is in `scripts/calibrate_agents.py`.

