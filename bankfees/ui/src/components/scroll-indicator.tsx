"use client"

import { useEffect, useState } from "react"

interface ScrollIndicatorProps {
  currentPage: number
  totalPages: number
  className?: string
}

export function ScrollIndicator({ currentPage, totalPages, className = "" }: ScrollIndicatorProps) {
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const container = document.querySelector(".pdf-scroll-container")
      if (!container) return

      const scrollTop = container.scrollTop
      const scrollHeight = container.scrollHeight - container.clientHeight
      const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0

      setScrollProgress(Math.min(100, Math.max(0, progress)))
    }

    const container = document.querySelector(".pdf-scroll-container")
    if (container) {
      container.addEventListener("scroll", handleScroll, { passive: true })
      return () => container.removeEventListener("scroll", handleScroll)
    }
  }, [])

  const pageProgress = totalPages > 0 ? ((currentPage - 1) / (totalPages - 1)) * 100 : 0

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex-1 bg-slate-200 rounded-full h-1.5 overflow-hidden">
        <div
          className="bg-blue-500 h-full transition-all duration-300 ease-out rounded-full"
          style={{ width: `${pageProgress}%` }}
        />
      </div>
      <div className="text-xs text-slate-500 min-w-0">{Math.round(scrollProgress)}%</div>
    </div>
  )
}
