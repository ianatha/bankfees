#!/usr/bin/env python3
"""Index PDF page embeddings into MeiliSearch using Google Gemini."""
import os
import argparse
import datetime
from pathlib import Path

from tqdm.auto import tqdm
from meilisearch import Client, errors as meilisearch_errors
from meilisearch.models.task import TaskInfo

from gemini import create_gemini
from doc_analysis import load_document_analysis
from generic_domain_model import GenericDocument

EMBEDDING_MODEL = "models/embedding-001"


def wait_for_task(meili: Client, task: TaskInfo, desc: str = "", verbose: bool = True) -> TaskInfo:
    task_result = meili.wait_for_task(task.task_uid)
    if task_result.error:
        raise RuntimeError(f"Task {task.task_uid} ({desc}) failed: {task_result.error}")
    if verbose:
        print(f"{desc} completed successfully.")
    return task_result


def embed_pages(gemini, pages: list[str]) -> list[list[float]]:
    embeddings = []
    for text in pages:
        res = gemini.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document",
        )
        embeddings.append(res["embedding"])
    return embeddings


def index_embeddings(meili: Client, root_dir: Path, index_name: str, batch_size: int = 100):
    try:
        index = meili.get_index(index_name)
    except meilisearch_errors.MeilisearchApiError:
        print(f"Index '{index_name}' does not exist. Creating index...")
        wait_for_task(meili, meili.create_index(uid=index_name, options={"primaryKey": "id"}), desc="Create index")
        index = meili.get_index(index_name)
        wait_for_task(meili, index.update_filterable_attributes(["entity"]), desc="Set filterable attributes")

    gemini = create_gemini()
    buffer = []
    tasks = []

    for analysis_path in tqdm(list(root_dir.glob("**/*.analysis.json")), desc="Analyses", unit="file"):
        pdf_path = analysis_path.with_suffix(".pdf")
        da = load_document_analysis(pdf_path)
        pages = da.get_pages_as_text(indent_level=1)
        if da.page_embeddings is None:
            da.page_embeddings = embed_pages(gemini, pages)
            da.save()
        for i, (text, embedding) in enumerate(zip(pages, da.page_embeddings)):
            doc = GenericDocument(
                id=f"{da.bank}_{da.content_hash}_p{i}",
                entity=da.bank,
                filename=pdf_path.name,
                path=str(pdf_path),
                page=i + 1,
                content=text,
                embedding=embedding,
            )
            buffer.append(doc.model_dump())
            if len(buffer) >= batch_size:
                tasks.append(index.add_documents(buffer, primary_key="id"))
                buffer.clear()

    if buffer:
        tasks.append(index.add_documents(buffer, primary_key="id"))

    for t in tasks:
        wait_for_task(meili, t, desc="Index batch", verbose=False)



def main():
    default_url = os.environ.get("MEILI_URL", "")
    default_key = os.environ.get("MEILI_API_KEY", "")

    parser = argparse.ArgumentParser(description="Add Gemini embeddings to MeiliSearch")
    parser.add_argument("--root-dir", type=Path, default=Path.cwd() / "data_new", help="Root directory with analysis JSONs")
    parser.add_argument("--meili-url", type=str, default=default_url, help="URL of the MeiliSearch instance")
    parser.add_argument("--api-key", type=str, default=default_key, help="API key for MeiliSearch")
    parser.add_argument("--index-name", type=str, default="documents", help="Name of the MeiliSearch index")
    parser.add_argument("--batch-size", type=int, default=100, help="Number of documents per batch")
    args = parser.parse_args()

    meili = Client(args.meili_url, args.api_key)
    index_embeddings(meili, args.root_dir, args.index_name, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
