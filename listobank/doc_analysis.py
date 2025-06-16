import datetime
from hashlib import md5
from pydantic import BaseModel, Field, HttpUrl, ValidationError
from utils import extract_pages_text
from pathlib import Path
from domain_config import domain_manager


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
  bank: str = Field(
      ..., description="name of the bank from which the document was retrieved"
  )
  relative_file_path: Path = Field(
      ..., description="relative path to the source file from the project directory"
  )
  content_hash: str = Field(
      ..., description="hash of the source file for integrity checks"
  )
  category: str = Field(
      default=None, description="document category"
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
  page_embeddings: list[list[float]] | None = Field(
      default=None, description="embedding vectors for each page in pages_text"
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
                          bank: str,
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
      bank=bank,
      content_hash=content_hash,
      retrieved_etag=retrieved_etag,
      category=domain_manager.get_default_category() if domain_manager.config else "Uncategorized"
  )


def load_document_analysis(file_path: Path, bank: str | None = None) -> DocumentAnalysis:
  """
  Load document analysis results from a JSON file.
  """
  if not file_path.is_file():
    raise FileNotFoundError(f"File {file_path} does not exist.")
  analysis_file = file_path.with_suffix(".analysis.json")
  if not analysis_file.is_file():
    if bank is None:
      raise ValueError(f"No analysis file found for {file_path} and no bank specified")
    return new_document_analysis(file_path, retrieved_from=HttpUrl("file://unknown"), 
                                retrieved_at=datetime.datetime.now(datetime.timezone.utc), 
                                bank=bank)
  with analysis_file.open('r', encoding='utf-8') as f:
    try:
      result = DocumentAnalysis.model_validate_json(f.read())
      # validate content hash
      content_hash = md5(file_path.read_bytes()).hexdigest()
      if result.content_hash != content_hash:
        if bank is None:
          raise ValueError(f"Content hash mismatch for {file_path} and no bank specified for recreation")
        return new_document_analysis(file_path, retrieved_from=HttpUrl("file://unknown"), 
                                    retrieved_at=datetime.datetime.now(datetime.timezone.utc), 
                                    bank=bank)
      return result
    except ValidationError:
      if bank is None:
        raise ValueError(f"Invalid analysis file for {file_path} and no bank specified")
      return new_document_analysis(file_path, retrieved_from=HttpUrl("file://unknown"), 
                                  retrieved_at=datetime.datetime.now(datetime.timezone.utc), 
                                  bank=bank)
