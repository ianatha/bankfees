"use client";

import type React from "react";

import { PdfViewer } from "@/components/pdf-viewer";
import { SearchResults } from "@/components/search-results";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSearchResults } from "@/hooks/use-search-results";
import { parseSearchInput } from "@/lib/utils";
import { Search } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export function SearchInterface() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedResult, setSelectedResult] = useState<{
    bankName: string;
    documentUrl: string;
    pageNumber: number;
    highlight: string;
  } | null>(null);

  const { results, isLoading, error, performSearch } = useSearchResults();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check if there's a document parameter in the URL
    const documentPath = searchParams.get("document");
    if (documentPath) {
      setSelectedResult({
        bankName: "",
        documentUrl: documentPath,
        pageNumber: 1,
        highlight: "",
      });
    }
  }, [searchParams]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      performSearch(searchQuery);
    }
  };

  const { query: highlightQuery } = parseSearchInput(searchQuery);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.5fr] gap-6">
      <div className="flex flex-col gap-6">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
            <Input
              type="search"
              placeholder="Search for fees (e.g., overdraft, wire transfer, ATM)"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                const newSearchQuery = e.target.value.trim();
                if (newSearchQuery.length === 0) {
                  performSearch(""); // Clear results on empty input
                } else if (newSearchQuery.length >= 2) {
                  performSearch(newSearchQuery); // Perform search on input change
                }
              }}
              className="pl-10"
            />
          </div>
          <Button type="submit">Αναζήτηση</Button>
        </form>

        <div className="bg-white rounded-lg shadow-sm border p-4">
          {isLoading && results.length === 0 ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-800"></div>
            </div>
          ) : error ? (
            <div className="text-red-500 p-4 text-center">{error}</div>
          ) : (
            <SearchResults
              updating={isLoading}
              results={results}
              onResultClick={setSelectedResult}
              searchQuery={searchQuery}
              highlightQuery={highlightQuery}
            />
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border h-[calc(100vh-12rem)] min-h-[500px]">
        {selectedResult ? (
          <PdfViewer
            documentUrl={selectedResult.documentUrl.replace(
              "/Users/iwa/ekpizo/bankfees/data/",
              "/api/file/"
            )}
            pageNumber={selectedResult.pageNumber}
            searchTerm={highlightQuery}
            highlight={selectedResult.highlight}
            bankName={selectedResult.bankName}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <Search className="h-12 w-12 mb-4" />
            <p className="text-lg">Search and select a result to view the PDF</p>
          </div>
        )}
      </div>
    </div>
  );
}
