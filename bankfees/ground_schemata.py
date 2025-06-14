from enum import Enum
from typing import Dict, List
from pydantic import RootModel, HttpUrl, BaseModel, Field

class Bank(str, Enum):
  ALPHA = "alpha"
  ATTICA = "attica"
  NBG = "nbg"
  EUROBANK = "eurobank"
  PIRAEUS = "piraeus"

BanksDocumentRoots = RootModel[Dict[Bank, List[HttpUrl]]]

class BankDocument(BaseModel):
  id: str = Field(..., description="Unique identifier for the document")
  bank: str = Field(..., description="Name of the bank (parent folder)")
  filename: str = Field(..., description="Name of the PDF file")
  path: str = Field(..., description="Full path to the PDF file")
  page: int = Field(..., description="Page number within the PDF")
  content: str = Field(..., description="Text content of the page")
