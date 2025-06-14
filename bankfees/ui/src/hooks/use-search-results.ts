"use client";

import { searchMeiliSearch } from "@/lib/meilisearch";
import { useState } from "react";

interface SearchResult {
  bankName: string;
  documentName: string;
  documentUrl: string;
  pageNumber: number;
  highlight: string;
  contextSnippets: string[];
  feeAmount?: string;
}

interface BankGroup {
  bankName: string;
  results: SearchResult[];
}

export function useSearchResults() {
  const [results, setResults] = useState<BankGroup[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const performSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);

    if (query.trim() === "") {
      setResults([]);
      setIsLoading(false);
      return;
    }

    try {
      const searchResults = await searchMeiliSearch(query);

      // Group results by bank
      const groupedByBank: Record<string, SearchResult[]> = {};

      searchResults.forEach((hit) => {
        if (!groupedByBank[hit.bank]) {
          groupedByBank[hit.bank] = [];
        }

        groupedByBank[hit.bank].push({
          bankName: hit.bank,
          documentName: hit.filename,
          documentUrl: hit.path,
          pageNumber: hit.page,
          highlight: hit.highlight,
          contextSnippets: hit.contextSnippets,
          feeAmount: hit.feeAmount,
        });
      });

      // Convert to array format
      const bankGroups: BankGroup[] = Object.keys(groupedByBank).map((bankName) => ({
        bankName,
        results: groupedByBank[bankName],
      }));

      // Sort banks alphabetically
      bankGroups.sort((a, b) => a.bankName.localeCompare(b.bankName));

      setResults(bankGroups);
    } catch (err) {
      console.error("Search error:", err);
      setError("An error occurred while searching. Please try again.");
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    results,
    isLoading,
    error,
    performSearch,
  };
}
