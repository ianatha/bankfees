"use client";

import type React from "react";

import { PdfViewer } from "@/components/pdf-viewer";
import { SearchResults } from "@/components/search-results";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useSearchResults } from "@/hooks/use-search-results";
import { parseSearchInput } from "@/lib/utils";
import { Filter, Search } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export function SearchInterface() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBanks, setSelectedBanks] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedResult, setSelectedResult] = useState<{
    bankName: string;
    documentUrl: string;
    pageNumber: number;
    highlight: string;
  } | null>(null);

  const { results, isLoading, error, performSearch } = useSearchResults();
  const searchParams = useSearchParams();

  const allBanks = ["alpha", "attica", "eurobank", "nbg", "piraeus"];
  const allCategories = [
    "PriceList",
    "CustomerGuide",
    "DeltioPliroforisisPeriTelon",
    "Disclosure",
    "GeneralTermsContract",
    "InterestRates",
    "PaymentFees",
    "PriceListExclusive",
  ];

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

  const extractBanks = (input: string) => {
    const bankRegex = /bank:("[^"]+"|\S+)/gi;
    return [...input.matchAll(bankRegex)].map((m) => m[1].replace(/^"|"$/g, ""));
  };

  const maybePerformSearch = (value: string) => {
    const { query } = parseSearchInput(value);
    if (query.trim().length === 0) {
      performSearch("");
    } else if (query.trim().length >= 2) {
      performSearch(value);
    }
  };

  const toggleBankSelection = (bank: string) => {
    setSelectedBanks((prev) => {
      const newBanks = prev.includes(bank) ? prev.filter((b) => b !== bank) : [...prev, bank];

      const baseQuery = searchQuery.replace(/bank:("[^"]+"|\S+)/gi, "").trim();
      const newQuery = `${baseQuery} ${newBanks.map((b) => `bank:${b}`).join(" ")}`.trim();

      setSearchQuery(newQuery);
      maybePerformSearch(newQuery);

      return newBanks;
    });
  };

  const toggleCategorySelection = (category: string) => {
    setSelectedCategories((prev) => {
      const newCategories = prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category];

      const baseQuery = searchQuery.replace(/category:("[^"]+"|\S+)/gi, "").trim();
      const newQuery = `${baseQuery} ${newCategories.map((c) => `category:${c}`).join(" ")}`.trim();

      setSearchQuery(newQuery);
      maybePerformSearch(newQuery);

      return newCategories;
    });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    maybePerformSearch(searchQuery);
  };

  const { query: highlightQuery } = parseSearchInput(searchQuery);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.5fr] gap-6">
      <div className="flex flex-col gap-6">
        <form onSubmit={handleSearch} className="flex gap-2 items-start">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
            <Input
              type="search"
              placeholder="Search for fees (e.g., overdraft, wire transfer, ATM)"
              value={searchQuery}
              onChange={(e) => {
                const value = e.target.value;
                setSearchQuery(value);
                setSelectedBanks(extractBanks(value));
                maybePerformSearch(value);
              }}
              className="pl-10"
            />
          </div>
          <Popover>
            <PopoverTrigger asChild>
              <Button type="button" variant="outline" className="shrink-0">
                <Filter className="h-4 w-4" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto" align="start">
              <div className="grid grid-cols-2">
                <div className="flex flex-col gap-2">
                  {allBanks.map((bank) => (
                    <label key={bank} className="flex items-center gap-2 text-sm capitalize">
                      <Checkbox
                        checked={selectedBanks.includes(bank)}
                        onCheckedChange={() => toggleBankSelection(bank)}
                        id={`bank-${bank}`}
                      />
                      {bank}
                    </label>
                  ))}
                </div>
                <div className="flex flex-col gap-2">
                  {allCategories.map((category) => (
                    <label key={category} className="flex items-center gap-2 text-sm capitalize">
                      <Checkbox
                        checked={selectedCategories.includes(category)}
                        onCheckedChange={() => toggleCategorySelection(category)}
                        id={`category-${category}`}
                      />
                      {category}
                    </label>
                  ))}
                </div>
              </div>
            </PopoverContent>
          </Popover>
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
            documentUrl={`/api/file/${selectedResult.documentUrl
              .split('/')
              .map(encodeURIComponent)
              .join('/')}`}
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
