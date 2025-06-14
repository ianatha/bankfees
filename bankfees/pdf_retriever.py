#!/usr/bin/env python3

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from enum import Enum
from typing import Dict, List
from pydantic import RootModel, HttpUrl
from tqdm import tqdm


class Bank(str, Enum):
  ALPHA = "alpha"
  ATTICA = "attica"
  NBG = "nbg"
  EUROBANK = "eurobank"
  PIRAEUS = "piraeus"


BanksDocRoot = RootModel[Dict[Bank, List[HttpUrl]]]

bank_root_urls = BanksDocRoot.model_validate(
    {
        Bank.ALPHA: [
            "https://www.alpha.gr/el/idiotes/support-center/isxuon-timologio-kai-oroi-sunallagon"
        ],
        Bank.PIRAEUS: ["https://www.piraeusbank.gr/el/support/epitokia-deltia-timwn"],
        Bank.NBG: [
            "https://www.nbg.gr/el/footer/timologia-ergasiwn",
        ],
        Bank.EUROBANK: [
            "https://www.eurobank.gr/el/timologia",
        ],
    }
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}


def download_file(url: str, dest_path: str, chunk_size: int = 8192):
  """
  Streams a file from the given URL to the specified filesystem path.
  """
  with requests.get(url, headers=HEADERS, stream=True, timeout=15) as response:
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


def download_pdfs(bank_name: str, page_url: str, base_folder: str = "data_new"):
  """
  Scrapes all PDF links from the given page URL and downloads them into
  data_new/{bank_name}/
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
    if href.lower().endswith(".pdf"):
      full_url = urljoin(page_url, href)
      pdf_links.add(full_url)

  # Download each PDF
  for pdf_url in tqdm(
      sorted(pdf_links), desc=f"{bank_name} PDFs", unit="file", leave=False
  ):
    filename = os.path.basename(urlparse(pdf_url).path)
    dest_path = os.path.join(target_dir, filename)
    if os.path.exists(dest_path):
      os.remove(dest_path)

    try:
      download_file(pdf_url, dest_path)
    except Exception as e:
      print(f"[ERROR] Failed to download {pdf_url}: {e}")


def main():
  for bank_name, url in tqdm(bank_root_urls.root.items(), desc="Banks", unit="bank"):
    download_pdfs(bank_name.value, url.encoded_string())


if __name__ == "__main__":
  main()
