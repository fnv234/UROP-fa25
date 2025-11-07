"""
Enhanced Forio Data Extractor
Based on the fde.py approach - extracts simulation data with explicit variable specification
"""

import os
import base64
import requests
import json
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class ForioDataExtractor:
    """Extract data from Forio simulations with variable specification."""
    
    def __init__(self, public_key=None, private_key=None, org=None, project=None):
        """Initialize with Forio credentials."""
        self.public_key = public_key or os.getenv("PUBLIC_KEY")
        self.private_key = private_key or os.getenv("PRIVATE_KEY")
        self.org = org or os.getenv("FORIO_ORG", "mitcams")
        self.project = project or os.getenv("FORIO_PROJECT", "cyberriskmanagement-ransomeware-2023")
        self.token = None
    
    def url_encode(self, s: str) -> str:
        """
        URL encode variable names for API compatibility.
        Replaces commas with %2C and spaces with %20.
        """
        return s.replace(',', '%2C').replace(' ', '%20')
    
    def get_access_token(self) -> Optional[str]:
        """
        Retrieve OAuth access token using client credentials.
        Returns the access token or None if authentication fails.
        """
        try:
            # Encode credentials to Base64
            credentials = base64.b64encode(
                f"{self.public_key}:{self.private_key}".encode('utf-8')
            ).decode('utf-8')
            
            # Token request headers and payload
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {credentials}'
            }
            payload = {'grant_type': 'client_credentials'}
            
            # Make token request
            response = requests.post(
                'https://api.forio.com/v2/oauth/token',
                headers=headers,
                data=payload
            )
            response.raise_for_status()
            
            # Extract and cache access token
            self.token = response.json()['access_token']
            return self.token
            
        except requests.RequestException as e:
            print(f"Error retrieving access token: {e}")
            return None
    
    def fetch_runs_with_variables(
        self, 
        variables: List[str],
        model_name: str = None,
        groups: List[str] = None,
        start_record: int = 0,
        end_record: int = 100,
        saved_only: bool = True,
        trashed: bool = False
    ) -> List[Dict]:
        """
        Fetch simulation runs with specific variables.
        
        Args:
            variables: List of variable names to include (e.g., ['accumulated_profit', 'compromised_systems'])
            model_name: Optional model name to filter by
            groups: Optional list of group names to filter by
            start_record: Starting record index
            end_record: Ending record index
            saved_only: Only fetch saved runs
            trashed: Include trashed runs
            
        Returns:
            List of run dictionaries with requested variables
        """
        # Ensure we have a token
        if not self.token:
            self.token = self.get_access_token()
            if not self.token:
                return []
        
        # URL encode the variables (comma-separated)
        variables_str = ','.join(variables)
        encoded_variables = self.url_encode(variables_str)
        
        all_runs = []
        
        # If no groups specified, fetch all runs
        if not groups:
            groups = [None]
        
        for group in groups:
            # Build filter string
            filters = []
            if saved_only:
                filters.append('saved=true')
            filters.append(f'trashed={str(trashed).lower()}')
            if model_name:
                filters.append(f'model={model_name}')
            if group:
                filters.append(f'scope.group={group}')
            
            filter_string = ';'.join(filters)
            
            # Build API URL
            url = f'https://forio.com/v2/run/{self.org}/{self.project}/;{filter_string}'
            url += f'?sort=created&direction=desc'
            url += f'&include={encoded_variables}'
            url += f'&startRecord={start_record}&endRecord={end_record}'
            
            # API call headers
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            try:
                # Make API request
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                runs = response.json()
                
                # Add group info if specified
                if group:
                    for run in runs:
                        run['_extracted_group'] = group
                
                all_runs.extend(runs)
                
            except requests.RequestException as e:
                print(f"Error fetching runs for group '{group}': {e}")
                continue
        
        return all_runs
    
    def fetch_all_runs_metadata(
        self,
        start_record: int = 0,
        end_record: int = 100
    ) -> List[Dict]:
        """
        Fetch run metadata without variables (faster).
        Useful for getting run IDs and basic info.
        """
        if not self.token:
            self.token = self.get_access_token()
            if not self.token:
                return []
        
        headers = {'Authorization': f'Bearer {self.token}'}
        url = f'https://forio.com/v2/run/{self.org}/{self.project}/;saved=true;trashed=false'
        url += f'?sort=created&direction=desc&startRecord={start_record}&endRecord={end_record}'
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching run metadata: {e}")
            return []
    
    def fetch_specific_run(
        self,
        run_id: str,
        variables: List[str] = None
    ) -> Optional[Dict]:
        """
        Fetch a specific run by ID with optional variables.
        
        Args:
            run_id: The run ID to fetch
            variables: Optional list of variables to include
            
        Returns:
            Run dictionary or None if not found
        """
        if not self.token:
            self.token = self.get_access_token()
            if not self.token:
                return None
        
        headers = {'Authorization': f'Bearer {self.token}'}
        url = f'https://forio.com/v2/run/{self.org}/{self.project}/{run_id}'
        
        if variables:
            variables_str = ','.join(variables)
            encoded_variables = self.url_encode(variables_str)
            url += f'?include={encoded_variables}'
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching run {run_id}: {e}")
            return None
    
    def extract_variables_from_runs(
        self,
        runs: List[Dict],
        variable_names: List[str]
    ) -> List[Dict]:
        """
        Extract specific variables from run data.
        
        Args:
            runs: List of run dictionaries
            variable_names: List of variable names to extract
            
        Returns:
            List of simplified dictionaries with just the requested variables
        """
        extracted = []
        
        for run in runs:
            run_data = {
                'id': run.get('id'),
                'created': run.get('created'),
                'user': run.get('user', {}).get('userName', 'Unknown'),
                'group': run.get('scope', {}).get('group', run.get('_extracted_group', 'default'))
            }
            
            # Extract variables from the 'variables' field
            variables = run.get('variables', {})
            for var_name in variable_names:
                run_data[var_name] = variables.get(var_name)
            
            extracted.append(run_data)
        
        return extracted
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save extracted data to JSON file."""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Saved {len(data)} runs to {filename}")
    
    def test_connection(self) -> Dict:
        """
        Test connection and return status information.
        
        Returns:
            Dictionary with connection status and details
        """
        status = {
            'authenticated': False,
            'runs_found': 0,
            'variables_recorded': False,
            'sample_run': None
        }
        
        # Test authentication
        token = self.get_access_token()
        if not token:
            return status
        
        status['authenticated'] = True
        
        # Test fetching runs
        runs = self.fetch_all_runs_metadata(start_record=0, end_record=1)
        if not runs:
            return status
        
        status['runs_found'] = len(runs)
        
        # Check if variables are recorded
        if runs[0].get('variables'):
            status['variables_recorded'] = True
            status['sample_run'] = {
                'id': runs[0].get('id'),
                'variables': list(runs[0]['variables'].keys())[:10]
            }
        else:
            status['sample_run'] = {
                'id': runs[0].get('id'),
                'variables': []
            }
        
        return status


# Example usage
if __name__ == '__main__':
    print("=" * 70)
    print("🔍 FORIO DATA EXTRACTOR TEST")
    print("=" * 70)
    
    # Initialize extractor
    extractor = ForioDataExtractor()
    
    # Test connection
    print("\n1️⃣ Testing connection...")
    status = extractor.test_connection()
    print(f"   Authenticated: {status['authenticated']}")
    print(f"   Runs found: {status['runs_found']}")
    print(f"   Variables recorded: {status['variables_recorded']}")
    
    if status['sample_run']:
        print(f"   Sample run ID: {status['sample_run']['id']}")
        print(f"   Variables: {status['sample_run']['variables']}")
    
    # Define variables we want to extract
    target_variables = [
        'accumulated_profit',
        'compromised_systems',
        'systems_availability',
        'prevention_budget',
        'detection_budget',
        'response_budget'
    ]
    
    print(f"\n2️⃣ Attempting to fetch runs with variables...")
    print(f"   Target variables: {target_variables}")
    
    # Try to fetch runs with variables
    runs = extractor.fetch_runs_with_variables(
        variables=target_variables,
        start_record=0,
        end_record=10
    )
    
    print(f"   Fetched {len(runs)} runs")
    
    if runs:
        # Check if variables are present
        sample_run = runs[0]
        has_variables = bool(sample_run.get('variables'))
        print(f"   Variables present: {has_variables}")
        
        if has_variables:
            print(f"   Sample variables: {list(sample_run['variables'].keys())[:5]}")
            
            # Extract and save
            extracted = extractor.extract_variables_from_runs(runs, target_variables)
            extractor.save_to_json(extracted, 'extracted_forio_data.json')
        else:
            print("   ⚠️  No variables recorded in runs")
            print("   💡 The Vensim model needs to be configured to save variables")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
