"use client";

import { BankLogo } from "@/components/bank-logo";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronLeft, ChevronRight, RotateCw, Search, ZoomIn, ZoomOut } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Document, Outline, Page, pdfjs } from "react-pdf";

import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import { CustomTextRenderer } from "react-pdf/src/shared/types.js";
import { ScrollIndicator } from "./scroll-indicator";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";

// Set up the worker for PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.mjs`;

interface PdfViewerProps {
  documentUrl: string;
  pageNumber: number;
  searchTerm: string;
  highlight: string;
  bankName?: string;
}

export function PdfViewer({ documentUrl, pageNumber, searchTerm, bankName }: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(pageNumber || 1);
  const [scale, setScale] = useState<number>(1.2);
  const [rotation, setRotation] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchMatches, setSearchMatches] = useState<number>(0);
  const [currentMatch, setCurrentMatch] = useState<number>(0);

  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const pageRef = useRef<HTMLDivElement>(null);
  const lastScrollTop = useRef<number>(0);
  const scrollTimeout = useRef<NodeJS.Timeout>(undefined);

  useEffect(() => {
    if (pageNumber) {
      setCurrentPage(pageNumber);
    }
  }, [pageNumber, documentUrl]);

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setIsLoading(false);
  }, []);

  function changePage(offset: number) {
    const newPage = currentPage + offset;
    if (newPage >= 1 && newPage <= (numPages || 1)) {
      setCurrentPage(newPage);
    }
  }

  function zoomIn() {
    setScale((prevScale) => Math.min(prevScale + 0.2, 3));
  }

  function zoomOut() {
    setScale((prevScale) => Math.max(prevScale - 0.2, 0.6));
  }

  function rotate() {
    setRotation((prevRotation) => (prevRotation + 90) % 360);
  }

  function navigateToMatch(direction: "next" | "prev") {
    const highlights = document.querySelectorAll(".search-highlight");
    if (highlights.length === 0) return;

    let newMatch = currentMatch;
    if (direction === "next") {
      newMatch = currentMatch >= highlights.length ? 1 : currentMatch + 1;
    } else {
      newMatch = currentMatch <= 1 ? highlights.length : currentMatch - 1;
    }

    setCurrentMatch(newMatch);
    const targetHighlight = highlights[newMatch - 1];
    if (targetHighlight) {
      targetHighlight.scrollIntoView({ behavior: "smooth", block: "center" });

      // Remove previous active highlight
      highlights.forEach((h) => h.classList.remove("ring-2", "ring-blue-500"));
      // Add active highlight
      targetHighlight.classList.add("ring-2", "ring-blue-500");
    }
  }

  // const handleScroll = useCallback(
  //   (e: Event) => {
  //     if (!scrollContainerRef.current || !numPages) return;

  //     const container = scrollContainerRef.current;
  //     const scrollTop = container.scrollTop;
  //     const scrollHeight = container.scrollHeight;
  //     const clientHeight = container.clientHeight;

  //     // Clear existing timeout
  //     if (scrollTimeout.current) {
  //       clearTimeout(scrollTimeout.current);
  //     }

  //     // Define thresholds for page navigation
  //     const bottomThreshold = scrollHeight - clientHeight - 30;
  //     const topThreshold = 30;

  //     // Set a timeout to check for page navigation after scroll stops
  //     scrollTimeout.current = setTimeout(() => {
  //       // Navigate to next page when scrolled to bottom
  //       if (scrollTop >= bottomThreshold && currentPage < numPages) {
  //         setCurrentPage((prev) => prev + 1);
  //       } else if (scrollTop <= topThreshold && currentPage > 1) {
  //         setCurrentPage((prev) => prev - 1);
  //       }
  //     }, 200);

  //     lastScrollTop.current = scrollTop;
  //   },
  //   [currentPage, numPages]
  // );

  // Add scroll event listener
  // useEffect(() => {
  //   const container = scrollContainerRef.current;
  //   if (!container) return;

  //   container.addEventListener("scroll", handleScroll, { passive: true });

  //   return () => {
  //     container.removeEventListener("scroll", handleScroll);
  //     if (scrollTimeout.current) {
  //       clearTimeout(scrollTimeout.current);
  //     }
  //   };
  // }, [handleScroll]);

  // Reset scroll position when page changes
  // useEffect(() => {
  //   if (scrollContainerRef.current) {
  //     const container = scrollContainerRef.current;
  //     // Set scroll to middle to avoid immediate re-triggering
  //     setTimeout(() => {
  //       if (container.scrollHeight > container.clientHeight) {
  //         container.scrollTop = Math.max(0, (container.scrollHeight - container.clientHeight) / 2);
  //       }
  //     }, 100);
  //   }
  // }, [currentPage]);

  function highlightPattern(text: string, pattern: string) {
    if (!pattern || pattern.length === 0) return text;
    return text.replace(pattern, (match) => {
      return `<mark class="bg-yellow-300/80 text-transparent px-1 rounded">${match}</mark>`;
    });
  }

  const textRenderer: CustomTextRenderer = useCallback(
    (props) => highlightPattern(props.str, searchTerm),
    [searchTerm]
  );

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center p-3 border-b bg-blue-400 z-10">
        <div className="flex items-center gap-3">
          {bankName && <BankLogo bankName={bankName} size="sm" />}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => changePage(-1)}
              disabled={currentPage <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm whitespace-nowrap">
              Page {currentPage} of {numPages || "..."}
            </span>
            <Button
              variant="outline"
              size="icon"
              onClick={() => changePage(1)}
              disabled={!numPages || currentPage >= numPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Search matches navigation */}
        {searchTerm && searchMatches > 0 && (
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              <Search className="h-3 w-3 mr-1" />
              {currentMatch} of {searchMatches}
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateToMatch("prev")}
              disabled={searchMatches === 0}
            >
              ↑
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateToMatch("next")}
              disabled={searchMatches === 0}
            >
              ↓
            </Button>
          </div>
        )}

        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={zoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm w-16 text-center">{Math.round(scale * 100)}%</span>
          <Button variant="outline" size="icon" onClick={zoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={rotate}>
            <RotateCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* <div className="px-3 py-1 bg-slate-50 border-b text-xs text-slate-500 text-center">
        Scroll to navigate between pages • Use buttons for precise control
      </div> */}

      {/* <div */}
        {/* ref={scrollContainerRef} */}
        {/* // className="bg-red-600 h-full" */}
        {/* // className="flex-1 overflow-auto flex justify-center p-4 bg-slate-100 scroll-smooth" */}
      {/* > */}
        {isLoading && (
          <div className="flex items-center justify-center w-full h-full">
            <Skeleton className="h-[80%] w-[60%]" />
          </div>
        )}
        {/* <div ref={pageRef}> */}
          <Document
          className={"h-full"}
            file={documentUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={
              <div className="flex items-center justify-center w-full h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-800"></div>
              </div>
            }
            error={
              <div className="flex items-center justify-center w-full h-full text-red-500">
                Failed to load PDF. Please try again.
              </div>
            }
            onItemClick={(e) => {
              // Prevent default click behavior on the PDF
              alert(JSON.stringify(e));
            }}
          >
            <div className="bg-red-700 h-full items-center flex-1">
            {numPages && (
              <>
              <AutoSizer>
                {({ width, height }) => (
                  <FixedSizeList
                    height={height}
                    itemCount={numPages || 0}
                    itemSize={height}
                    width={width}
                  >
                    {({ index, style }) => (
                      <div style={style}>
                        <Page
                          pageIndex={index}
                          scale={scale}
                          rotate={rotation}
                          renderTextLayer={true}
                          renderAnnotationLayer={true}
                          className="shadow-lg transition-opacity duration-300 mb-4"
                          customTextRenderer={textRenderer}
                        />
                      </div>
                    )}
                  </FixedSizeList>
                )}
              </AutoSizer>
              </>
            )}
            </div>
            {/* Array.from({ length: numPages }, (_, i) => (
                <Page
                  pageIndex={i}
                  scale={scale}
                  rotate={rotation}
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                  className="shadow-lg transition-opacity duration-300 mb-4"
                  customTextRenderer={textRenderer}
                />
              ))} */}
          </Document>
        {/* </div> */}
      {/* </div> */}

      {/* Navigation hints with scroll indicator */}
      {/* <div className="px-3 py-2 bg-white border-t text-xs text-slate-400">
        <div className="flex justify-between items-center mb-2">
          <span>Scroll to navigate • Zoom: {Math.round(scale * 100)}%</span>
          {numPages && (
            <span>
              {currentPage > 1 && "↑ Previous page"} {currentPage < numPages && "↓ Next page"}
            </span>
          )}
        </div>
        {numPages && <ScrollIndicator currentPage={currentPage} totalPages={numPages} />}
      </div> */}
    </div>
  );
}
