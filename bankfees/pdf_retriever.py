#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from ground_truths import BankRootUrls
from tqdm import tqdm
import json

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}


def download_file(url: str, dest_path: str, chunk_size: int = 8192, etag: str = None):
    """
    Streams a file from the given URL to the specified filesystem path.
    Uses ETag for conditional requests if provided.
    Returns the new ETag (if any).
    """
    headers = HEADERS.copy()
    if etag:
        headers["If-None-Match"] = etag

    with requests.get(url, headers=headers, stream=True, timeout=15) as response:
        if response.status_code == 304:
            # Not modified
            return etag
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            total = int(response.headers.get("content-length", 0))
            with tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                desc=os.path.basename(dest_path),
                leave=False,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        return response.headers.get("ETag")


def download_pdfs(bank_name: str, page_url: str, base_folder: str = "data_new"):
    """
    Scrapes all PDF links from the given page URL and downloads them into
    data_new/{bank_name}/, skipping files that haven't changed (using ETag).
    """
    # Create target directory
    target_dir = os.path.join(base_folder, bank_name)
    os.makedirs(target_dir, exist_ok=True)

    # ETag cache file
    etag_cache_path = os.path.join(target_dir, "_etag_cache.json")
    if os.path.exists(etag_cache_path):
        with open(etag_cache_path, "r") as f:
            etag_cache = json.load(f)
    else:
        etag_cache = {}

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
    updated = False
    for pdf_url in tqdm(
        sorted(pdf_links), desc=f"    Downloading PDFs from {page_url}", unit="file", leave=False
    ):
        filename = os.path.basename(urlparse(pdf_url).path)
        dest_path = os.path.join(target_dir, filename)
        etag = etag_cache.get(pdf_url)
        try:
            new_etag = download_file(pdf_url, dest_path, etag=etag)
            if new_etag:
                etag_cache[pdf_url] = new_etag
                updated = True
        except requests.HTTPError as e:
            if e.response.status_code == 304:
                # Not modified, skip
                continue
            print(f"[ERROR] Failed to download {pdf_url} for {bank_name}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to download {pdf_url} for {bank_name}: {e}")

    # Save updated ETag cache
    if updated:
        with open(etag_cache_path, "w") as f:
            json.dump(etag_cache, f, indent=2)



def main():
  for bank_name, urls in tqdm(BankRootUrls.root.items(), desc="Banks", unit="bank"):
    for url in tqdm(urls, desc=f"  Crawling {bank_name.value} URLs", unit="URL", leave=False):
        download_pdfs(bank_name.value, url.encoded_string())


if __name__ == "__main__":
  main()
