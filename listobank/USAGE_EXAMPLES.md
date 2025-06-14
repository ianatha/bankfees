# Usage Examples

This document shows how to use the generalized document analysis system with different domains.

## Example 1: Banking Domain

The original banking domain is still fully supported:

```bash
# Initialize banking domain
python init_domain.py banking_domain.json

# Show current configuration
python configure_domain.py show
# Output: Current domain: banking (5 entities, 8 categories)

# Use the banking-specific tools
python pdf_retriever.py        # Downloads from Greek bank websites
python doc_classification.py   # Classifies using banking categories
python pdfs_to_meili.py        # Indexes with entity="alpha", "eurobank", etc.
```

## Example 2: Insurance Domain

Switch to insurance companies:

```bash
# Create insurance domain configuration
python configure_domain.py create insurance

# Switch to insurance domain
python init_domain.py insurance_domain.json

# Show current configuration  
python configure_domain.py show
# Output: Current domain: insurance (3 entities, 6 categories)

# Now the same tools work with insurance data
python pdf_retriever.py        # Downloads from insurance company websites
python doc_classification.py   # Classifies as Policy, Terms, Coverage, etc.
python pdfs_to_meili.py        # Indexes with entity="allianz", "axa", etc.
```

## Example 3: Retail Domain

Switch to retail companies:

```bash
# Create retail domain configuration
python configure_domain.py create retail

# Switch to retail domain
python init_domain.py retail_domain.json

# The tools now analyze retail documents
python pdf_retriever.py        # Downloads from retail websites
python doc_classification.py   # Classifies as ProductCatalog, ReturnPolicy, etc.
python pdfs_to_meili.py        # Indexes with entity="amazon", "walmart", etc.
```

## Example 4: Custom Domain

Create your own domain configuration:

```json
{
  "name": "healthcare",
  "description": "Healthcare provider domain for analyzing medical documents",
  "entities": {
    "hospital_a": {
      "name": "General Hospital A",
      "description": "Major hospital system",
      "display_name": "Hospital A"
    },
    "clinic_b": {
      "name": "Specialty Clinic B", 
      "description": "Specialized medical clinic",
      "display_name": "Clinic B"
    }
  },
  "document_categories": {
    "PatientGuide": "Patient information and guidance documents",
    "Procedures": "Medical procedure descriptions and requirements",
    "Insurance": "Insurance coverage and billing information",
    "Policies": "Hospital policies and protocols"
  },
  "entity_urls": {
    "hospital_a": ["https://hospitala.com/documents"],
    "clinic_b": ["https://clinicb.com/patient-info"]
  },
  "default_category": "Uncategorized"
}
```

Save as `healthcare_domain.json` and use:

```bash
python init_domain.py healthcare_domain.json
python configure_domain.py show
# Now all tools work with healthcare entities and categories
```

## Data Organization

The file system structure adapts to your domain:

### Banking Domain:
```
data/
├── alpha/           # Alpha Bank documents
├── eurobank/        # Eurobank documents  
└── piraeus/         # Piraeus Bank documents
```

### Insurance Domain:
```
data/
├── allianz/         # Allianz documents
├── axa/             # AXA documents
└── generali/        # Generali documents
```

### Custom Domain:
```
data/
├── hospital_a/      # Hospital A documents
└── clinic_b/        # Clinic B documents
```

## Key Benefits

1. **No Code Changes**: Switch domains without modifying any Python code
2. **Consistent Interface**: Same commands work across all domains
3. **Flexible Categories**: Define document types specific to your industry
4. **Scalable**: Add new entities and categories without code changes
5. **Reusable**: All analysis tools work across domains