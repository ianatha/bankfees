"use server";

import { MeiliSearch } from "meilisearch";
import {
  MEILI_INDEX,
  ENTITY_FIELD,
  CATEGORY_FIELD,
} from "@/lib/domain";
import { uniqBy } from "es-toolkit/array";

// Initialize the MeiliSearch client
const client = new MeiliSearch({
  host:
    process.env.NEXT_PUBLIC_MEILISEARCH_HOST ||
    "http://meilisearch.tenant-a9.svc.cluster.local:7700",
  apiKey: process.env.NEXT_PUBLIC_MEILISEARCH_API_KEY || "7FmUz2qYKDjjbhaZ3LkjNvNDkkhMUfew",
});

// The index where PDFs are stored
const index = client.index(MEILI_INDEX);

interface SearchHit {
  id: string;
  entity: string;
  filename: string;
  path: string;
  page: number;
  content: string;
  highlight: string;
  contextSnippets: string[];
  feeAmount?: string;
  category?: string;
}

export interface LibDocument {
  id: string;
  entity: string;
  filename: string;
  title: string;
  path: string;
  page?: number;
  effective_date?: Date;
  category: string;
}

const CONTEXT_LENGTH = 200;

export async function searchMeiliSearch(
  query: string,
  filters: string[] = []
): Promise<SearchHit[]> {
  try {
    const searchResults = await index.search(query, {
      limit: 100,
      attributesToHighlight: ["content"],
      highlightPreTag: "**",
      highlightPostTag: "**",
      attributesToCrop: ["content"],
      cropLength: 150,
      cropMarker: "...",
      filter: filters.length > 0 ? filters.join(" AND ") : undefined,
    });

    // Process the results to extract highlights and other information
    return searchResults.hits.map((hit: any) => {
      const contextSnippets = extractContextSnippets(hit.content, query, 3);

      // Extract the highlighted text from the content
      let highlight = "";
      if (hit._formatted && hit._formatted.content) {
        // Extract text around the highlighted terms
        const highlightedContent = hit._formatted.content;
        const matches = highlightedContent.match(/(.{0,80})\*\*.*?\*\*(.{0,80})/g);
        highlight = matches
          ? matches[0].replace(/\*\*/g, "")
          : highlightedContent.substring(0, CONTEXT_LENGTH);
      } else {
        highlight = hit.content.substring(0, CONTEXT_LENGTH) + "...";
      }

      // Try to extract fee amounts using regex
      let feeAmount;
      const feeRegex = /\$(\d+(?:,\d{3})*(?:\.\d{2})?)/g;
      const feeMatches = hit.content.match(feeRegex);
      if (feeMatches && feeMatches.length > 0) {
        feeAmount = feeMatches[0].substring(1); // Remove the $ sign
      }

      return {
        id: hit.id,
        entity: hit[ENTITY_FIELD],
        filename: hit.filename,
        path: hit.path,
        page: hit.page,
        content: hit.content,
        highlight,
        contextSnippets,
        feeAmount,
        category: hit[CATEGORY_FIELD],
      };
    });
  } catch (error) {
    console.error("MeiliSearch error:", error);
    throw new Error("Failed to search documents");
  }
}

// Helper function to extract context snippets around search terms
function extractContextSnippets(content: string, searchTerm: string, maxSnippets = 3): string[] {
  const snippets: string[] = [];
  const searchRegex = new RegExp(searchTerm, "gi");
  const matches = [...content.matchAll(searchRegex)];

  for (let i = 0; i < Math.min(matches.length, maxSnippets); i++) {
    const match = matches[i];
    const matchIndex = match.index || 0;
    const start = Math.max(0, matchIndex - 100);
    const end = Math.min(content.length, matchIndex + searchTerm.length + 100);

    let snippet = content.substring(start, end);

    // Add ellipsis if we're not at the beginning/end
    if (start > 0) snippet = "..." + snippet;
    if (end < content.length) snippet = snippet + "...";

    // Avoid duplicate snippets
    if (
      !snippets.some((existing) => existing.includes(snippet.substring(10, snippet.length - 10)))
    ) {
      snippets.push(snippet);
    }
  }

  return snippets.length > 0 ? snippets : [content.substring(0, 200) + "..."];
}

export async function getAllDocuments(): Promise<LibDocument[]> {
  try {
    // Get all documents with minimal fields
    const results = await index.search("", {
      limit: 1000,
      attributesToRetrieve: ["id", ENTITY_FIELD, CATEGORY_FIELD, "filename", "path", "page"],
    });

    // Process and deduplicate documents by path (since each page is a separate document)
    const uniqueDocuments = new Map<string, Document>();

    results.hits.forEach((hit: any) => {
      const documentPath = hit.path;

      if (!uniqueDocuments.has(documentPath)) {
        uniqueDocuments.set(documentPath, {
          id: hit.id,
          entity: hit[ENTITY_FIELD],
          filename: hit.filename,
          path: hit.path,
          page: hit.page,
          category: hit[CATEGORY_FIELD],
        });
      }
    });

    // Use es-toolkit utilities for deduplication and mapping
    // Assuming es-toolkit is installed and imported as:
    // import { uniqBy, map } from "es-toolkit/array";

    // Deduplicate by 'path' and map to Document type
    const uniqueDocuments = uniqBy(allDocuments.results, (doc: any) => doc.path);

    return uniqueDocuments.map((hit: any) => ({
      id: hit.id,
      bank: hit.bank,
      filename: hit.filename,
      path: hit.path,
      page: hit.page,
      title: hit.document_title ?? hit.filename,
      effective_date: hit.effective_date,
      category: hit.category,
    }));
  } catch (error) {
    console.error("MeiliSearch error:", error);
    throw new Error("Failed to fetch documents");
  }
}
