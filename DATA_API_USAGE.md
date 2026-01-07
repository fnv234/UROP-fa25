# Forio Data API Integration Guide

## Overview

The codebase now includes integration with Forio's Data API, which allows you to store and retrieve simulation results in a structured collection format. This is particularly useful for:

- Storing simulation results with F1-F4 inputs and all outputs
- Querying and searching results
- Sharing results across team members
- Building dashboards and analytics

## Setup

### 1. Environment Variables

Ensure your `.env` file contains:

```env
PUBLIC_KEY=your_public_key_here
PRIVATE_KEY=your_private_key_here
FORIO_ORG=mitcams
FORIO_PROJECT=cyberriskmanagement-ransomeware-2023
DATA_COLLECTION=simulation-results  # Optional, defaults to "simulation-results"
```

### 2. Collection Name

The Data API stores data in collections. By default, the code uses `simulation-results` as the collection name. You can override this by setting `DATA_COLLECTION` in your `.env` file.

## Usage

### Basic Usage

```python
from data.forio_data_api import ForioDataAPI

# Initialize the API client
api = ForioDataAPI()

# Save a simulation result
result = {
    "F1": 30,
    "F2": 30,
    "F3": 25,
    "F4": 15,
    "accumulated_profit": 1500000,
    "compromised_systems": 8,
    "systems_availability": 0.94,
    "systems_at_risk": 12,
    "fraction_to_make_profits": 0.75,
    "impact_on_business": 3.5,
    "strategy_name": "Balanced"
}

# Save with auto-generated ID
saved = api.save_simulation_result(result)

# Save with specific ID
saved = api.save_simulation_result(result, document_id="my-run-123")
```

### Using SimulationRunner

The `SimulationRunner` class now automatically saves to Data API:

```python
from simulation_runner import SimulationRunner

runner = SimulationRunner()

# Run strategies - results are automatically saved to Data API
strategies = [
    {'F1': 30, 'F2': 30, 'F3': 25, 'F4': 15, 'name': 'Balanced'},
    {'F1': 50, 'F2': 25, 'F3': 15, 'F4': 10, 'name': 'Prevention-Heavy'},
]

results = runner.run_strategy_batch(strategies)
runner.save_results(results, use_data_api=True)  # Saves to both Data API and local file
```

### Retrieving Results

```python
from data.forio_data_api import ForioDataAPI

api = ForioDataAPI()

# Get all results (sorted by lastModified, descending)
all_results = api.get_all_results(limit=10)

# Get a specific result
result = api.get_simulation_result("document-id-here")

# Search for results
# Find all with F1 >= 30
results = api.search_results({"F1": {"$gte": 30}})

# Find all with accumulated_profit > 1000000
results = api.search_results({"accumulated_profit": {"$gt": 1000000}})

# Complex search with logical operators
results = api.search_results({
    "$and": [
        {"F1": {"$gte": 30}},
        {"compromised_systems": {"$lt": 10}}
    ]
})
```

### Using with Manual Data Entry

When using `scripts/manual_data_entry.py`, you'll be prompted to optionally save to Data API after entering the data.

## Data Structure

Each document in the collection should include:

### Inputs (F1-F4)
- `F1`: Prevention budget (%)
- `F2`: Detection budget (%)
- `F3`: Response budget (%)
- `F4`: Recovery budget (%)
- `prevention_budget`, `detection_budget`, `response_budget`, `recovery_budget` (for compatibility)

### Main Outputs
- `accumulated_profit`: Total profits over simulation period
- `profits`: Current period profits
- `compromised_systems`: Number of compromised systems
- `systems_availability`: Systems availability (0-1)

### Additional Outputs
- `systems_at_risk`: Systems with vulnerabilities
- `fraction_to_make_profits`: Fraction of resources for profit generation
- `impact_on_business`: Business disturbance metric

### Metadata
- `strategy_name`: Name of the strategy
- `timestamp`: When the simulation was run
- `id`: Document ID (auto-generated or specified)
- `lastModified`: Last modification time (auto-added by Data API)

## Search Examples

### Exact Match
```python
# Find results with F1 = 30
results = api.search_results({"F1": 30})
```

### Comparison Operators
```python
# Greater than
results = api.search_results({"accumulated_profit": {"$gt": 1000000}})

# Less than or equal
results = api.search_results({"compromised_systems": {"$lte": 10}})

# Not equal
results = api.search_results({"strategy_name": {"$ne": "Balanced"}})

# In array
results = api.search_results({"F1": {"$in": [30, 40, 50]}})
```

### Logical Operators
```python
# AND - both conditions must be true
results = api.search_results({
    "$and": [
        {"F1": {"$gte": 30}},
        {"compromised_systems": {"$lt": 10}}
    ]
})

# OR - either condition can be true
results = api.search_results({
    "$or": [
        {"F1": {"$gte": 50}},
        {"F2": {"$gte": 50}}
    ]
})
```

### Sorting
```python
# Get results sorted by accumulated_profit, descending
results = api.get_all_results(sort_by="accumulated_profit", direction="desc", limit=10)

# Get results sorted by F1, ascending
results = api.get_all_results(sort_by="F1", direction="asc", limit=10)
```

## Batch Operations

### Save Multiple Results
```python
results = [
    {"id": "run1", "F1": 30, "F2": 30, "F3": 25, "F4": 15, ...},
    {"id": "run2", "F1": 50, "F2": 25, "F3": 15, "F4": 10, ...},
]

saved = api.save_batch_results(results)
```

## Error Handling

The Data API client includes error handling:

- Returns `None` if authentication fails
- Returns empty list `[]` if no results found
- Prints error messages for debugging
- Falls back to local file storage if Data API is not configured

## Testing

Test the Data API connection:

```bash
python data/forio_data_api.py
```

This will:
1. Test authentication
2. Save a sample result
3. Retrieve the saved result
4. Test search functionality
5. Test get all functionality

## Integration with Existing Code

The Data API integration is backward compatible:

- `SimulationRunner` saves to both Data API and local files
- `manual_data_entry.py` optionally saves to Data API
- Existing code using local JSON files continues to work
- Data can be loaded from either source

## Best Practices

1. **Use consistent document IDs**: Use run IDs from Forio runs as document IDs for easy tracking
2. **Include all fields**: Save complete data including inputs and all outputs
3. **Use strategy names**: Include descriptive strategy names for easier searching
4. **Regular backups**: Data API is the primary storage, but local files serve as backups
5. **Search efficiently**: Use specific queries rather than retrieving all results

## Troubleshooting

### Authentication Errors
- Check that `PUBLIC_KEY` and `PRIVATE_KEY` are set correctly in `.env`
- Verify credentials at https://forio.com/

### Collection Not Found
- Collections are created automatically on first POST
- Ensure project name is correct in `.env`

### Search Not Working
- Check query syntax matches MongoDB query format
- Use quotes for string values in queries
- Verify field names match exactly (case-sensitive)

### Rate Limiting
- Data API has rate limits
- Use batch operations when saving multiple results
- Add delays between requests if needed

