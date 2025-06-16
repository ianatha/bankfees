"use client";

import { BankLogo } from "@/components/bank-logo";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { getAllDocuments } from "@/lib/meilisearch";
import {
  ENTITY_FIELD,
  LIBRARY_TOP_LEVEL_FIELD,
} from "@/lib/domain";
import { ChevronDown, ChevronRight, ChevronUp, ExternalLink, FileText } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

interface Document {
  id: string;
  entity: string;
  category: string;
  filename: string;
  path: string;
  page?: number;
}

interface GroupDocuments {
  groupName: string;
  documents: Document[];
}

export function PdfLibrary() {
  const [documents, setDocuments] = useState<GroupDocuments[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openGroups, setOpenGroups] = useState<string[]>([]);
  const [groupField, setGroupField] = useState(LIBRARY_TOP_LEVEL_FIELD);

  useEffect(() => {
    async function fetchDocuments() {
      try {
        const docs = await getAllDocuments();

        const grouped: Record<string, Document[]> = {};

        docs.forEach((doc) => {
          const key = (doc as any)[groupField];
          if (!grouped[key]) {
            grouped[key] = [];
          }

          const existingDoc = grouped[key].find((d) => d.path === doc.path);
          if (!existingDoc) {
            grouped[key].push(doc);
          }
        });

        const groupedDocuments: GroupDocuments[] = Object.keys(grouped)
          .sort()
          .map((groupName) => ({
            groupName,
            documents: grouped[groupName].sort((a, b) => a.filename.localeCompare(b.filename)),
          }));

        setDocuments(groupedDocuments);
      } catch (err) {
        console.error("Error fetching documents:", err);
        setError("Failed to load documents. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    }

    fetchDocuments();
  }, [groupField]);

  const toggleGroup = (name: string) => {
    setOpenGroups((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name]
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
          <h2 className="text-lg font-semibold">
            {groupField === ENTITY_FIELD ? "Τράπεζες" : "Κατηγορίες"} ({documents.length})
          </h2>
          <select
            value={groupField}
            onChange={(e) => setGroupField(e.target.value)}
            className="border rounded px-2 py-1 text-sm mr-4"
          >
            <option value={ENTITY_FIELD}>Group by {ENTITY_FIELD}</option>
            <option value={CATEGORY_FIELD}>Group by {CATEGORY_FIELD}</option>
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setOpenGroups(
                openGroups.length === documents.length ? [] : documents.map((b) => b.groupName)
              )
            }
          >
            {openGroups.length === documents.length ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
            {openGroups.length === documents.length ? "Σύμπτυξη" : "Εμφάνιση Όλων"}
          </Button>
        </div>

        <ScrollArea className="h-[calc(100vh-12rem)]">
          <div className="space-y-4">
            {documents.map((group) => (
              <Collapsible
                key={group.groupName}
                open={openGroups.includes(group.groupName)}
                onOpenChange={() => toggleGroup(group.groupName)}
                className="border rounded-md overflow-hidden bg-white"
              >
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    className="w-full flex justify-between items-center p-4 h-auto"
                  >
                    <div className="flex items-center gap-3 font-medium">
                      {openGroups.includes(group.groupName) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                      {groupField === ENTITY_FIELD && (
                        <BankLogo bankName={group.groupName} size="md" className="shadow-sm" />
                      )}
                      {group.groupName}
                    </div>
                    <Badge variant="secondary">{group.documents.length} έγγραφα</Badge>
                </Button>
              </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
                    {group.documents.map((doc) => (
                      <DocumentCard key={doc.id} document={doc} groupField={groupField} />
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

function DocumentCard({ document, groupField }: { document: Document; groupField: string }) {
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
          {groupField !== ENTITY_FIELD && (
            <BankLogo bankName={document.entity} size="sm" />
          )}
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
              href={document.path}
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
