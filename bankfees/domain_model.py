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

BankRootUrls = BanksDocumentRoots.model_validate(
    {
        Bank.ALPHA: [
            "https://www.alpha.gr/el/idiotes/support-center/isxuon-timologio-kai-oroi-sunallagon"
        ],
		Bank.ATTICA: [
			"https://www.atticabank.gr/el/eidikoi-oroi-trapezikon-ergasion-timologio-ergasion/",
			"https://www.atticabank.gr/el/genikoi-oroi-synallagon/",
		],
        Bank.PIRAEUS: [
			"https://www.piraeusbank.gr/el/support/epitokia-deltia-timwn",
			"https://www.piraeusbank.gr/el/support/synallaktikoi-oroi",
		],
        Bank.NBG: [
            "https://www.nbg.gr/el/footer/timologia-ergasiwn",
			"https://www.nbg.gr/el/footer/deltio-plhroforhshs-peri-telwn",
        ],
        Bank.EUROBANK: [
            "https://www.eurobank.gr/el/timologia",
			"https://www.eurobank.gr/el/oroi-sunallagon",
        ],
    }
)

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

Categories = {
    "CustomerGuide": "Οδηγίες για την διευκόλυνση των πελατών της τράπεζας κατά τη διενέργεια ραντεβού ή συνναλαγών",
    "DeltioPliroforisisPeriTelon": "Έγγραφα με τίτλο \"Δελτίο Πληροφόρησης περί Τελών\"",
    "Disclosure": "Έγγραφα ενημέρωσης πελάτη για υποχρεώσεις, κινδύνους και διαφάνεια όρων (αποποιήσεις ευθυνών, γνωστοποιήσεις), εκτός από Δελτία Πληροφόρησης περί Τελών",
    "GeneralTermsContract": "Γενικοί όροι σύμβασης και συναλλαγών μεταξύ πελάτη και τράπεζας",
    "InterestRates": "Έγγραφα που περιέχουν πληροφορίες για επιτόκια καταθέσεων, δανείων και άλλων τραπεζικών προϊόντων",
    # "NeedsOCR": "Έγγραφα με ελάχιστους ή καθόλου αναγνώσιμους χαρακτήρες, που απαιτούν OCR για εξαγωγή κειμένου",
    "PaymentFees": "Πίνακες τελών και προμηθειών για πληρωμές, μεταφορές και υπηρεσίες σε συγκεκριμένους παραλήπτες",
    "PriceList": "Γενικός τιμοκατάλογος τραπεζικών προϊόντων και υπηρεσιών με βασικές χρεώσεις και επιτόκια",
    "PriceListExclusive": "Ειδικός τιμοκατάλογος για premium προϊόντα/υπηρεσίες (π.χ. private banking, gold accounts)",
    # "Unknown": "Έγγραφο μη κατηγοριοποιημένο ή αδιευκρίνιστης κατηγορίας",
}

class BankDocument(BaseModel):
  id: str = Field(..., description="Unique identifier for the document")
  bank: str = Field(..., description="Name of the bank (parent folder)")
  filename: str = Field(..., description="Name of the PDF file")
  path: str = Field(..., description="Full path to the PDF file")
  page: int = Field(..., description="Page number within the PDF")
  content: str = Field(..., description="Text content of the page")
