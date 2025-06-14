from pathlib import Path
from PyPDF2 import PdfReader
from tqdm.auto import tqdm

def extract_pages_text(pdf_path: Path, indent_level: int, limit: int = 0) -> list[str]:
  """
  Extracts and returns a list of text content for each page in the PDF file.
  """
  reader = PdfReader(str(pdf_path))
  indentation = "  " * indent_level
  pages = reader.pages[:limit] if limit != 0 else reader.pages
  return [page.extract_text() or "" for page in tqdm(pages, desc=f"{indentation}Extracting text from {pdf_path.name}", unit="page", leave=False)]
