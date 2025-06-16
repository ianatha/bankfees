import pdfplumber
import pandas as pd

def extract_raw_data_from_pdf(pdf_path):
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        # Extract bank name and effective date (heuristic)
        first_page_text = pdf.pages[0].extract_text()
        # You'll need logic here to find the bank name and date
        bank_name = "Unknown Bank" # e.g., find_bank_name(first_page_text)
        effective_date = "YYYY-MM-DD" # e.g., find_effective_date(first_page_text)

        for i, page in enumerate(pdf.pages[2:4]):
            print("#### page")
            # Primary method: extract tables directly
            tables = page.extract_tables()
            for table in tables:
                print("#### table")
                # Print as markdown table
                df = pd.DataFrame(table[1:], columns=table[0])
                print(df)
                # Clean up None values and newlines
                clean_table = [[cell.replace('\n', ' ') if cell is not None else '' for cell in row] for row in table]
                all_tables.append({
                    "bank": bank_name,
                    "date": effective_date,
                    "page": i + 1,
                    "data": pd.DataFrame(clean_table[1:], columns=clean_table[0]) # Assuming first row is header
                })
    return all_tables

# You would run this for each PDF.
raw_data = extract_raw_data_from_pdf('alpha.pdf')
