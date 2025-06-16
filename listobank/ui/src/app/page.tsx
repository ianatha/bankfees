import { SearchInterface } from "@/components/search-interface";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { DatabaseIcon, Library, LibraryIcon, SearchIcon } from "lucide-react";
import { BankHeader } from "@/components/bank-header";
import { BankLogo } from "@/components/bank-logo";
import { ALL_ENTITIES } from "@/lib/domain";
import Balancer from "react-wrap-balancer";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto py-8 px-4 flex flex-col gap-8">
        <div className="flex items-center justify-between">
          <BankHeader
            title="Ευρετήριο Τραπεζικών Όρων & Χρεώσεων"
            subtitle="Αναζητήστε λέξεις-κλειδιά σε γενικούς όρους συναλλαγών τραπεζών"
          />
        </div>
        <div className="flex flex-col w-full items-center gap-2">
          <div className="w-96 text-center">
            <Balancer>
              Έχουμε <span className="font-bold">κατεβάσει, ταξινομήσει και τιθασεύσει</span> 1000+
              σελίδες τραπεζικών όρων συναλλαγών και τιμολογιακών πρακτικών από τις εξής τράπεζες:
            </Balancer>
          </div>
          <div className="flex gap-3">
            {ALL_ENTITIES.map((bank) => (
              <BankLogo key={bank} bankName={bank} size="md" />
            ))}
          </div>
        </div>
        <div className="flex flex-row justify-center items-center gap-4">
          <Link href="/search">
            <Button variant="outline" className="flex flex-col items-center gap-2 h-32 w-32">
              <SearchIcon className="!h-8 !w-8" />
              Αναζήτηση
            </Button>
          </Link>
          <Link href="/pdfs">
            <Button variant="outline" className="flex flex-col items-center gap-2 h-32 w-32">
              <LibraryIcon className="!h-8 !w-8" />
              Βιβλιοθήκη
            </Button>
          </Link>
          <Link href="/sources">
            <Button variant="outline" className="flex flex-col items-center gap-2 h-32 w-32">
              <DatabaseIcon className="!h-8 !w-8" />
              Πηγές
            </Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
