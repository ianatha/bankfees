#!/usr/bin/env python3
import os
from pydantic import HttpUrl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from ground_truths import BankRootUrls
from tqdm import tqdm
import datetime
from pathlib import Path
from doc_analysis import DocumentAnalysis, load_document_analysis, new_document_analysis

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}


def download_file(url: str, dest_path: str, chunk_size: int = 8192, existing_etag: str = None, indent_level: int = 0) -> tuple[str, bool]:
    """
    Streams a file from the given URL to the specified filesystem path.
    Uses ETag for conditional requests if provided.
    Returns tuple of (new_etag, was_modified).
    """
    headers = HEADERS.copy()
    if existing_etag:
        headers["If-None-Match"] = existing_etag

    indentation = "  " * indent_level
    with requests.get(url, headers=headers, stream=True, timeout=15) as response:
        if response.status_code == 304:
            # Not modified
            return existing_etag, False
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            total = int(response.headers.get("content-length", 0))
            with tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                desc=indentation + os.path.basename(dest_path),
                leave=False,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        return response.headers.get("ETag"), True


def download_pdfs(bank_name: str, page_url: str, base_folder: str = "data_new"):
    """
    Scrapes all PDF links from the given page URL and downloads them into
    data_new/{bank_name}/, using DocumentAnalysis to track metadata and ETags.
    """
    # Create target directory
    target_dir = os.path.join(base_folder, bank_name)
    os.makedirs(target_dir, exist_ok=True)

    # Fetch page content
    resp = requests.get(page_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    # Parse HTML for PDF links
    soup = BeautifulSoup(resp.text, "html.parser")
    pdf_links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        parsed_href = urlparse(href)
        if parsed_href.path.lower().endswith(".pdf"):
            full_url = urljoin(page_url, href)
            pdf_links.add(full_url)

    # Download each PDF
    for pdf_url in tqdm(
        sorted(pdf_links), desc=f"    Downloading PDFs from {page_url}", unit="file", leave=False
    ):
        filename = os.path.basename(urlparse(pdf_url).path)
        dest_path = Path(target_dir) / filename
        
        # Load existing DocumentAnalysis if available
        try:
            doc_analysis = load_document_analysis(dest_path)
        except FileNotFoundError:
            doc_analysis = None
        if doc_analysis is not None:
            existing_etag = doc_analysis.retrieved_etag
        else:
            existing_etag = None

        try:
            new_etag, was_modified = download_file(pdf_url, str(dest_path), existing_etag=existing_etag, indent_level=3)
            
            if doc_analysis is None:
                doc_analysis = new_document_analysis(
                    file_path=dest_path,
                    retrieved_from=pdf_url,
                    retrieved_at=datetime.datetime.now(datetime.timezone.utc),
                    retrieved_etag=new_etag,
                )
            # Create or update DocumentAnalysis
            if was_modified:
                doc_analysis.retrieved_from = HttpUrl(pdf_url)
                doc_analysis.retrieved_at = datetime.datetime.now(datetime.timezone.utc)
                doc_analysis.retrieved_etag = new_etag
                doc_analysis.save()
                
        except requests.HTTPError as e:
            if e.response.status_code == 304:
                # Not modified, skip
                continue
            print(f"[ERROR] Failed to download {pdf_url} for {bank_name}: {e}")


def main():
    for bank_name, urls in tqdm(BankRootUrls.root.items(), desc="Banks", unit="bank"):
        for url in tqdm(urls, desc=f"  Crawling {bank_name.value} URLs", unit="URL", leave=False):
            download_pdfs(bank_name.value, url.encoded_string())


if __name__ == "__main__":
    main()