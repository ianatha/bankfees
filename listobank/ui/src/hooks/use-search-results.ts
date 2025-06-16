"use client";

import { searchMeiliSearch } from "@/lib/meilisearch";
import { parseSearchInput } from "@/lib/utils";
import { useState } from "react";

interface SearchResult {
  entityName: string;
  documentName: string;
  documentUrl: string;
  pageNumber: number;
  highlight: string;
  contextSnippets: string[];
  feeAmount?: string;
  category?: string;
}

interface EntityGroup {
  entityName: string;
  results: SearchResult[];
}

export function useSearchResults() {
  const [results, setResults] = useState<EntityGroup[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const performSearch = async (input: string) => {
    setIsLoading(true);
    setError(null);

    const { query, filters } = parseSearchInput(input);

    if (query.trim() === "" && filters.length === 0) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    try {
      const searchResults = await searchMeiliSearch(query, filters);

      // Group results by entity
      const groupedByEntity: Record<string, SearchResult[]> = {};

      searchResults.forEach((hit) => {
        const key = hit.entity;
        if (!groupedByEntity[key]) {
          groupedByEntity[key] = [];
        }

        groupedByEntity[key].push({
          entityName: hit.entity,
          documentName: hit.filename,
          documentUrl: hit.path,
          pageNumber: hit.page,
          highlight: hit.highlight,
          contextSnippets: hit.contextSnippets,
          feeAmount: hit.feeAmount,
          category: hit.category,
        });
      });

      // Convert to array format
      const entityGroups: EntityGroup[] = Object.keys(groupedByEntity).map((name) => ({
        entityName: name,
        results: groupedByEntity[name],
      }));

      // Sort entities alphabetically
      entityGroups.sort((a, b) => a.entityName.localeCompare(b.entityName));

      setResults(entityGroups);
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
