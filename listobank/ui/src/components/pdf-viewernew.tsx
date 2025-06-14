"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { Document, Page, pdfjs } from "react-pdf"
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, RotateCw, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { BankLogo } from "@/components/bank-logo"
import { Badge } from "@/components/ui/badge"

import "react-pdf/dist/Page/AnnotationLayer.css"
import "react-pdf/dist/Page/TextLayer.css"

// Set up the worker for PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.mjs`

interface PdfViewerProps {
  documentUrl: string
  pageNumber: number
  searchTerm: string
  highlight: string
  bankName?: string
}

interface PageInfo {
  pageNumber: number
  height: number
  width: number
  offsetTop: number
}

export function PdfViewer({ documentUrl, pageNumber, searchTerm, bankName }: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null)
  const [currentPage, setCurrentPage] = useState<number>(pageNumber || 1)
  const [scale, setScale] = useState<number>(1.2)
  const [rotation, setRotation] = useState<number>(0)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [searchMatches, setSearchMatches] = useState<number>(0)
  const [currentMatch, setCurrentMatch] = useState<number>(0)
  const [pageInfos, setPageInfos] = useState<PageInfo[]>([])
  const [visiblePages, setVisiblePages] = useState<number[]>([])
  const [containerHeight, setContainerHeight] = useState<number>(0)

  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const documentRef = useRef<any>(null)
  const isScrollingToPage = useRef<boolean>(false)

  // Buffer for rendering pages around the visible area
  const PAGE_BUFFER = 2

  useEffect(() => {
    if (pageNumber && pageNumber !== currentPage) {
      scrollToPage(pageNumber)
    }
  }, [pageNumber, documentUrl])

  useEffect(() => {
    // Recalculate page positions when scale or rotation changes
    if (pageInfos.length > 0) {
      updatePagePositions()
    }
  }, [scale, rotation])

  const onDocumentLoadSuccess = useCallback(
    ({ numPages }: { numPages: number }) => {
      setNumPages(numPages)
      setIsLoading(false)
      // Initialize page infos with estimated heights
      const initialPageInfos: PageInfo[] = []
      let offsetTop = 0
      for (let i = 1; i <= numPages; i++) {
        const estimatedHeight = 800 * scale // Rough estimate
        initialPageInfos.push({
          pageNumber: i,
          height: estimatedHeight,
          width: 600 * scale,
          offsetTop,
        })
        offsetTop += estimatedHeight + 20 // 20px gap between pages
      }
      setPageInfos(initialPageInfos)
      setContainerHeight(offsetTop)
    },
    [scale],
  )

  const onPageLoadSuccess = useCallback(
    (page: any, pageNum: number) => {
      const viewport = page.getViewport({ scale, rotation })

      // Update page info with actual dimensions
      setPageInfos((prev) => {
        const newPageInfos = [...prev]
        const pageIndex = pageNum - 1
        if (pageIndex >= 0 && pageIndex < newPageInfos.length) {
          newPageInfos[pageIndex] = {
            ...newPageInfos[pageIndex],
            height: viewport.height,
            width: viewport.width,
          }

          // Recalculate offsets
          let offsetTop = 0
          for (let i = 0; i < newPageInfos.length; i++) {
            newPageInfos[i].offsetTop = offsetTop
            offsetTop += newPageInfos[i].height + 20
          }

          setContainerHeight(offsetTop)
        }
        return newPageInfos
      })

      // Highlight search terms after page loads
      if (searchTerm) {
        setTimeout(() => highlightSearchTermsOnPage(searchTerm, pageNum), 100)
      }
    },
    [scale, rotation, searchTerm],
  )

  const updatePagePositions = useCallback(() => {
    setPageInfos((prev) => {
      const newPageInfos = prev.map((info) => ({
        ...info,
        height: (info.height / scale) * scale, // Recalculate based on new scale
        width: (info.width / scale) * scale,
      }))

      let offsetTop = 0
      for (let i = 0; i < newPageInfos.length; i++) {
        newPageInfos[i].offsetTop = offsetTop
        offsetTop += newPageInfos[i].height + 20
      }

      setContainerHeight(offsetTop)
      return newPageInfos
    })
  }, [scale])

  const handleScroll = useCallback(() => {
    if (!scrollContainerRef.current || isScrollingToPage.current) return

    const scrollTop = scrollContainerRef.current.scrollTop
    const viewportHeight = scrollContainerRef.current.clientHeight

    // Find visible pages
    const visible: number[] = []
    let newCurrentPage = 1

    pageInfos.forEach((pageInfo) => {
      const pageTop = pageInfo.offsetTop
      const pageBottom = pageTop + pageInfo.height

      // Check if page is in viewport
      if (pageBottom >= scrollTop && pageTop <= scrollTop + viewportHeight) {
        visible.push(pageInfo.pageNumber)

        // Update current page to the first visible page
        if (newCurrentPage === 1 || pageInfo.pageNumber < newCurrentPage) {
          newCurrentPage = pageInfo.pageNumber
        }
      }
    })

    // Add buffer pages
    const minPage = Math.max(1, Math.min(...visible) - PAGE_BUFFER)
    const maxPage = Math.min(numPages || 1, Math.max(...visible) + PAGE_BUFFER)

    const pagesToRender: number[] = []
    for (let i = minPage; i <= maxPage; i++) {
      pagesToRender.push(i)
    }

    setVisiblePages(pagesToRender)
    setCurrentPage(newCurrentPage)
  }, [pageInfos, numPages])

  const scrollToPage = useCallback(
    (targetPage: number) => {
      if (!scrollContainerRef.current || !pageInfos.length) return

      const pageInfo = pageInfos.find((p) => p.pageNumber === targetPage)
      if (!pageInfo) return

      isScrollingToPage.current = true
      scrollContainerRef.current.scrollTo({
        top: pageInfo.offsetTop,
        behavior: "smooth",
      })

      // Reset the flag after scrolling
      setTimeout(() => {
        isScrollingToPage.current = false
      }, 1000)
    },
    [pageInfos],
  )

  const highlightSearchTermsOnPage = useCallback((term: string, pageNum: number) => {
    if (!term) return

    const pageContainer = document.querySelector(`[data-page-number="${pageNum}"]`)
    if (!pageContainer) return

    const textLayer = pageContainer.querySelector(".react-pdf__Page__textContent")
    if (!textLayer) return

    // Remove existing highlights
    const existingHighlights = textLayer.querySelectorAll(".search-highlight")
    existingHighlights.forEach((highlight) => {
      const parent = highlight.parentNode
      if (parent) {
        parent.replaceChild(document.createTextNode(highlight.textContent || ""), highlight)
        parent.normalize()
      }
    })

    // Find and highlight new matches
    const walker = document.createTreeWalker(textLayer, NodeFilter.SHOW_TEXT, null)
    const textNodes: Text[] = []
    let node
    while ((node = walker.nextNode())) {
      textNodes.push(node as Text)
    }

    const regex = new RegExp(`(${term})`, "gi")
    textNodes.forEach((textNode) => {
      const text = textNode.textContent || ""
      if (regex.test(text)) {
        const highlightedHTML = text.replace(
          regex,
          '<mark class="search-highlight bg-yellow-300 px-1 rounded">$1</mark>',
        )
        const wrapper = document.createElement("span")
        wrapper.innerHTML = highlightedHTML
        textNode.parentNode?.replaceChild(wrapper, textNode)
      }
    })
  }, [])

  const countAllMatches = useCallback(() => {
    if (!searchTerm) return 0

    let totalMatches = 0
    visiblePages.forEach((pageNum) => {
      const pageContainer = document.querySelector(`[data-page-number="${pageNum}"]`)
      if (pageContainer) {
        const highlights = pageContainer.querySelectorAll(".search-highlight")
        totalMatches += highlights.length
      }
    })

    return totalMatches
  }, [searchTerm, visiblePages])

  const navigateToMatch = useCallback(
    (direction: "next" | "prev") => {
      const allHighlights = document.querySelectorAll(".search-highlight")
      if (allHighlights.length === 0) return

      let newMatch = currentMatch
      if (direction === "next") {
        newMatch = currentMatch >= allHighlights.length ? 1 : currentMatch + 1
      } else {
        newMatch = currentMatch <= 1 ? allHighlights.length : currentMatch - 1
      }

      setCurrentMatch(newMatch)
      const targetHighlight = allHighlights[newMatch - 1]
      if (targetHighlight) {
        // Remove previous active highlight
        allHighlights.forEach((h) => h.classList.remove("ring-2", "ring-blue-500"))
        // Add active highlight
        targetHighlight.classList.add("ring-2", "ring-blue-500")

        // Scroll to the highlight
        targetHighlight.scrollIntoView({ behavior: "smooth", block: "center" })
      }
    },
    [currentMatch],
  )

  function changePage(offset: number) {
    const newPage = currentPage + offset
    if (newPage >= 1 && newPage <= (numPages || 1)) {
      scrollToPage(newPage)
    }
  }

  function zoomIn() {
    setScale((prevScale) => Math.min(prevScale + 0.2, 3))
  }

  function zoomOut() {
    setScale((prevScale) => Math.max(prevScale - 0.2, 0.6))
  }

  function rotate() {
    setRotation((prevRotation) => (prevRotation + 90) % 360)
  }

  // Update search matches count when visible pages change
  useEffect(() => {
    if (searchTerm && visiblePages.length > 0) {
      setTimeout(() => {
        const matches = countAllMatches()
        setSearchMatches(matches)
        if (matches > 0 && currentMatch === 0) {
          setCurrentMatch(1)
        }
      }, 200)
    }
  }, [visiblePages, searchTerm, countAllMatches])

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center p-3 border-b bg-white z-10">
        <div className="flex items-center gap-3">
          {bankName && <BankLogo bankName={bankName} size="sm" />}
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" onClick={() => changePage(-1)} disabled={currentPage <= 1}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm">
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
            <Button variant="outline" size="sm" onClick={() => navigateToMatch("prev")} disabled={searchMatches === 0}>
              ↑
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigateToMatch("next")} disabled={searchMatches === 0}>
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

      <div className="flex-1 bg-slate-100">
        {isLoading ? (
          <div className="flex items-center justify-center w-full h-full">
            <Skeleton className="h-[80%] w-[60%]" />
          </div>
        ) : (
          <div
            ref={scrollContainerRef}
            className="h-full overflow-auto pdf-scroll-container"
            onScroll={handleScroll}
            style={{ scrollBehavior: "smooth" }}
          >
            <div
              className="relative mx-auto"
              style={{
                height: containerHeight,
                width: Math.max(...pageInfos.map((p) => p.width)) || 600,
              }}
            >
              <Document
                ref={documentRef}
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
              >
                {visiblePages.map((pageNum) => {
                  const pageInfo = pageInfos.find((p) => p.pageNumber === pageNum)
                  if (!pageInfo) return null

                  return (
                    <div
                      key={pageNum}
                      data-page-number={pageNum}
                      className="absolute left-1/2 transform -translate-x-1/2"
                      style={{
                        top: pageInfo.offsetTop,
                      }}
                    >
                      <div className="shadow-lg bg-white mb-5">
                        <Page
                          pageNumber={pageNum}
                          scale={scale}
                          rotate={rotation}
                          renderTextLayer={true}
                          renderAnnotationLayer={true}
                          onLoadSuccess={(page) => onPageLoadSuccess(page, pageNum)}
                        />
                      </div>
                    </div>
                  )
                })}
              </Document>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
