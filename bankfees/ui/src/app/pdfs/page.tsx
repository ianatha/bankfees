import { PdfLibrary } from "@/components/pdf-library"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowLeft, SearchIcon } from "lucide-react"
import { BankHeader } from "@/components/bank-header"

export default function PDFsPage() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-between">
          <BankHeader title="Βιβλιοθήκη Εγγράφων PDF" subtitle="Περιηγηθείτε σε όλα τα τραπεζικά έγγραφα στο ευρετήριο" />
          <Link href="/">
            <Button variant="outline" className="flex items-center gap-2">
              <SearchIcon className="h-4 w-4" />
              Αναζήτηση
            </Button>
          </Link>
        </div>
        <PdfLibrary />
      </div>
    </main>
  )
}
