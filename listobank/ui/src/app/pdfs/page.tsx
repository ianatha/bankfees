import { PdfLibrary } from "@/components/pdf-library";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, SearchIcon } from "lucide-react";
import { BankHeader } from "@/components/bank-header";
import { Card, CardContent, CardTitle } from "@/components/ui/card";

export default function PDFsPage() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-between">
          <BankHeader
            title="Βιβλιοθήκη Εγγράφων"
            subtitle="Περιηγηθείτε σε όλα τα τραπεζικά έγγραφα στο ευρετήριο"
          />
          <Link href="/search">
            <Button variant="outline" className="flex items-center gap-2">
              <SearchIcon className="h-4 w-4" />
              Αναζήτηση
            </Button>
          </Link>
        </div>
        <div className="flex justify-center gap-2 mt-4 mb-6">
          <Card className="mt-6 mb-8 w-[50%]">
            <CardContent className="flex items-center gap-3">
              <p className="text-slate-600">
                Εδώ μπορείτε να περιηγηθείτε σε όλα τα τραπεζικά έγγραφα που έχουμε συλλέξει. Κάντε
                κλικ σε οποιοδήποτε έγγραφο για να δείτε τις λεπτομέρειες και να αναζητήσετε
                συγκεκριμένους όρους ή χρεώσεις.
              </p>
            </CardContent>
          </Card>
        </div>
        <PdfLibrary />
      </div>
    </main>
  );
}
