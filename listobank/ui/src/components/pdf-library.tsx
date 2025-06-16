"use client";

import { BankLogo } from "@/components/bank-logo";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { CATEGORY_FIELD, ENTITY_FIELD, ENTITY_LOGOS, LIBRARY_TOP_LEVEL_FIELD } from "@/lib/domain";
import { getAllDocuments, LibDocument } from "@/lib/meilisearch";
import { group } from "console";
import { groupBy, sortBy, uniq } from "es-toolkit/array";
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
  GroupIcon,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

interface GroupDocuments {
  groupName: string;
  documents: LibDocument[];
}

export function PdfLibrary() {
  const [documents, setDocuments] = useState<GroupDocuments[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openGroups, setOpenGroups] = useState<string[]>([]);
  const [groupField, setGroupField] = useState(LIBRARY_TOP_LEVEL_FIELD);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedBank, setSelectedBank] = useState<string>("all");
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    async function fetchDocuments() {
      try {
        const docs = await getAllDocuments();

        const calculatedCategories = uniq(docs.map((doc) => doc.category));
        setCategories(calculatedCategories);

        let filteredDocuments = docs;

        if (groupField === ENTITY_FIELD && selectedCategory !== "all") {
          filteredDocuments = docs.filter((doc) => doc.category === selectedCategory);
        }

        if (groupField === CATEGORY_FIELD && selectedBank !== "all") {
          filteredDocuments = docs.filter((doc) => doc.entity === selectedBank);
        }

        const grouped: Record<string, LibDocument[]> = groupBy(filteredDocuments, (item) =>
          groupField === ENTITY_FIELD ? item.entity : item.category
        );

        let groupedDocuments: GroupDocuments[] = Object.keys(grouped).map((groupName) => ({
          groupName,
          documents: grouped[groupName].sort((a, b) => a.filename.localeCompare(b.filename)),
        }));

        if (groupField === ENTITY_FIELD) {
          for (const entity of Object.keys(ENTITY_LOGOS)) {
            if (!groupedDocuments.some((doc) => doc.groupName === entity)) {
              groupedDocuments.push({
                groupName: entity,
                documents: [],
              });
            }
          }
        }

        groupedDocuments = sortBy(groupedDocuments, [(docGroup) => docGroup.groupName]);

        setDocuments(groupedDocuments);
      } catch (err) {
        console.error("Error fetching documents:", err);
        setError("Failed to load documents. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    }

    fetchDocuments();
  }, [groupField, selectedCategory]);

  const toggleGroup = (name: string) => {
    setOpenGroups((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name]
    );
  };

  if (isLoading) {
    return (
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4 w-full">
          <h2 className="text-lg font-semibold">Τράπεζες (...)</h2>
          <Skeleton className="h-6 w-32 inline-block" />
        </div>

        <div className="flex items-center justify-around gap-2 mb-4 overflow-x-auto w-full">
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
          <h2 className="text-lg font-semibold">
            {groupField === ENTITY_FIELD ? "Τράπεζες" : "Κατηγορίες"} ({documents.length})
          </h2>
          <div className="flex flex-row">
            <div className="mr-4 flex flex-row gap-1 items-center">
              <GroupIcon className="h-4 w-4" />
              <Select value={groupField} onValueChange={setGroupField}>
                <SelectTrigger className="w-96">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ENTITY_FIELD}>Ομαδοποίηση ανά Οργανισμό</SelectItem>
                  <SelectItem value={CATEGORY_FIELD}>Ομαδοποίηση ανά Κατηγορία Εγγράφου</SelectItem>
                </SelectContent>
              </Select>
            </div>
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
        </div>

        {groupField === ENTITY_FIELD && (
          <div className="flex items-center gap-2 mb-4 overflow-x-auto w-full">
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
        )}

        {groupField === CATEGORY_FIELD && (
          <div className="flex items-center gap-2 mb-4 overflow-x-auto w-full">
            <FilterIcon className="h-4 w-4 text-slate-500" />
            <Button
              variant={selectedBank === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedBank("all")}
            >
              Όλες οι Τράπεζες
            </Button>
            {Object.keys(ENTITY_LOGOS).map((bank) => (
              <Button
                key={bank}
                variant={selectedBank === bank ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedBank(bank)}
                className="whitespace-nowrap"
              >
                {bank}
              </Button>
            ))}
          </div>
        )}

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
                    className="w-full flex justify-between items-center p-4 h-16"
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
                  <div className="grid grid-cols-1 md:grid-cols-1 gap-4 p-4">
                    {group.documents.length === 0 && (
                      <div className="text-center text-slate-500">
                        Δεν υπάρχουν έγγραφα κατηγορίας {selectedCategory} για αυτή την{" "}
                        {groupField === ENTITY_FIELD ? "τράπεζα" : "κατηγορία"}.
                      </div>
                    )}
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

function DocumentCard({ document, groupField }: { document: LibDocument; groupField: string }) {
  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow bg-slate-100 p-4">
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
            href={`/api/file/${document.path.split("/").map(encodeURIComponent).join("/")}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
          >
            View PDF
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
        <BankLogo bankName={document.entity} size="sm" />
      </CardContent>
    </Card>
  );
}
