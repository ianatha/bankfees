#!/usr/bin/env python3
"""
Initialize the system with a domain configuration.
This script should be run before using other tools to ensure the domain is properly configured.
"""
import argparse
from pathlib import Path
from domain_config import domain_manager


def main():
    parser = argparse.ArgumentParser(description="Initialize domain configuration")
    parser.add_argument('config_file', type=Path, nargs='?', 
                       default=Path('banking_domain.json'),
                       help='Path to domain configuration file (default: banking_domain.json)')
    
    args = parser.parse_args()
    
    if not args.config_file.exists():
        print(f"Error: Configuration file {args.config_file} does not exist.")
        print("Available configurations:")
        config_files = list(Path(".").glob("*_domain.json"))
        for config_file in config_files:
            print(f"  • {config_file}")
        print("\nTo create a new domain configuration:")
        print("  python configure_domain.py create insurance")
        print("  python configure_domain.py create retail")
        return 1
    
    try:
        domain_manager.load_config(args.config_file)
        print(f"✓ Successfully loaded domain configuration: {domain_manager.config.name}")
        print(f"  Description: {domain_manager.config.description}")
        print(f"  Entities: {len(domain_manager.config.entities)}")
        print(f"  Categories: {len(domain_manager.config.document_categories)}")
        return 0
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return 1


if __name__ == "__main__":
    exit(main())