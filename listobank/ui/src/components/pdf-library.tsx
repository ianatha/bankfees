"use client";

import { BankLogo } from "@/components/bank-logo";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { getAllDocuments } from "@/lib/meilisearch";
import { ChevronDown, ChevronRight, ChevronUp, ExternalLink, FileText } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

interface Document {
  id: string;
  bank: string;
  filename: string;
  path: string;
  page?: number;
}

interface BankDocuments {
  bankName: string;
  documents: Document[];
}

export function PdfLibrary() {
  const [documents, setDocuments] = useState<BankDocuments[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openBanks, setOpenBanks] = useState<string[]>([]);

  useEffect(() => {
    async function fetchDocuments() {
      try {
        const docs = await getAllDocuments();

        // Group documents by bank
        const groupedByBank: Record<string, Document[]> = {};

        docs.forEach((doc) => {
          if (!groupedByBank[doc.bank]) {
            groupedByBank[doc.bank] = [];
          }

          // Check if document already exists in the array (by path)
          const existingDoc = groupedByBank[doc.bank].find((d) => d.path === doc.path);
          if (!existingDoc) {
            groupedByBank[doc.bank].push(doc);
          }
        });

        // Convert to array format and sort banks alphabetically
        const bankDocuments: BankDocuments[] = Object.keys(groupedByBank)
          .sort()
          .map((bankName) => ({
            bankName,
            documents: groupedByBank[bankName].sort((a, b) => a.filename.localeCompare(b.filename)),
          }));

        setDocuments(bankDocuments);
      } catch (err) {
        console.error("Error fetching documents:", err);
        setError("Failed to load documents. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    }

    fetchDocuments();
  }, []);

  const toggleBank = (bankName: string) => {
    setOpenBanks((prev) =>
      prev.includes(bankName) ? prev.filter((name) => name !== bankName) : [...prev, bankName]
    );
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <Skeleton className="h-5 w-3/4 mb-4" />
              <Skeleton className="h-4 w-full mb-2" />
              <Skeleton className="h-4 w-2/3" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 p-4 text-center">{error}</div>;
  }

  return (
    <div>
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4 w-full">
          <h2 className="text-lg font-semibold">Τράπεζες ({documents.length})</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setOpenBanks(
                openBanks.length === documents.length ? [] : documents.map((b) => b.bankName)
              )
            }
          >
            {openBanks.length === documents.length ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
            {openBanks.length === documents.length ? "Σύμπτυξη" : "Εμφάνιση Όλων"}
          </Button>
        </div>

        <ScrollArea className="h-[calc(100vh-12rem)]">
          <div className="space-y-4">
            {documents.map((bank) => (
              <Collapsible
                key={bank.bankName}
                open={openBanks.includes(bank.bankName)}
                onOpenChange={() => toggleBank(bank.bankName)}
                className="border rounded-md overflow-hidden bg-white"
              >
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    className="w-full flex justify-between items-center p-4 h-auto"
                  >
                    <div className="flex items-center gap-3 font-medium">
                      {openBanks.includes(bank.bankName) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                      <BankLogo bankName={bank.bankName} size="md" className="shadow-sm" />
                      {bank.bankName}
                    </div>
                    <Badge variant="secondary">{bank.documents.length} έγγραφα</Badge>
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
                    {bank.documents.map((doc) => (
                      <DocumentCard key={doc.id} document={doc} />
                    ))}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}

function DocumentCard({ document }: { document: Document }) {
  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow">
      <CardContent className="p-0">
        <div className="bg-slate-100 p-4 flex items-center gap-3">
          <div className="bg-white p-2 rounded shadow-sm">
            <FileText className="h-6 w-6 text-slate-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-sm truncate" title={document.filename}>
              {document.filename}
            </h3>
            <p className="text-xs text-slate-500">PDF Document</p>
          </div>
          <BankLogo bankName={document.bank} size="sm" />
        </div>
        <div className="p-4">
          <div className="flex justify-between items-center">
            <Link
              href={`/?document=${encodeURIComponent(document.path)}`}
              className="text-xs text-slate-500 hover:text-slate-800"
            >
              Search within document
            </Link>
            <a
              href={`/api/file/${document.path
                .split('/')
                .map(encodeURIComponent)
                .join('/')}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
            >
              View PDF
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
