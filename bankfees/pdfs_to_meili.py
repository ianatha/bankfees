#!/usr/bin/env python3
"""
Script to extract text from PDFs in bank-specific subfolders and index them into a MeiliSearch instance.
Each document is tagged with a "bank" field corresponding to its parent folder.
"""
import os
from pathlib import Path
import argparse
import hashlib

from meilisearch import Client, errors as meilisearch_errors
from PyPDF2 import PdfReader


def extract_pages_text(pdf_path: Path) -> list[str]:
    """
    Extracts and returns a list of text content for each page in the PDF file.
    """
    reader = PdfReader(str(pdf_path))
    return [page.extract_text() or "" for page in reader.pages]

def clean_index(meili: Client, index_name: str):
    try:
        index = meili.get_index(index_name)
        meili.delete_index(index.uid)
    except meilisearch_errors.MeilisearchApiError:
        pass

def index_pdfs(meili: Client, root_dir: Path, index_name: str, batch_size: int = 10):
    """
    Walk through each subfolder in root_dir (each representing a bank), extract text from all PDFs,
    split them by page, add previous-page context, and index them into the specified MeiliSearch index in batches.
    """
    try:
        index = meili.get_index(index_name)
    except meilisearch_errors.MeilisearchApiError:
        create_task = meili.create_index(uid=index_name, options={"primaryKey": "id"})
        meili.wait_for_task(create_task.task_uid)
        index = meili.get_index(index_name)

    buffer = []
    for bank_folder in root_dir.iterdir():
        if not bank_folder.is_dir():
            continue
        bank_name = bank_folder.name
        print(f"Processing bank folder: {bank_name}")

        for pdf_file in bank_folder.glob("*.pdf"):
            if not pdf_file.is_file() or pdf_file.name.startswith("_"):
                continue

            print(f"  Processing {pdf_file.name}")
            pages = extract_pages_text(pdf_file)
            document_name_hash = hashlib.md5(pdf_file.stem.encode()).hexdigest()
            document_mtime = pdf_file.stat().st_mtime_ns
            prev_text = ""

            for page_idx, page_text in enumerate(pages, start=1):
                # combine previous page's text as context
                if prev_text:
                    content = prev_text + "\n" + page_text
                else:
                    content = page_text

                doc_id = f"{bank_name}_{document_name_hash}_{document_mtime}_p{page_idx}"
                doc = {
                    "id": doc_id,
                    "bank": bank_name,
                    "filename": pdf_file.name,
                    "path": str(pdf_file),
                    "page": page_idx,
                    "content": content,
                }
                buffer.append(doc)
                prev_text = page_text

                # send batch if full
                if len(buffer) >= batch_size:
                    print(f"    Indexing batch of {len(buffer)} docs...")
                    index.add_documents(buffer, primary_key="id")
                    buffer.clear()

    # index any remaining docs
    if buffer:
        print(f"Indexing final batch of {len(buffer)} docs...")
        task_info = index.add_documents(buffer)
        result = meili.wait_for_task(task_info.task_uid)
        if result.error:
            print(f"Error indexing documents: {result.error}")

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
        "--batch-size", type=int, default=10,
        help="Number of documents to index in each batch"
    )
    args = parser.parse_args()

    meili = Client(args.meili_url, args.api_key)

    clean_index(
        meili=meili,
        index_name=args.index_name
    )

    index_pdfs(
        meili=meili,
        root_dir=args.root_dir,
        index_name=args.index_name,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
