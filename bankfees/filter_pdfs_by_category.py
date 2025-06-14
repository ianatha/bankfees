#!/usr/bin/env python3
import argparse
from pathlib import Path
from doc_analysis import DocumentCategory, load_document_analysis

def main():
    parser = argparse.ArgumentParser(description="Print PDFs filtered by docanalysis category")
    parser.add_argument("category", type=str, help="Category to filter by")
    parser.add_argument("--data-dir", type=str, default="data_new", help="Data directory (default: data_new)")
    
    args = parser.parse_args()
    
    # Validate category
    try:
        target_category = DocumentCategory(args.category)
    except ValueError:
        print(f"Error: Invalid category '{args.category}'")
        print("Valid categories:", [c.value for c in DocumentCategory])
        return
    
    root_dir = Path(args.data_dir)
    if not root_dir.exists():
        print(f"Error: Data directory '{root_dir}' does not exist")
        return
    
    pdf_files = list(root_dir.glob("**/*.pdf"))
    matching_files = []
    
    for pdf_file in pdf_files:
        if pdf_file.name.startswith("_"):
            continue
            
        try:
            doc_analysis = load_document_analysis(pdf_file)
            if doc_analysis and doc_analysis.category == target_category:
                matching_files.append(pdf_file)
        except Exception as e:
            continue
    
    if matching_files:
        for pdf_file in matching_files:
            print(pdf_file)
    else:
        print(f"No PDFs found with category '{target_category.value}'")

if __name__ == "__main__":
    main()