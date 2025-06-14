import datetime
from enum import Enum
from hashlib import md5
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ValidationError
from utils import extract_pages_text
from pathlib import Path


class DocumentCategory(str, Enum):
  CustomerGuide = "CustomerGuide"
  DeltioPliroforisisPeriTelon = "DeltioPliroforisisPeriTelon"
  Disclosure = "Disclosure"
  GeneralTermsContract = "GeneralTermsContract"
  InterestRates = "InterestRates"
  # NeedsOCR = "NeedsOCR"
  PaymentFees = "PaymentFees"
  PriceList = "PriceList"
  PriceListExclusive = "PriceListExclusive"
  Uncategorized = "Uncategorized"


class DocumentAnalysis(BaseModel):
  retrieved_from: HttpUrl = Field(
      ..., description="URL from which the document was retrieved, if applicable"
  )
  retrieved_at: datetime.datetime = Field(
      ..., description="timestamp of when the document was retrieved"
  )
  retrieved_etag: str | None = Field(
      default=None, description="ETag of the document at the time of retrieval"
  )
  relative_file_path: Path = Field(
      ..., description="relative path to the source file from the project directory"
  )
  content_hash: str = Field(
      ..., description="hash of the source file for integrity checks"
  )
  category: DocumentCategory = Field(
      default=DocumentCategory.Uncategorized, description="document category"
  )
  document_title: str | None = Field(
      default=None, description="title of the document, if available"
  )
  effective_date: datetime.datetime | None = Field(
      default=None, description="date when the document becomes effective"
  )
  pages_text: list[str] | None = Field(
      default=None, description="text content of each page in the document"
  )

  def get_pages_as_text(self, indent_level: int = 0) -> list[str]:
    """
    Extracts and returns a list of text content for each page in the document.
    """
    if not self.pages_text:
      result = extract_pages_text(self.relative_file_path, indent_level=indent_level)
      if not result:
        raise ValueError(f"No text extracted from {self.relative_file_path}. "
                         "Ensure the file is a valid PDF and contains extractable text.")
      self.pages_text = result
      self.save()
      return result
    else:
      return self.pages_text

  def save(self):
    """
    Save the document analysis to a JSON file in the specified root directory.
    """
    analysis_file = self.relative_file_path.with_suffix(".analysis.json")
    with analysis_file.open('w', encoding='utf-8') as f:
      f.write(self.model_dump_json(indent=2, exclude_none=True))


def new_document_analysis(file_path: Path,
                          retrieved_from: HttpUrl,
                          retrieved_at: datetime.datetime,
                          retrieved_etag: str | None = None
                          ) -> DocumentAnalysis:
  """
  Create a new DocumentAnalysis object with the content hash and default category.
  """
  if not file_path.is_file():
    raise FileNotFoundError(f"File {file_path} does not exist.")
  content_hash = md5(file_path.read_bytes()).hexdigest()
  return DocumentAnalysis(
      relative_file_path=file_path,
      retrieved_from=HttpUrl(retrieved_from),
      retrieved_at=retrieved_at,
      content_hash=content_hash,
      category=DocumentCategory.Uncategorized
  )


def load_document_analysis(file_path: Path) -> DocumentAnalysis:
  """
  Load document analysis results from a JSON file.
  """
  if not file_path.is_file():
    raise FileNotFoundError(f"File {file_path} does not exist.")
  analysis_file = file_path.with_suffix(".analysis.json")
  if not analysis_file.is_file():
    return new_document_analysis(file_path)
  with analysis_file.open('r', encoding='utf-8') as f:
    try:
      result = DocumentAnalysis.model_validate_json(f.read())
      # validate content hash
      content_hash = md5(file_path.read_bytes()).hexdigest()
      if result.content_hash != content_hash:
        return new_document_analysis(file_path)
      return result
    except ValidationError as e:
      return None
