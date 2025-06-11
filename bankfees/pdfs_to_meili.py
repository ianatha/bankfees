#!/usr/bin/env python3
"""
Script to extract text from PDFs in bank-specific subfolders and index them into a MeiliSearch instance.
Each document is tagged with a "bank" field corresponding to its parent folder.
"""
import os
from pathlib import Path
import argparse

from meilisearch import Client
from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extracts and returns the full text content from a PDF file.
    """
    reader = PdfReader(str(pdf_path))
    text_chunks = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_chunks.append(page_text)
    return "\n".join(text_chunks)


def index_pdfs(root_dir: Path, meili_url: str, api_key: str, index_name: str, batch_size: int = 100):
    """
    Walks through each subfolder in root_dir (each representing a bank), extracts text from all PDFs,
    and indexes them into the specified MeiliSearch index in batches.
    """
    client = Client(meili_url, api_key)
    try:
        index = client.get_index(index_name)
    except Exception:
        index = client.create_index(uid=index_name, options={"primaryKey": "id"})

    buffer = []
    for bank_folder in root_dir.iterdir():
        print(f"Processing bank folder: {bank_folder}")
        if bank_folder.is_dir():
            bank_name = bank_folder.name
            for pdf_file in bank_folder.glob("*.pdf"):
                print(f"Processing {pdf_file} in bank {bank_name}")
                if not pdf_file.is_file():
                    continue
                content = extract_text_from_pdf(pdf_file)
                print(f"Extracted content from {pdf_file}: {len(content)} characters")
                print(content)
                doc = {
                    "id": f"{bank_name}_{pdf_file.stem}",
                    "bank": bank_name,
                    "filename": pdf_file.name,
                    "path": str(pdf_file),
                    "content": content,
                }
                buffer.append(doc)
                if len(buffer) >= batch_size:
                    index.add_documents(buffer, primary_key="id")
                    buffer.clear()

    if buffer:
        index.add_documents(buffer)


def main():
    # Environment defaults
    default_url = os.environ.get("MEILI_URL", "")
    default_key = os.environ.get("MEILI_API_KEY", "")

    parser = argparse.ArgumentParser(description="Index bank PDFs into MeiliSearch")
    parser.add_argument(
        "--root-dir", type=Path, default=Path.cwd() / "data",
        help="Root directory containing bank-named subfolders with PDFs (default: ./data)"
    )
    parser.add_argument(
        "--meili-url", type=str, default=default_url,
        help="URL of the MeiliSearch instance (or set MEILI_URL env)"
    )
    parser.add_argument(
        "--api-key", type=str, default=default_key,
        help="API key for MeiliSearch (or set MEILI_API_KEY env)"
    )
    parser.add_argument(
        "--index-name", type=str, default="bankfees",
        help="Name of the MeiliSearch index to use or create"
    )
    parser.add_argument(
        "--batch-size", type=int, default=100,
        help="Number of documents to index in each batch"
    )
    args = parser.parse_args()

    index_pdfs(
        root_dir=args.root_dir,
        meili_url=args.meili_url,
        api_key=args.api_key,
        index_name=args.index_name,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
