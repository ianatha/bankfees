"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { PdfViewer } from "@/components/pdf-viewer"

export function PdfDebug() {
  const [testUrl, setTestUrl] = useState("https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf")
  const [currentUrl, setCurrentUrl] = useState("")

  const loadTestPdf = () => {
    setCurrentUrl(testUrl)
  }

  return (
    <div className="p-4">
      <div className="mb-4 flex gap-2">
        <Input
          value={testUrl}
          onChange={(e) => setTestUrl(e.target.value)}
          placeholder="Enter PDF URL to test"
          className="flex-1"
        />
        <Button onClick={loadTestPdf}>Load PDF</Button>
      </div>

      {currentUrl && (
        <div className="h-[600px] border rounded-lg overflow-hidden">
          <PdfViewer documentUrl={currentUrl} pageNumber={1} searchTerm="" highlight="" />
        </div>
      )}
    </div>
  )
}

export default function DebugPage() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-2xl font-bold mb-4">PDF Debug Page</h1>
        <p className="text-slate-600 mb-8">Use this page to test PDF loading functionality</p>
        <PdfDebug />
      </div>
    </main>
  )
}
