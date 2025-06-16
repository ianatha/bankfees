"use client";

import { BankLogo } from "@/components/bank-logo";
import { HighlightedText } from "@/components/highlighted-text";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronDown, ChevronRight, FileText, MoreHorizontal } from "lucide-react";
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

interface SearchResultsProps {
  updating?: boolean;
  results: EntityGroup[];
  onResultClick: (result: SearchResult) => void;
  searchQuery: string; // original user input
  highlightQuery: string; // parsed query used for highlighting
}

export function SearchResults({
  updating,
  results,
  onResultClick,
  searchQuery,
  highlightQuery,
}: SearchResultsProps) {
  const [openEntities, setOpenEntities] = useState<string[]>([]);
  const [expandedResults, setExpandedResults] = useState<string[]>([]);

  const toggleEntity = (entity: string) => {
    setOpenEntities((prev) =>
      prev.includes(entity) ? prev.filter((name) => name !== entity) : [...prev, entity]
    );
  };

  const toggleResultExpansion = (resultId: string) => {
    setExpandedResults((prev) =>
      prev.includes(resultId) ? prev.filter((id) => id !== resultId) : [...prev, resultId]
    );
  };

  if (results.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        {searchQuery
          ? "Δεν βρέθηκαν αποτελέσματα. Δοκιμάστε διαφορετικό όρο αναζήτησης."
          : "Εισάγετε όρους αναζήτησης για να βρείτε αναφορές στα έγγραφα."}
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Αποτελέσματα Αναζήτησης</h2>
        {updating && (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-slate-800"></div>
        )}
        <Badge variant="outline">
          {results.reduce((acc, g) => acc + g.results.length, 0)} matches
        </Badge>
      </div>

      <ScrollArea className="h-[calc(100vh-20rem)] pr-4">
        <div className="space-y-4">
          {results.map((group) => (
            <Collapsible
              key={group.entityName}
              open={openEntities.includes(group.entityName)}
              onOpenChange={() => toggleEntity(group.entityName)}
              className="border rounded-md overflow-hidden"
            >
              <CollapsibleTrigger asChild>
                <Button
                  variant="ghost"
                  className="w-full flex justify-between items-center p-3 h-auto"
                >
                  <div className="flex items-center gap-2 font-medium">
                    {openEntities.includes(group.entityName) ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                    <BankLogo bankName={group.entityName} size="sm" />
                    {group.entityName}
                  </div>
                  <Badge variant="secondary">{group.results.length}</Badge>
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="divide-y">
                  {group.results.map((result, idx) => {
                    const resultId = `${result.documentName}-${result.pageNumber}-${idx}`;
                    const isExpanded = expandedResults.includes(resultId);

                    return (
                      <div key={resultId} className="p-4 hover:bg-slate-50">
                        <div
                          className="flex items-start gap-3 cursor-pointer"
                          onClick={() => onResultClick(result)}
                        >
                          <FileText className="h-4 w-4 mt-1 text-slate-400 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-2">
                              <div>
                                <div className="font-medium text-sm">{result.documentName}</div>
                                <div className="text-xs text-slate-500">
                                  Page {result.pageNumber}
                                </div>
                              </div>
                              {result.feeAmount && (
                                <Badge className="ml-2" variant="outline">
                                  ${result.feeAmount}
                                </Badge>
                              )}
                            </div>

                            {/* Primary context snippet */}
                            <div className="text-sm mb-2">
                              <HighlightedText text={result.highlight} searchTerm={highlightQuery} />
                            </div>

                            {/* Additional context snippets */}
                            {result.contextSnippets.length > 1 && (
                              <div className="space-y-2">
                                {isExpanded
                                  ? result.contextSnippets.slice(1).map((snippet, snippetIdx) => (
                                      <div
                                        key={snippetIdx}
                                        className="text-sm text-slate-600 pl-4 border-l-2 border-slate-200"
                                      >
                                        <HighlightedText text={snippet} searchTerm={highlightQuery} />
                                      </div>
                                    ))
                                  : result.contextSnippets.length > 1 && (
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        className="h-6 px-2 text-xs text-slate-500"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          toggleResultExpansion(resultId);
                                        }}
                                      >
                                        <MoreHorizontal className="h-3 w-3 mr-1" />
                                        Show {result.contextSnippets.length - 1} more context
                                        {result.contextSnippets.length > 2 ? "s" : ""}
                                      </Button>
                                    )}

                                {isExpanded && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 px-2 text-xs text-slate-500"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleResultExpansion(resultId);
                                    }}
                                  >
                                    Show less
                                  </Button>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
