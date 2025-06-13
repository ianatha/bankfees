#!/usr/bin/env python3

# # gemini_bank_url_retriever.py
# Python tool to retrieve URLs for specific bank rate documents using Google’s Gemini AI with Google Search grounding

import os
import sys
import re
import asyncio
import aiohttp
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from pydantic import BaseModel
import json

# https://www.alpha.gr/el/idiotes/support-center/isxuon-timologio-kai-oroi-sunallagon

# https://www.piraeusbank.gr/el/support/epitokia-deltia-timwn
# https://www.piraeusbank.gr/-/jssmedia/Project/Piraeus/PiraeusBank/shared/Files/PiraeusBank/support/epitokia-deltia-timwn/price-02062025.pdf

class BankFeesDocument(BaseModel):
    document_name: str
    url: str
    description: str

# List of banks and their primary domains
BANKS = {
    "Alpha Bank": "alpha.gr",
    # "Τράπεζα Πειραιώς": "piraeusbank.gr",
    # "NBG": "nbg.gr",
    # "Eurobank Εργασίας": "eurobank.gr",
    # "Attica Bank": "atticabank.gr",
}

# Gemini model and plugin configuration
MODEL_NAME = "gemini-2.5-pro-preview-06-05"
GOOGLE_SEARCH_TOOL = Tool(
    google_search = GoogleSearch()
)

def configure_genai():
    """
    Configure the Google Generative AI (Gemini) client.
    Expects the API key in the environment variable GEMINI_API_KEY.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: Please set the GEMINI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    client = genai.Client(api_key=api_key)
    return client

async def _resolve_url(session: aiohttp.ClientSession, url: str) -> str:
    """
    Resolve a single redirect URL to its final destination.
    """
    print(f"Resolving URL: {url}")
    try:
        # Use GET to follow redirects and obtain final URL
        async with session.get(url, allow_redirects=True, timeout=10) as resp:
            return str(resp.url)
    except Exception:
        return url

def resolve_redirects(urls: list[str]) -> list[str]:
    """
    Resolve a list of redirect URLs in parallel and return the final URLs.
    """
    async def _resolve_all():
        async with aiohttp.ClientSession() as session:
            tasks = [_resolve_url(session, u) for u in urls]
            return await asyncio.gather(*tasks)
    try:
        return list(dict.fromkeys(asyncio.run(_resolve_all())))  # preserve order, dedupe
    except Exception as e:
        print(f"Warning: Redirect resolution failed: {e}", file=sys.stderr)
        return urls

# Present the results as a JSON array where each object represents a found relevant document and conforms to the following structure:

# <JsonItemFormat>
# {{
#   "document_name": "string",
#   "url": "string",
#   "description": "string"
# }}
# </JsonItemFormat>

# For the document_name, use the title of the document or the relevant part of the URL/search result snippet.
# For the url, provide the direct link to the PDF document.
# If no relevant PDF documents are found for the specified bank and domain, return an empty JSON array [].
# Respond only with the JSON array. Do not include any introductory text, explanations, or conversational filler.

def gemini_prompt(bank_name: str, bank_domain: str) -> str:
    return f"""
For the following Greek bank, give me a JSON array with all documents they have available on their website that list their pricing policies.
Relevant search terms are 'όροι τιμολόγησης', 'τιμοκατάλογος', 'χρεώσεις', 'Δελτίο Πληροφόρησης περί τελών', or similar keywords related to banking service fees.

Bank Name: "{bank_name}"
Bank Domain: "{bank_domain}"
"""

def search_grounded_urls(client: genai.Client, bank_name: str, bank_domain: str) -> list[str]:
    """
    Use Gemini with the Google Search plugin to retrieve URLs matching the query.
    Filters results to URLs containing the specified domain_filter.

    Args:
        query: The search query string.
        domain_filter: A substring that must be present in returned URLs.

    Returns:
        A list of unique URLs matching the domain filter.
    """
    prompt = gemini_prompt(bank_name, bank_domain)
    print("Using prompt:")
    print(prompt)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[GOOGLE_SEARCH_TOOL],
            response_modalities=["TEXT"],
            # response_mime_type="application/json",
            # response_schema=list[BankFeesDocument],
        ),
    )

    # Extract URLs from the response using Gemini's candidate content and grounding metadata
    urls = set()
    candidate = response.candidates[0] if response.candidates else None
    if candidate and hasattr(candidate, "grounding_metadata"):
        print("candidate")
        print(json.dumps(candidate.to_json_dict(), indent=2, ensure_ascii=False))
        print()
        print()
        print(candidate.content.parts[0].text)
        print()
        print()
        print(candidate.grounding_metadata)
        print()
        print()
        for chunk in candidate.grounding_metadata.grounding_chunks:
            if chunk.web and chunk.web.uri:
                urls.add(chunk.web.uri)
    return list(urls)


def retrieve_all_urls(client: genai.Client) -> dict[str, list[str]]:
    """
    Retrieve and resolve document URLs for all banks and document types.

    Returns:
        Dictionary mapping bank names to lists of resolved URLs.
    """
    all_urls = {}
    for bank_name, bank_domain in BANKS.items():
        raw_urls = []
        # for term in DOCUMENT_TERMS:
        print(f"Searching: '{bank_name}' in '{bank_domain}'...")
        try:
            urls = search_grounded_urls(client, bank_name, bank_domain)
            raw_urls.extend(urls)
        except Exception as e:
            print(e)
            print(f"Warning: search for '{bank_name}' failed: {e}", file=sys.stderr)
        # Resolve any redirector URLs in parallel
        resolved = resolve_redirects(raw_urls)
        all_urls[bank_name] = sorted(set(resolved))
    return all_urls


def main():
    """
    Command-line entry point. Prints gathered URLs to stdout.
    """
    client = configure_genai()
    results = retrieve_all_urls(client)

    for bank, urls in results.items():
        print(f"\n{bank}:")
        if urls:
            for url in urls:
                print(f" - {url}")
        else:
            print(" (No URLs found.)")

if __name__ == "__main__":
    main()
