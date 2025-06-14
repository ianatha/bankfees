import { MeiliSearch } from "meilisearch";

// Initialize the MeiliSearch client
const client = new MeiliSearch({
  host:
    process.env.NEXT_PUBLIC_MEILISEARCH_HOST ||
    "http://meilisearch.tenant-a9.svc.cluster.local:7700",
  apiKey: process.env.NEXT_PUBLIC_MEILISEARCH_API_KEY || "7FmUz2qYKDjjbhaZ3LkjNvNDkkhMUfew",
});

// The index where bank PDFs are stored (matching your Python script)
const index = client.index("bankfees");

interface SearchHit {
  id: string;
  bank: string;
  filename: string;
  path: string;
  page: number;
  content: string;
  highlight: string;
  contextSnippets: string[];
  feeAmount?: string;
}

interface Document {
  id: string;
  bank: string;
  filename: string;
  path: string;
  page?: number;
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
        bank: hit.bank,
        filename: hit.filename,
        path: hit.path,
        page: hit.page - 1,
        content: hit.content,
        highlight,
        contextSnippets,
        feeAmount,
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

export async function getAllDocuments(): Promise<Document[]> {
  try {
    // Get all documents with minimal fields
    const results = await index.search("", {
      limit: 1000,
      attributesToRetrieve: ["id", "bank", "filename", "path", "page"],
    });

    // Process and deduplicate documents by path (since each page is a separate document)
    const uniqueDocuments = new Map<string, Document>();

    results.hits.forEach((hit: any) => {
      const documentPath = hit.path;

      if (!uniqueDocuments.has(documentPath)) {
        uniqueDocuments.set(documentPath, {
          id: hit.id,
          bank: hit.bank,
          filename: hit.filename,
          path: hit.path,
          page: hit.page,
        });
      }
    });

    return Array.from(uniqueDocuments.values());
  } catch (error) {
    console.error("MeiliSearch error:", error);
    throw new Error("Failed to fetch documents");
  }
}
