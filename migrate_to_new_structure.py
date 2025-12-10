#!/usr/bin/env python3
"""
Migration Script: Reorganize Project Structure
Run this to automatically reorganize your files into the new structure.
"""

import os
import shutil
import json

# Color codes for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
END = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{END}")
    print(f"{BLUE}{text}{END}")
    print(f"{BLUE}{'='*70}{END}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{END}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{END}")

def print_error(text):
    print(f"{RED}✗ {text}{END}")

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print_success(f"Created directory: {path}")
    else:
        print_warning(f"Directory already exists: {path}")

def create_file(path, content):
    """Create file with content."""
    with open(path, 'w') as f:
        f.write(content)
    print_success(f"Created file: {path}")

def move_file(src, dst):
    """Move file if source exists."""
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        print_success(f"Moved: {src} → {dst}")
        return True
    return False

def backup_existing():
    """Create backup of existing structure."""
    backup_dir = "backup_old_structure"
    if os.path.exists(backup_dir):
        print_warning(f"Backup already exists: {backup_dir}")
        return False
    
    print_header("Creating Backup")
    shutil.copytree(".", backup_dir, 
                   ignore=shutil.ignore_patterns('backup_*', '*.pyc', '__pycache__', '.git', 'venv'))
    print_success(f"Backup created: {backup_dir}")
    return True

def create_new_structure():
    """Create new directory structure."""
    print_header("Creating New Directory Structure")
    
    directories = [
        "app",
        "data",
        "scripts",
        "config",
        "templates",
        "static",
        "docs"
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # Create __init__.py files
    for directory in ["app", "data"]:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            create_file(init_file, "# Package initialization\n")

def move_existing_files():
    """Move existing files to new locations."""
    print_header("Moving Existing Files")
    
    # Move scripts
    scripts_to_move = [
        ("manual_data_entry.py", "scripts/manual_data_entry.py"),
        ("calibrate_agents.py", "scripts/calibrate_agents.py"),
        ("test_forio_connection.py", "scripts/test_connection.py"),
        ("evaluate_framework.py", "scripts/evaluate_framework.py"),
        ("generate_agent_justification.py", "scripts/generate_justification.py"),
    ]
    
    for src, dst in scripts_to_move:
        move_file(src, dst)
    
    # Keep existing template
    if os.path.exists("templates/dashboard.html"):
        print_success("Template already in place: templates/dashboard.html")
    
    # Move documentation
    docs_to_move = [
        ("EXTRACT_DATA_FROM_BROWSER.md", "docs/EXTRACT_DATA_FROM_BROWSER.md"),
    ]
    
    for src, dst in docs_to_move:
        move_file(src, dst)

def create_agent_config():
    """Create agent configuration file."""
    print_header("Creating Agent Configuration")
    
    config_file = "config/agent_config.json"
    
    if os.path.exists(config_file):
        print_warning(f"Config already exists: {config_file}")
        return
    
    config = {
        "agents": {
            "CFO": {
                "kpi": "accumulated_profit",
                "target": {"min": 1200000},
                "personality": {
                    "risk_tolerance": 0.3,
                    "friendliness": 0.6,
                    "ambition": 0.8
                }
            },
            "CRO": {
                "kpi": "compromised_systems",
                "target": {"max": 10},
                "personality": {
                    "risk_tolerance": 0.2,
                    "friendliness": 0.5,
                    "ambition": 0.6
                }
            },
            "COO": {
                "kpi": "systems_availability",
                "target": {"min": 0.92},
                "personality": {
                    "risk_tolerance": 0.5,
                    "friendliness": 0.7,
                    "ambition": 0.7
                }
            }
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print_success(f"Created: {config_file}")

def list_files_to_delete():
    """List old files that can be deleted."""
    print_header("Old Files (Can Be Deleted)")
    
    files_to_delete = [
        "multi-agent_setup.py",
        "multi_agent_demo.py",
        "multi_agent_demo_mock.py",
        "forio_data_extractor.py",
        "data_extractor_example.py",
        "extract_real_data.py",
        "quick_test_extraction.py",
        "test_enhanced_extraction.py",
        "test_run_variables.py",
        "list_variables.py",
        "list_models.py",
        "inspect_run_details.py",
        "view_agent_config.py",
        "static-dashboard.html",
        "quick_connection_test.sh",
    ]
    
    found = []
    for filename in files_to_delete:
        if os.path.exists(filename):
            found.append(filename)
            print(f"  • {filename}")
    
    if found:
        print(f"\n{YELLOW}To delete these files, run:{END}")
        print(f"  rm {' '.join(found)}")
        print(f"\n{YELLOW}Or move to backup:{END}")
        print(f"  mkdir old_files && mv {' '.join(found)} old_files/")
    else:
        print_success("No old files found")

def create_setup_guide():
    """Create setup guide."""
    print_header("Creating Documentation")
    
    setup_content = """# Setup Instructions

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Enter simulation data:
   ```bash
   python scripts/manual_data_entry.py
   ```

3. Run dashboard:
   ```bash
   python app/dashboard.py
   ```

4. Open browser:
   - Visit: http://localhost:5000

## For Detailed Instructions

See SETUP.md for complete setup guide.
"""
    
    if not os.path.exists("QUICK_START.md"):
        create_file("QUICK_START.md", setup_content)

def create_readme():
    """Create README if it doesn't exist."""
    if os.path.exists("README.md"):
        print_warning("README.md already exists, skipping")
        return
    
    readme_content = """# Multi-Agent Personality Bot System

Dashboard for analyzing cyber-risk simulation results with AI agents.

## Quick Start

1. Install: `pip install -r requirements.txt`
2. Enter data: `python scripts/manual_data_entry.py`
3. Run: `python app/dashboard.py`
4. Visit: http://localhost:5000

## Documentation

- SETUP.md - Complete setup instructions
- QUICK_START.md - Quick start guide
- docs/ - Additional documentation

## Structure

- app/ - Main application (dashboard, agents)
- data/ - Data loading and management
- scripts/ - Utility scripts
- config/ - Configuration files
- templates/ - HTML templates

## Data Sources

Priority order:
1. Manual data (simulation_data.json)
2. Forio API (if configured)
3. Mock data (fallback)

## Configuration

Edit `config/agent_config.json` to customize agent behavior.
"""
    
    create_file("README.md", readme_content)

def main():
    """Main migration process."""
    print_header("Multi-Agent Project Migration")
    print("This script will reorganize your project into a cleaner structure.")
    
    # Confirm
    response = input(f"\n{YELLOW}Create backup and proceed? (y/n): {END}").strip().lower()
    if response != 'y':
        print_error("Migration cancelled")
        return
    
    # Execute migration steps
    backup_existing()
    create_new_structure()
    move_existing_files()
    create_agent_config()
    create_setup_guide()
    create_readme()
    list_files_to_delete()
    
    # Next steps
    print_header("Migration Complete!")
    print(f"{GREEN}Your project has been reorganized.{END}\n")
    print(f"{BLUE}Next Steps:{END}")
    print("1. Copy the new Python files from the artifacts I provided:")
    print("   - app/agents.py")
    print("   - app/dashboard.py")
    print("   - data/data_loader.py")
    print("   - data/forio_client.py")
    print("\n2. Test the new structure:")
    print("   python data/data_loader.py")
    print("   python app/agents.py")
    print("\n3. Run the dashboard:")
    print("   python app/dashboard.py")
    print("\n4. Clean up old files (optional):")
    print("   See the list above and delete/move as needed")
    print(f"\n{YELLOW}Backup saved in: backup_old_structure/{END}")
    print()

if __name__ == "__main__":
    main()