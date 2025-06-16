# Generic Document Analysis System

brew install anaconda
/opt/homebrew/anaconda3/bin/conda init zsh
conda env create -f environment.yml

conda env export --name <your_env> --from-history > environment.yml

A flexible, domain-configurable tool for analyzing documents across different industries. Originally designed for analyzing bank fees across major Greek banks, the system now supports any domain through configurable entity and document category definitions. It automatically retrieves documents, classifies them using LLM analysis, and provides a searchable interface through a Next.js web application.

## Features

- **Domain-Configurable**: Supports any industry/domain through JSON configuration files
- **Automated Document Retrieval**: Downloads documents from configurable entity websites
- **AI-Powered Classification**: Uses Gemini AI to automatically categorize documents based on domain-specific categories
- **Document Analysis**: Extracts structured data from PDFs with domain-specific analysis
- **Search Interface**: Next.js web application with MeiliSearch for fast document search and comparison
- **Multi-Entity Support**: Configurable to work with any set of entities (banks, insurance companies, retailers, etc.)

## Project Structure

```
├── data/              # Raw PDF documents organized by entity
├── data_new/          # Processed documents with AI analysis
├── pricelists/        # Consolidated documents by entity
├── ui/                # Next.js web interface
├── explorations/      # Jupyter notebooks for data exploration
├── *_domain.json      # Domain configuration files
└── *.py               # Python processing scripts
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install and setup the web interface:
```bash
cd ui
npm install
```

3. Initialize your domain configuration:
```bash
# Use the default banking configuration
python init_domain.py

# Or specify a different configuration file
python init_domain.py my_domain.json
```

## Usage

### Domain Configuration

1. **List available domains**:
```bash
python configure_domain.py list
```

2. **Create a new domain** (e.g., insurance or retail):
```bash
python configure_domain.py create insurance
python configure_domain.py create retail
```

3. **Set active domain**:
```bash
python configure_domain.py set insurance_domain.json
```

4. **View current domain**:
```bash
python configure_domain.py show
```

### Data Processing Pipeline

1. **Initialize domain** (run this first):
```bash
python init_domain.py [config_file]
```

2. **Retrieve Documents**: Download latest documents from entity websites
```bash
python pdf_retriever.py
```

3. **Classify Documents**: Use AI to categorize documents
```bash
python doc_classification.py
```

4. **Index for Search**: Add documents to MeiliSearch index
```bash
python pdfs_to_meili.py
```

### Web Interface

Start the development server:
```bash
cd ui
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the search interface.

## Domain Configuration

The system uses JSON configuration files to define:

- **Entities**: Organizations to analyze (banks, insurance companies, etc.)
- **Document Categories**: Types of documents specific to your domain
- **Entity URLs**: Website URLs to scrape for documents
- **Category Descriptions**: Detailed descriptions for AI classification

### Example Domain Configurations

**Banking Domain** (`banking_domain.json`):
- Entities: Alpha Bank, Attica Bank, Eurobank, NBG, Piraeus Bank
- Categories: PriceList, InterestRates, PaymentFees, etc.

**Insurance Domain** (create with `configure_domain.py create insurance`):
- Entities: Allianz, AXA, Generali
- Categories: Policy, Terms, PremiumSchedule, ClaimsInfo, etc.

**Retail Domain** (create with `configure_domain.py create retail`):
- Entities: Amazon, Walmart, Target  
- Categories: ProductCatalog, PriceList, ReturnPolicy, etc.

## Requirements

- Python 3.8+
- Node.js 18+
- MeiliSearch server
- Google AI API key (for document classification)
- Domain configuration file (JSON)