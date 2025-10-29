"""
Test the enhanced Forio data extraction with variable specification.
This script demonstrates the key improvements from fde.py applied to your project.
"""

import json
from forio_data_extractor import ForioDataExtractor

print("=" * 70)
print("🧪 TESTING ENHANCED FORIO DATA EXTRACTION")
print("=" * 70)

# Initialize extractor
print("\n1️⃣ Initializing extractor...")
extractor = ForioDataExtractor()

# Test connection
print("\n2️⃣ Testing connection...")
status = extractor.test_connection()
print(f"   ✅ Authenticated: {status['authenticated']}")
print(f"   📊 Runs found: {status['runs_found']}")
print(f"   📝 Variables recorded: {status['variables_recorded']}")

if status['sample_run']:
    print(f"   🆔 Sample run: {status['sample_run']['id']}")
    if status['sample_run']['variables']:
        print(f"   📋 Variables: {status['sample_run']['variables']}")
    else:
        print(f"   ⚠️  No variables in sample run")

# Load configuration
print("\n3️⃣ Loading configuration...")
try:
    with open('forio_config.json', 'r') as f:
        config = json.load(f)
    print(f"   ✅ Config loaded")
    print(f"   📋 KPI variables: {config['variables']['kpis']}")
    print(f"   💰 Budget variables: {config['variables']['budgets']}")
    print(f"   👥 Groups: {config.get('groups', ['all'])}")
except Exception as e:
    print(f"   ⚠️  Could not load config: {e}")
    config = {
        'variables': {
            'kpis': ['accumulated_profit', 'compromised_systems', 'systems_availability'],
            'budgets': ['prevention_budget', 'detection_budget', 'response_budget']
        },
        'groups': None,
        'model_name': None
    }

# Combine all variables
all_variables = []
all_variables.extend(config['variables'].get('kpis', []))
all_variables.extend(config['variables'].get('budgets', []))
all_variables.extend(config['variables'].get('additional', []))

print(f"\n4️⃣ Attempting enhanced extraction...")
print(f"   🎯 Target variables ({len(all_variables)}): {all_variables}")
print(f"   👥 Groups: {config.get('groups', 'all')}")
print(f"   📦 Model: {config.get('model_name', 'auto-detect')}")

try:
    # Fetch runs with variables using the fde.py approach
    runs = extractor.fetch_runs_with_variables(
        variables=all_variables,
        model_name=config.get('model_name'),
        groups=config.get('groups'),
        start_record=0,
        end_record=10
    )
    
    print(f"   ✅ Fetched {len(runs)} runs")
    
    if runs:
        # Check first run for variables
        sample = runs[0]
        print(f"\n5️⃣ Analyzing sample run...")
        print(f"   🆔 Run ID: {sample.get('id')}")
        print(f"   📅 Created: {sample.get('created')}")
        print(f"   👤 User: {sample.get('user', {}).get('userName', 'Unknown')}")
        
        # Check if variables are present
        has_variables = bool(sample.get('variables'))
        print(f"   📊 Has variables: {has_variables}")
        
        if has_variables:
            print(f"   ✅ SUCCESS! Variables are being extracted!")
            print(f"   📋 Variable keys: {list(sample['variables'].keys())[:10]}")
            
            # Show sample values
            print(f"\n   📈 Sample values:")
            for var in all_variables[:5]:
                value = sample['variables'].get(var)
                if value is not None:
                    print(f"      • {var}: {value}")
            
            # Extract and save
            print(f"\n6️⃣ Extracting data from all runs...")
            extracted = extractor.extract_variables_from_runs(runs, all_variables)
            
            # Save to file
            output_file = 'extracted_simulation_data.json'
            extractor.save_to_json(extracted, output_file)
            
            print(f"\n   ✅ Data extraction complete!")
            print(f"   💾 Saved to: {output_file}")
            print(f"   📊 Total runs: {len(extracted)}")
            
            # Show summary
            print(f"\n7️⃣ Data summary:")
            for i, run in enumerate(extracted[:3]):
                print(f"\n   Run {i+1}:")
                print(f"      ID: {run['id']}")
                print(f"      User: {run['user']}")
                print(f"      Group: {run['group']}")
                for var in ['accumulated_profit', 'compromised_systems', 'systems_availability']:
                    if var in run and run[var] is not None:
                        print(f"      {var}: {run[var]}")
        else:
            print(f"   ⚠️  No variables recorded in runs")
            print(f"\n   💡 This means:")
            print(f"      • The Vensim model is not configured to save variables")
            print(f"      • You need to configure the model to record these variables")
            print(f"      • OR use manual data entry as a workaround")
            print(f"\n   📖 See VARIABLE_RECORDING_ISSUE.md for details")
    else:
        print(f"   ⚠️  No runs returned")
        
except Exception as e:
    print(f"   ❌ Error during extraction: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)

print("\n📝 Next steps:")
print("   1. If variables are present: Great! The enhanced extraction works!")
print("   2. If no variables: Configure Vensim model to save variables")
print("   3. Update forio_config.json with your specific variables")
print("   4. Run the dashboard: python dashboard.py")
print()
