# Listobank

A comprehensive tool for analyzing and comparing bank fees across major Greek banks (Alpha Bank, Attica Bank, Eurobank, NBG, Piraeus Bank). The system automatically retrieves pricing documents, classifies them using LLM analysis, and provides a searchable interface through a Next.js web application.

## Features

- **Automated Document Retrieval**: Downloads pricing documents and fee schedules from bank websites
- **AI-Powered Classification**: Uses Gemini AI to automatically categorize documents (price lists, fee schedules, terms & conditions, etc.)
- **Document Analysis**: Extracts structured data from PDFs with analysis of fees, rates, and terms
- **Search Interface**: Next.js web application with MeiliSearch for fast document search and comparison
- **Multi-Bank Support**: Covers Alpha Bank, Attica Bank, Eurobank, NBG, and Piraeus Bank

## Project Structure

```
├── data/              # Raw PDF documents organized by bank
├── data_new/          # Processed documents with AI analysis
├── pricelists/        # Consolidated price lists by bank
├── ui/                # Next.js web interface
├── explorations/      # Jupyter notebooks for data exploration
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

## Usage

### Data Processing Pipeline

1. **Retrieve Documents**: Download latest documents from bank websites
```bash
./pdf_retriever.py
```

2. **Classify Documents**: Use AI to categorize documents
```bash
./doc_classification.py
```

3. **Index for Search**: Add documents to MeiliSearch index
```bash
./pdfs_to_meili.py
```

### Web Interface

Start the development server:
```bash
cd ui
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the search interface.

## Document Categories

The system classifies documents into the following categories:
- **PriceList**: General fee schedules and pricing
- **PriceListExclusive**: Premium/private banking fees
- **InterestRates**: Deposit and loan interest rates
- **PaymentFees**: Payment and transfer charges
- **DeltioPliroforisisPeriTelon**: Official fee disclosure documents
- **GeneralTermsContract**: Terms and conditions
- **Disclosure**: Risk disclosures and regulatory information
- **CustomerGuide**: Customer service documentation

## Requirements

- Python 3.8+
- Node.js 18+
- MeiliSearch server
- Google AI API key (for document classification)