#!/usr/bin/env python3
"""
Script to extract text from PDFs in bank-specific subfolders and index them into a MeiliSearch instance.
Each document is tagged with a "bank" field corresponding to its parent folder.
"""
import os
from pathlib import Path
import argparse
import hashlib
import datetime

from meilisearch import Client, errors as meilisearch_errors
from meilisearch.models.task import TaskInfo

from tqdm.auto import tqdm
from generic_domain_model import GenericDocument
from domain_config import domain_manager
from doc_analysis import load_document_analysis

def wait_for_task(meili: Client, task: TaskInfo, desc: str = "", verbose: bool = True) -> TaskInfo:
  task_result = meili.wait_for_task(task.task_uid)
  if task_result.error:
    raise RuntimeError(
        f"Task {task.task_uid} ({desc}) failed: {task_result.error}")
  if verbose:
    print(f"{desc} completed successfully.")
  return task_result


def clean_index(meili: Client, index_name: str):
  index = meili.get_index(index_name)
  wait_for_task(meili, meili.delete_index(index.uid),
                desc=f"Deleting index '{index_name}'", verbose=False)


def swap_index(meili: Client, old_index_name: str, new_index_name: str):
  print(
      f"Swapping index '{old_index_name}' with new index '{new_index_name}'...")
  wait_for_task(meili, meili.swap_indexes([{
      "indexes": [old_index_name, new_index_name],
  }]), desc="Swapping indexes")
  print(f"Cleaning up index...")
  clean_index(meili, new_index_name)


def index_pdfs(meili: Client, root_dir: Path, index_name: str, batch_size: int = 10):
  """
  Walk through each subfolder in root_dir (each representing an entity), extract text from all PDFs,
  split them by page, add previous-page context, and index them into the specified MeiliSearch index in batches.
  """
  try:
    index = meili.get_index(index_name)
  except meilisearch_errors.MeilisearchApiError:
    print(f"Index '{index_name}' does not exist. Creating index...")
    wait_for_task(meili,
                  meili.create_index(uid=index_name, options={
                                     "primaryKey": "id"}),
                  desc=f"Create index '{index_name}'")
    index = meili.get_index(index_name)
    wait_for_task(meili,
                  index.update_filterable_attributes([
                      "entity", "bank", "category", "filename", 
                      "retrieved_from", "content_hash", "effective_date"
                  ]),
                  desc=f"Set filterable attributes for index '{index_name}'")

  print(
      f"Indexing PDFs from {root_dir} into MeiliSearch index '{index_name}'...")

  buffer = []
  tasks = []
  print()
  for entity_folder in tqdm(list(root_dir.iterdir()), desc="Entities", unit="entity", leave=True):
    if not entity_folder.is_dir():
      continue
    entity_name = entity_folder.name

    for pdf_file in tqdm(list(entity_folder.glob("*.pdf")), desc=f"  Processing PDFs in {entity_name}", unit="pdf", leave=False):
      if not pdf_file.is_file() or pdf_file.name.startswith("_"):
        continue

      try:
        doc_analysis = load_document_analysis(pdf_file, bank=entity_name)
        pages = doc_analysis.get_pages_as_text(indent_level=2)
        
        document_name_hash = hashlib.md5(pdf_file.stem.encode()).hexdigest()
        document_mtime = pdf_file.stat().st_mtime_ns

        for page_idx in tqdm(range(len(pages)), desc=f"    Converting Pages to GenericDocument in {pdf_file.name}", unit="page", leave=False):
          content = pages[page_idx]

          doc_id = f"{entity_name}_{document_name_hash}_{document_mtime}_p{page_idx}"
          doc = GenericDocument(
              id=doc_id,
              entity=entity_name,
              filename=pdf_file.name,
              path=str(pdf_file),
              page=page_idx+1,
              content=content,
              # Include DocumentAnalysis metadata
              retrieved_from=str(doc_analysis.retrieved_from) if doc_analysis.retrieved_from else None,
              retrieved_at=doc_analysis.retrieved_at.isoformat() if doc_analysis.retrieved_at else None,
              retrieved_etag=doc_analysis.retrieved_etag,
              bank=doc_analysis.bank,
              content_hash=doc_analysis.content_hash,
              category=doc_analysis.category,
              document_title=doc_analysis.document_title,
              effective_date=doc_analysis.effective_date.isoformat() if doc_analysis.effective_date else None,
          )
          buffer.append(doc.model_dump())

          # send batch if full
          if len(buffer) >= batch_size:
            tasks.append(index.add_documents(buffer, primary_key="id"))
            buffer.clear()
            
      except (FileNotFoundError, ValueError) as e:
        print(f"Warning: Could not load DocumentAnalysis for {pdf_file}: {e}")
        continue

  # index any remaining docs
  if buffer:
    print(f"Indexing final batch of {len(buffer)} docs...")
    tasks.append(index.add_documents(buffer))

  # wait for all tasks to complete
  for task in tasks:
    task_info = meili.wait_for_task(task.task_uid)
    if task_info.error:
      raise RuntimeError(f"Failed to index documents: {task_info.error}")


def index_exists(meili: Client, index_name: str) -> bool:
  """
  Check if the specified index exists in MeiliSearch.
  """
  try:
    meili.get_index(index_name)
    return True
  except meilisearch_errors.MeilisearchApiError:
    return False


def cleanup_indexes(meili: Client, index_name_prefix: str):
  """
  Clean up any indexes that start with the specified prefix.
  This is useful for removing temporary or old indexes.
  """
  indexes = meili.get_indexes({
      "limit": 1000
  })["results"]
  for index in tqdm(indexes, desc="Cleaning up indexes", unit="index"):
    if index.uid.startswith(index_name_prefix):
      clean_index(meili, index.uid)


def main():
  # Environment defaults
  default_url = os.environ.get("MEILI_URL", "")
  default_key = os.environ.get("MEILI_API_KEY", "")

  parser = argparse.ArgumentParser(
      description="Index bank PDFs into MeiliSearch")
  parser.add_argument(
      "--root-dir", type=Path, default=Path.cwd() / "data_new",
      help="Root directory containing entity-named subfolders with PDFs (default: ./data)"
  )
  parser.add_argument(
      "--meili-url", type=str, default=default_url,
      help="URL of the MeiliSearch instance (or set MEILI_URL env)"
  )
  parser.add_argument(
      "--api-key", type=str, default=default_key,
      help="API key for MeiliSearch (or set MEILI_API_KEY env)"
  )
  parser.add_argument(
      "--index-name", type=str, default="bankfees",
      help="Name of the MeiliSearch index to use or create"
  )
  parser.add_argument(
      "--batch-size", type=int, default=500,
      help="Number of documents to index in each batch"
  )
  args = parser.parse_args()

  meili = Client(args.meili_url, args.api_key)

  using_temporary_index = False
  if index_exists(meili, args.index_name):
    timestamp_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_index_name = f"{args.index_name}_new_{timestamp_now}"
    using_temporary_index = True
  else:
    output_index_name = args.index_name

  index_pdfs(
      meili=meili,
      root_dir=args.root_dir,
      index_name=output_index_name,
      batch_size=args.batch_size,
  )

  if using_temporary_index:
    swap_index(
        meili=meili,
        old_index_name=args.index_name,
        new_index_name=output_index_name,
    )

  cleanup_indexes(meili, f"{args.index_name}_new_")


if __name__ == "__main__":
  main()
