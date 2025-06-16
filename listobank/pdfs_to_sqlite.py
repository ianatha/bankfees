#!/usr/bin/env python3
"""Create a SQLite database containing all PDF files and their analysis JSON.

This script walks a directory tree, stores every PDF file as a BLOB and, if
available, the corresponding ``.analysis.json`` file as text. The resulting
SQLite database can then be bundled with the web application for offline use.
"""

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable

from tqdm.auto import tqdm


def iter_pdfs(root: Path) -> Iterable[Path]:
    """Yield all PDF files under ``root``."""
    return root.glob("**/*.pdf")


def store_documents(db_path: Path, pdf_files: Iterable[Path], root: Path) -> None:
    """Insert PDFs and optional analyses into the SQLite database."""
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                pdf BLOB,
                analysis TEXT
            )
            """
        )
        conn.commit()

        for pdf_file in tqdm(pdf_files, desc="Storing PDFs", unit="file"):
            rel_path = pdf_file.relative_to(root).as_posix()
            pdf_blob = pdf_file.read_bytes()
            analysis_file = pdf_file.with_suffix(".analysis.json")
            analysis_text = (
                analysis_file.read_text(encoding="utf-8") if analysis_file.is_file() else None
            )
            cur.execute(
                "INSERT OR REPLACE INTO documents(path, pdf, analysis) VALUES(?, ?, ?)",
                (rel_path, pdf_blob, analysis_text),
            )
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Bundle PDFs and analyses into a SQLite database")
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path.cwd() / "data_new",
        help="Root directory to search for PDF files (default: current directory)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path.cwd() / "ui" / Path("documents.sqlite"),
        help="Path to output SQLite database file (default: ./documents.sqlite)",
    )
    args = parser.parse_args()

    pdf_files = iter_pdfs(args.root_dir)
    store_documents(args.db_path, pdf_files, args.root_dir)
    print(f"Created database {args.db_path}")


if __name__ == "__main__":
    main()
