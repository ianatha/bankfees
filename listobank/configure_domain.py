#!/usr/bin/env python3
"""
Script to configure and switch between different domain models.
"""
import argparse
import json
from pathlib import Path
from typing import Dict, Any
from domain_config import DomainConfig, domain_manager


def create_insurance_domain() -> DomainConfig:
    """Create a sample insurance domain configuration"""
    return DomainConfig(
        name="insurance",
        description="Insurance company domain for analyzing policies and documents",
        entities={
            "allianz": {
                "name": "Allianz Insurance",
                "description": "Allianz Insurance Company",
                "display_name": "Allianz"
            },
            "axa": {
                "name": "AXA Insurance", 
                "description": "AXA Insurance Company",
                "display_name": "AXA"
            },
            "generali": {
                "name": "Generali Insurance",
                "description": "Generali Insurance Company",
                "display_name": "Generali"
            }
        },
        document_categories={
            "Policy": "Insurance policy documents",
            "Terms": "Terms and conditions documents", 
            "PremiumSchedule": "Premium calculation schedules",
            "ClaimsInfo": "Claims processing information",
            "Coverage": "Coverage details and limitations",
            "Disclosure": "Risk disclosures and regulatory information"
        },
        entity_urls={
            "allianz": ["https://www.allianz.com/en/policy-documents"],
            "axa": ["https://www.axa.com/en/policy-terms"],
            "generali": ["https://www.generali.com/policy-info"]
        },
        default_category="Uncategorized"
    )


def create_retail_domain() -> DomainConfig:
    """Create a sample retail domain configuration"""
    return DomainConfig(
        name="retail",
        description="Retail company domain for analyzing product catalogs and documents",
        entities={
            "amazon": {
                "name": "Amazon",
                "description": "Amazon retail platform",
                "display_name": "Amazon"
            },
            "walmart": {
                "name": "Walmart",
                "description": "Walmart retail stores",
                "display_name": "Walmart"
            },
            "target": {
                "name": "Target",
                "description": "Target retail stores", 
                "display_name": "Target"
            }
        },
        document_categories={
            "ProductCatalog": "Product catalogs and listings",
            "PriceList": "Pricing information and fee schedules",
            "Terms": "Terms of service and purchase agreements",
            "ReturnPolicy": "Return and refund policies",
            "ShippingInfo": "Shipping and delivery information",
            "CustomerGuide": "Customer service guides and FAQs"
        },
        entity_urls={
            "amazon": ["https://www.amazon.com/help"],
            "walmart": ["https://www.walmart.com/help"],
            "target": ["https://www.target.com/help"]
        },
        default_category="Uncategorized"
    )


def list_available_domains() -> None:
    """List all available domain configuration files"""
    print("Available domain configurations:")
    
    config_files = list(Path(".").glob("*_domain.json"))
    if not config_files:
        print("  No domain configuration files found.")
        return
        
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                domain_name = config_data.get('name', 'Unknown')
                description = config_data.get('description', 'No description')
                entity_count = len(config_data.get('entities', {}))
                category_count = len(config_data.get('document_categories', {}))
                
            print(f"  • {config_file.stem}: {domain_name}")
            print(f"    Description: {description}")
            print(f"    Entities: {entity_count}, Categories: {category_count}")
            print()
        except Exception as e:
            print(f"  • {config_file.stem}: Error reading file - {e}")


def show_current_domain() -> None:
    """Show information about the currently loaded domain"""
    if not domain_manager.config:
        print("No domain configuration currently loaded.")
        return
        
    config = domain_manager.config
    print(f"Current domain: {config.name}")
    print(f"Description: {config.description}")
    print(f"Entities ({len(config.entities)}):")
    for entity_id, entity_config in config.entities.items():
        print(f"  • {entity_id}: {entity_config.get('display_name', entity_config.get('name', entity_id))}")
    print(f"Document categories ({len(config.document_categories)}):")
    for category, description in config.document_categories.items():
        print(f"  • {category}: {description}")


def main():
    parser = argparse.ArgumentParser(description="Configure domain models for document analysis")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available domain configurations')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show current domain configuration')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set active domain configuration')
    set_parser.add_argument('config_file', type=Path, help='Path to domain configuration JSON file')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create sample domain configurations')
    create_parser.add_argument('domain_type', choices=['insurance', 'retail'], 
                              help='Type of domain configuration to create')
    create_parser.add_argument('--output', '-o', type=Path, 
                              help='Output file (default: {domain_type}_domain.json)')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_available_domains()
        
    elif args.command == 'show':
        # Try to load default configuration if none is loaded
        if not domain_manager.config:
            default_config = Path("banking_domain.json")
            if default_config.exists():
                domain_manager.load_config(default_config)
        show_current_domain()
        
    elif args.command == 'set':
        if not args.config_file.exists():
            print(f"Error: Configuration file {args.config_file} does not exist.")
            return
            
        try:
            domain_manager.load_config(args.config_file)
            print(f"Successfully loaded domain configuration from {args.config_file}")
            show_current_domain()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            
    elif args.command == 'create':
        if args.domain_type == 'insurance':
            config = create_insurance_domain()
        elif args.domain_type == 'retail':
            config = create_retail_domain()
        else:
            print(f"Unknown domain type: {args.domain_type}")
            return
            
        output_file = args.output or Path(f"{args.domain_type}_domain.json")
        
        try:
            domain_manager.save_config(config, output_file)
            print(f"Created {args.domain_type} domain configuration: {output_file}")
        except Exception as e:
            print(f"Error creating configuration: {e}")
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()