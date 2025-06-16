"use client";

import { BankLogo } from "@/components/bank-logo";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { getAllDocuments, LibDocument } from "@/lib/meilisearch";
import {
  CalendarIcon,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  ExternalLink,
  FileIcon,
  FileText,
  FilterIcon,
  FolderIcon,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

interface BankDocuments {
  bankName: string;
  documents: LibDocument[];
}

export function PdfLibrary() {
  const [documents, setDocuments] = useState<BankDocuments[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openBanks, setOpenBanks] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    async function fetchDocuments() {
      try {
        const docs = await getAllDocuments();

        // Extract unique categories
        const uniqueCategories = Array.from(new Set(docs.map((doc) => doc.category))).sort();
        setCategories(uniqueCategories);

        // Group documents by bank
        const groupedByBank: Record<string, LibDocument[]> = {};

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

  // Filter documents based on selected category
  const filteredDocuments = documents
    .map((bank) => ({
      ...bank,
      documents:
        selectedCategory === "all"
          ? bank.documents
          : bank.documents.filter((doc) => doc.category === selectedCategory),
    }))
    .filter((bank) => bank.documents.length > 0);

  if (isLoading) {
    return (
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4 w-full">
          <h2 className="text-lg font-semibold">Τράπεζες (...)</h2>
          <Skeleton className="h-6 w-32 inline-block" />
        </div>

        <div className="flex items-center justify-around gap-2 mb-4 overflow-x-auto">
          <FilterIcon className="h-4 w-4 text-slate-500" />
          <Skeleton className="h-10 w-full inline-block" />
        </div>

        <div className="flex flex-col gap-4">
          {[...Array(5)].map((_, i) => (
            <Button
              key={i}
              variant="ghost"
              className="border rounded-md overflow-hidden !bg-white w-full flex justify-between items-center p-4 h-16"
              disabled
            >
              <div className="flex items-center gap-3 font-medium">
                <ChevronRight className="h-4 w-4" />
                <Skeleton className="h-10 w-10" />
                ...
              </div>
              <Badge variant="secondary">... έγγραφα</Badge>
            </Button>
          ))}
        </div>
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
          <h2 className="text-lg font-semibold">Τράπεζες ({filteredDocuments.length})</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setOpenBanks(
                openBanks.length === filteredDocuments.length
                  ? []
                  : filteredDocuments.map((b) => b.bankName)
              )
            }
          >
            {openBanks.length === filteredDocuments.length ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
            {openBanks.length === filteredDocuments.length ? "Σύμπτυξη" : "Εμφάνιση Όλων"}
          </Button>
        </div>

        <div className="flex items-center justify-around gap-2 mb-4 overflow-x-auto">
          <FilterIcon className="h-4 w-4 text-slate-500" />
          <Button
            variant={selectedCategory === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedCategory("all")}
          >
            Όλες οι κατηγορίες
          </Button>
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category)}
              className="whitespace-nowrap"
            >
              {category}
            </Button>
          ))}
        </div>

        <ScrollArea className="h-[calc(100vh-12rem)]">
          <div className="space-y-4">
            {filteredDocuments.map((bank) => (
              <Collapsible
                key={bank.bankName}
                open={openBanks.includes(bank.bankName)}
                onOpenChange={() => toggleBank(bank.bankName)}
                className="border rounded-md overflow-hidden bg-white"
              >
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    className="w-full flex justify-between items-center p-4 h-16"
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
                  <div className="grid grid-cols-1 md:grid-cols-1 gap-4 p-4">
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

function DocumentCard({ document }: { document: LibDocument }) {
  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow bg-slate-100 p-4 ">
      <CardContent className="flex items-center gap-3">
        <div className="bg-white p-2 rounded shadow-sm">
          <FileText className="h-6 w-6 text-slate-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-sm truncate" title={document.title}>
            {document.title}
          </h3>
          <p className="text-sm text-slate-500 flex flex-row items-center gap-4">
            {document.effective_date && (
              <span className="flex flex-row items-center gap-1">
                <CalendarIcon className="inline h-4 w-4 text-slate-500" />
                {document.effective_date
                  ? new Date(document.effective_date).toLocaleDateString("el-GR")
                  : ""}
              </span>
            )}
            <span className="flex flex-row items-center gap-1">
              <FileIcon className="inline h-4 w-4 text-slate-500" />
              {document.filename}
            </span>
            <span className="flex flex-row items-center gap-1">
              <FolderIcon className="inline h-4 w-4 text-slate-500" />
              {document.category}
            </span>
          </p>
        </div>
        <div>
          <Link
            href={`/?document=${encodeURIComponent(document.path)}`}
            className="text-xs text-slate-500 hover:text-slate-800"
          >
            Search within document
          </Link>
          <a
            href={document.path}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            View PDF
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
        <BankLogo bankName={document.bank} size="sm" />
      </CardContent>
    </Card>
  );
}
