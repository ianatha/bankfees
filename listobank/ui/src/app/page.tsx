import { SearchInterface } from "@/components/search-interface";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Library, LibraryIcon, SearchIcon } from "lucide-react";
import { BankHeader } from "@/components/bank-header";
import { BankLogo } from "@/components/bank-logo";
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
              Έχουν ανακτηθεί <span className="font-bold">1,000+</span> σελίδες όρων συμβάσεων και
              τιμολογιακών πρακτικών από τις εξης τράπεζες:
            </Balancer>
          </div>
          <div className="flex gap-3">
            <BankLogo bankName="alpha" size="md" />
            <BankLogo bankName="attica" size="md" />
            <BankLogo bankName="eurobank" size="md" />
            <BankLogo bankName="nbg" size="md" />
            <BankLogo bankName="piraeus" size="md" />
          </div>
        </div>
        <div className="flex flex-row justify-center items-center gap-4">
          <Link href="/search">
            <Button variant="outline" className="flex flex-col items-center gap-2 h-32 w-32">
              <SearchIcon className="h-8 w-8" />
              Αναζήτηση
            </Button>
          </Link>
          <Link href="/pdfs">
            <Button variant="outline" className="flex flex-col items-center gap-2 h-32 w-32">
              <LibraryIcon className="h-16 w-16" />
              Βιβλιοθήκη
            </Button>
          </Link>
        </div>
      </div>
    </main>
  );
}
