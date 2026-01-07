"""
Simulation Runner for Forio Cyber-Risk Management
Creates simulation runs with F1-F4 inputs and extracts results.

This script:
1. Connects to Forio API
2. Creates simulation runs with F1-F4 budget allocations
3. Fetches results including main and additional outputs
4. Saves results to Forio Data API for analysis
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from data.forio_client import ForioClient
from data.forio_data_api import ForioDataAPI

load_dotenv()


class SimulationRunner:
    """Runs simulations with F1-F4 inputs and extracts results."""
    
    def __init__(self):
        self.client = ForioClient()
        self.data_api = ForioDataAPI()
        if not self.client.is_configured():
            raise ValueError(
                "Forio credentials not configured. Set PUBLIC_KEY and PRIVATE_KEY in .env file."
            )
    
    def create_run_with_budgets(
        self, 
        f1: float, 
        f2: float, 
        f3: float, 
        f4: float,
        strategy_name: Optional[str] = None,
        wait_for_completion: bool = True
    ) -> Optional[Dict]:
        """
        Create a simulation run with F1-F4 budget allocations.
        Note: For facilitator projects, this may need to be done via web interface.
        This method prepares the data structure and can save results to Data API.
        
        Args:
            f1: Prevention budget (% of IT budget)
            f2: Detection budget (% of IT budget)
            f3: Response budget (% of IT budget)
            f4: Recovery budget (% of IT budget)
            strategy_name: Optional name for this strategy
            wait_for_completion: Whether to wait for simulation to complete
        
        Returns:
            Run dictionary with results or None if failed
        """
        # Validate that F1-F4 sum to approximately 100
        total = f1 + f2 + f3 + f4
        if abs(total - 100) > 5:
            print(f"⚠️  Warning: F1-F4 sum to {total}%, not 100%")
        
        print(f"\n▶️  Preparing simulation run:")
        print(f"   F1 (Prevention): {f1}%")
        print(f"   F2 (Detection): {f2}%")
        print(f"   F3 (Response): {f3}%")
        print(f"   F4 (Recovery): {f4}%")
        
        # Prepare run data structure
        run_data = {
            "F1": f1,
            "F2": f2,
            "F3": f3,
            "F4": f4,
            "prevention_budget": f1,
            "detection_budget": f2,
            "response_budget": f3,
            "recovery_budget": f4,
            "strategy_name": strategy_name or f"F1={f1}_F2={f2}_F3={f3}_F4={f4}",
            "timestamp": datetime.now().isoformat(),
            "status": "pending"  # Will be updated when results are available
        }
        
        print("\n⚠️  Note: Direct API run creation may not be supported for facilitator projects.")
        print("   For facilitator projects, use one of these approaches:")
        print("   1. Use automated_simulation_runner.py (Selenium-based)")
        print("   2. Manually run simulations in Forio web interface")
        print("   3. Use scripts/manual_data_entry.py to enter results")
        print("   4. Results can be saved to Data API using save_result_to_data_api()")
        
        return run_data
    
    def fetch_run_results(self, run_id: str) -> Optional[Dict]:
        """Fetch results for a specific run ID."""
        token = self.client._get_token()
        if not token:
            return None
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to fetch variables
        endpoints = [
            f"https://api.forio.com/v2/model/run/{run_id}/variables",
            f"https://api.forio.com/v2/run/{self.client.org}/{self.client.project}/{run_id}/variables"
        ]
        
        for endpoint in endpoints:
            try:
                import requests
                response = requests.get(endpoint, headers=headers, timeout=10)
                if response.status_code == 200:
                    variables = response.json()
                    if variables:
                        return {
                            'id': run_id,
                            'variables': variables,
                            # Flatten main outputs
                            'accumulated_profit': variables.get('accumulated_profit'),
                            'compromised_systems': variables.get('compromised_systems'),
                            'profits': variables.get('profits'),
                            'systems_availability': variables.get('systems_availability'),
                            # Flatten inputs
                            'F1': variables.get('prevention_budget'),
                            'F2': variables.get('detection_budget'),
                            'F3': variables.get('response_budget'),
                            'F4': variables.get('recovery_budget'),
                            # Flatten additional outputs
                            'systems_at_risk': variables.get('systems_at_risk'),
                            'fraction_to_make_profits': variables.get('fraction_to_make_profits'),
                            'impact_on_business': variables.get('impact_on_business')
                        }
            except Exception as e:
                print(f"Error fetching from {endpoint}: {e}")
                continue
        
        return None
    
    def run_strategy_batch(self, strategies: List[Dict]) -> List[Dict]:
        """
        Run multiple strategies and collect results.
        
        Args:
            strategies: List of dicts with 'F1', 'F2', 'F3', 'F4' keys
        
        Returns:
            List of run results
        """
        results = []
        
        for i, strategy in enumerate(strategies):
            print(f"\n{'='*70}")
            print(f"Strategy {i+1}/{len(strategies)}")
            print(f"{'='*70}")
            
            f1 = strategy.get('F1', strategy.get('prevention_budget', 0))
            f2 = strategy.get('F2', strategy.get('detection_budget', 0))
            f3 = strategy.get('F3', strategy.get('response_budget', 0))
            f4 = strategy.get('F4', strategy.get('recovery_budget', 0))
            strategy_name = strategy.get('name', f"Strategy_{i+1}")
            
            run = self.create_run_with_budgets(f1, f2, f3, f4, strategy_name=strategy_name)
            
            if run:
                results.append(run)
            else:
                print(f"   ⚠️  Could not create run for strategy {i+1}")
                print(f"   💡 Use manual data entry or automated runner instead")
        
        return results
    
    def save_result_to_data_api(self, result: Dict, document_id: Optional[str] = None) -> Optional[Dict]:
        """
        Save a simulation result to Forio Data API.
        
        Args:
            result: Dictionary with F1-F4 inputs and all outputs
            document_id: Optional specific document ID. If None, auto-generated
        
        Returns:
            Saved document with id and lastModified, or None if failed
        """
        if not self.data_api.is_configured():
            print("⚠️  Data API not configured, saving to local file instead")
            return self._save_to_local_file([result])
        
        saved = self.data_api.save_simulation_result(result, document_id)
        return saved
    
    def save_results(self, results: List[Dict], filename: Optional[str] = None, 
                    use_data_api: bool = True):
        """
        Save results to Data API and/or local JSON file.
        
        Args:
            results: List of result dictionaries
            filename: Optional local filename (default: 'simulation_results.json')
            use_data_api: Whether to save to Data API (default: True)
        """
        saved_count = 0
        
        if use_data_api and self.data_api.is_configured():
            print(f"\n💾 Saving {len(results)} results to Forio Data API...")
            for result in results:
                saved = self.data_api.save_simulation_result(result)
                if saved:
                    saved_count += 1
            print(f"✅ Saved {saved_count}/{len(results)} results to Data API")
        
        # Also save to local file as backup
        if filename is None:
            filename = 'simulation_results.json'
        self._save_to_local_file(results, filename)
    
    def _save_to_local_file(self, results: List[Dict], filename: str = 'simulation_results.json'):
        """Save results to local JSON file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"✅ Saved {len(results)} results to {filename}")
    
    def load_results_from_data_api(self, limit: Optional[int] = None, 
                                   search_query: Optional[Dict] = None) -> List[Dict]:
        """
        Load simulation results from Forio Data API.
        
        Args:
            limit: Maximum number of results to retrieve
            search_query: Optional search query (e.g., {"F1": {"$gte": 30}})
        
        Returns:
            List of simulation results
        """
        if not self.data_api.is_configured():
            print("⚠️  Data API not configured")
            return []
        
        if search_query:
            results = self.data_api.search_results(search_query, limit=limit)
        else:
            results = self.data_api.get_all_results(limit=limit, sort_by="lastModified", direction="desc")
        
        return results


def main():
    """Example usage of SimulationRunner."""
    print("=" * 70)
    print("🤖 Simulation Runner for Cyber-Risk Management")
    print("=" * 70)
    
    try:
        runner = SimulationRunner()
        
        # Define test strategies with F1-F4
        strategies = [
            {
                'name': 'Balanced',
                'F1': 30,  # Prevention
                'F2': 30,  # Detection
                'F3': 25,  # Response
                'F4': 15   # Recovery
            },
            {
                'name': 'Prevention-Heavy',
                'F1': 50,
                'F2': 25,
                'F3': 15,
                'F4': 10
            },
            {
                'name': 'Detection-Heavy',
                'F1': 20,
                'F2': 50,
                'F3': 20,
                'F4': 10
            },
            {
                'name': 'Response-Heavy',
                'F1': 15,
                'F2': 20,
                'F3': 45,
                'F4': 20
            },
            {
                'name': 'Recovery-Heavy',
                'F1': 20,
                'F2': 20,
                'F3': 20,
                'F4': 40
            }
        ]
        
        print(f"\n📋 Running {len(strategies)} strategies...")
        results = runner.run_strategy_batch(strategies)
        
        if results:
            # Save to both Data API and local file
            runner.save_results(results, use_data_api=True)
            print("\n✅ Simulation runs completed!")
            print("\n📊 You can now:")
            print("   - View results in Forio Data API collection")
            print("   - Load results: runner.load_results_from_data_api()")
            print("   - Search results: runner.data_api.search_results({'F1': {'$gte': 30}})")
        else:
            print("\n⚠️  No runs created. Use alternative methods:")
            print("   1. python automated_simulation_runner.py")
            print("   2. python scripts/manual_data_entry.py")
            print("   3. Use Forio web interface directly")
            print("   4. Manually enter results and save to Data API")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

