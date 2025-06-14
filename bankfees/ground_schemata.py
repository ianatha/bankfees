from enum import Enum
from typing import Dict, List
from pydantic import RootModel, HttpUrl

class Bank(str, Enum):
  ALPHA = "alpha"
  ATTICA = "attica"
  NBG = "nbg"
  EUROBANK = "eurobank"
  PIRAEUS = "piraeus"

BanksDocumentRoots = RootModel[Dict[Bank, List[HttpUrl]]]
