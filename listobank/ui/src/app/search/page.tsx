import { SearchInterface } from "@/components/search-interface"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Library } from "lucide-react"
import { BankHeader } from "@/components/bank-header"

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-between">
          <BankHeader
            title="Έρευνα Τραπεζικών Όρων & Χρεώσεων"
            subtitle="Αναζητήστε λέξεις-κλειδιά σε γενικούς όρους συναλλαγών τραπεζών"
          />
          <Link href="/pdfs">
            <Button variant="outline" className="flex items-center gap-2">
              <Library className="h-4 w-4" />
              Βιβλιοθήκη
            </Button>
          </Link>
        </div>
        <SearchInterface />
      </div>
    </main>
  )
}
