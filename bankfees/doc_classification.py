#!/usr/bin/env python3
import concurrent.futures
from enum import Enum
from pydantic import BaseModel, Field
import json
from utils import extract_pages_text
from tqdm import tqdm
from pathlib import Path
from gemini import create_gemini, generate_content

root_dir = Path.cwd() / "data_new"

categories = {
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
  # Unknown = "Unknown"


class DocumentClassification(BaseModel):
  category: DocumentCategory = Field(
      ..., description="document category"
  )


def strip_successive_newlines(text: str) -> str:
  """
  Strips successive newlines from the text, leaving only a single newline.
  """
  return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def classification_prompt(categories: dict[str, str], file_name: str, page_texts: list[str]) -> str:
  prompt = f"Classify the following text into one of the predefined categories:\n<ClassificationCategories>\n"
  for category, description in categories.items():
    prompt += f"<Category><Identifier>{category}</Identifier><Description>{description}</Description></Category>\n"
  prompt += "</ClassificationCategories>\n\n"
  prompt += "The text is divided into pages. The document should be classified in its entirety. In case the document doesn't contain enough information, you should also consult the filename to make a determination. You must respond with one of the Category Identifiers and nothing else.\n\n"
  prompt += "The document is as follows:\n"
  prompt += "<Document>\n"
  prompt += "<FileName>" + file_name + "</FileName>\n"
  for i, page_text in enumerate(page_texts):
    prompt += f"<Page number=\"{i + 1}\">\n{strip_successive_newlines(page_text)}\n</Page>\n"
  prompt += "</Document>\n"
  return prompt


def process_pdf(pdf_file):
  if not pdf_file.is_file() or pdf_file.name.startswith("_"):
    return None

  pages_text = extract_pages_text(pdf_file, indent_level=2, limit=5)
  if not pages_text:
    print(f"Warning: No text extracted from {pdf_file.name}. Skipping...")
    return None

  prompt = classification_prompt(categories, pdf_file.name, pages_text)
  category = generate_content(
      gemini, prompt, response_schema=DocumentClassification).category
  bank_name = pdf_file.parent.name
  fname = bank_name + "/" + pdf_file.name
  return (fname, category)


file_categories = {}
gemini = create_gemini()
pdf_files = list(root_dir.glob("**/*.pdf"))
with concurrent.futures.ThreadPoolExecutor() as executor:
  results = list(
      tqdm(executor.map(process_pdf, pdf_files), total=len(pdf_files)))

for result in results:
  if result:
    fname, category = result
    file_categories[fname] = category

print()
print("Classification results:")
for file_path, category in file_categories.items():
  print(f"{file_path}: {category}")

# write results to JSON file
output_file = root_dir / "document_classification_results.json"
with open(output_file, "w", encoding="utf-8") as f:
  json.dump(file_categories, f, ensure_ascii=False, indent=2)
print(f"\nClassification results saved to {output_file}")
