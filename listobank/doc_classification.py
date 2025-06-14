#!/usr/bin/env python3
import concurrent.futures
import datetime

from pydantic import BaseModel, Field
from doc_analysis import DocumentCategory, load_document_analysis
from tqdm import tqdm
from pathlib import Path
from gemini import create_gemini, generate_content
from domain_model import Categories

root_dir = Path.cwd() / "data_new"


PAGES_CONTEXT_LIMIT = 12

class DocumentLLMClassification(BaseModel):
  category: DocumentCategory = Field(
      ..., description="document category"
  )
  effective_date: datetime.datetime | None = Field(
      ..., description="date when the document becomes effective"
  )
  document_title: str | None = Field(
      description="title of the document, if available"
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
  prompt += "The text is divided into pages. The document should be classified in its entirety. In case the document doesn't contain enough information, you should also consult the filename to make a determination.\n"
  prompt += "If the document contains an effective date, it should be included in your response as the effective_date field. If there isn't one, omit that field.\n"
  prompt += "If you can discern a clear title for the document, it should be included in your response as the document_title field. If there isn't one, omit that field.\n"
  prompt += "\n"
  prompt += "The document is as follows:\n"
  prompt += "<Document>\n"
  prompt += "<FileName>" + file_name + "</FileName>\n"
  for i, page_text in enumerate(page_texts):
    prompt += f"<Page number=\"{i + 1}\">\n{strip_successive_newlines(page_text)}\n</Page>\n"
  prompt += "</Document>\n"
  return prompt


def process_pdf(gemini, pdf_file):
  if not pdf_file.is_file() or pdf_file.name.startswith("_"):
    return None

  doc_analysis = load_document_analysis(pdf_file)
  pages_text = doc_analysis.get_pages_as_text(indent_level=1)[:PAGES_CONTEXT_LIMIT]
  if not pages_text:
    print(f"Warning: No text extracted from {pdf_file.name}. Skipping...")
    return None

  prompt = classification_prompt(Categories, pdf_file.name, pages_text)
  llm_classification: DocumentLLMClassification = generate_content(
      gemini, prompt, response_schema=DocumentLLMClassification)
  doc_analysis.category = llm_classification.category
  if llm_classification.effective_date:
    doc_analysis.effective_date = llm_classification.effective_date
  if llm_classification.document_title:
    doc_analysis.document_title = llm_classification.document_title
  doc_analysis.save()
  return (f"{pdf_file.parent.name}/{pdf_file.name}", llm_classification.category)


def main():
  gemini = create_gemini()
  pdf_files = list(root_dir.glob("**/*.pdf"))
  with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(
        tqdm(executor.map(lambda pdf_file: process_pdf(gemini, pdf_file), pdf_files), total=len(pdf_files)))

  # convert list of tuples in results to a dictionary
  file_categories = {}
  for result in results:
    if result:
      fname, category = result
      file_categories[fname] = category

  print()
  print("Classification Results:")
  for file_path, category in file_categories.items():
    print(f"{file_path}: {category}")


if __name__ == "__main__":
  main()
