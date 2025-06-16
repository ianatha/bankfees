import { BankHeader } from "@/components/bank-header";
import { Button } from "@/components/ui/button";
import { Library, SearchIcon } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-between">
          <BankHeader
            title="Πηγές"
            subtitle="Λεπτομέρειες για τις πηγές των δεδομένων μας στο Listobank"
          />
          <div className="flex flex-col gap-2">
            <Link href="/search">
              <Button variant="outline" className="flex items-center gap-2">
                <SearchIcon className="h-4 w-4" />
                Αναζήτηση
              </Button>
            </Link>
            <Link href="/pdfs">
              <Button variant="outline" className="flex items-center gap-2">
                <Library className="h-4 w-4" />
                Βιβλιοθήκη
              </Button>
            </Link>
          </div>
        </div>
        <div className="tailwind prose prose-slate max-w-none mt-8">
          <h1>Πηγές &amp; Μεθοδολογία</h1>
          <p>
            Το Listobank συλλέγει δεδομένα από δημόσιες πηγές, όπως οι ιστοσελίδες των τραπεζών και
            επίσημα έγγραφα. Για κάθε μία από τις ακόλουθες πηγές, κατεβάσαμε όλα τα συνδεδεμένα PDF και τα
            προσθέσαμε στη βιβλιοθήκη μας:
          </p>
          <ul>
            <li>
              Alpha Bank:
              <ul>
                <li>
                  https://www.alpha.gr/el/idiotes/support-center/isxuon-timologio-kai-oroi-sunallagon
                </li>
              </ul>
            </li>
            <li>
              Τράπεζα Αττικής (Attica Bank):
              <ul>
                <li>
                  https://www.atticabank.gr/el/eidikoi-oroi-trapezikon-ergasion-timologio-ergasion/
                </li>
                <li>https://www.atticabank.gr/el/genikoi-oroi-synallagon/</li>
              </ul>
            </li>
            <li>
              Εθνική Τράπεζα της Ελλάδος (National Bank of Greece):
              <ul>
                <li>https://www.nbg.gr/el/footer/timologia-ergasiwn</li>
                <li>https://www.nbg.gr/el/footer/deltio-plhroforhshs-peri-telwn</li>
              </ul>
            </li>
            <li>
              Piraeus Bank:
              <ul>
                <li>https://www.piraeusbank.gr/el/support/epitokia-deltia-timwn</li>
                <li>https://www.piraeusbank.gr/el/support/synallaktikoi-oroi</li>
              </ul>
            </li>
            <li>
              Eurobank:
              <ul>
                <li>https://www.eurobank.gr/el/timologia</li>
                <li>https://www.eurobank.gr/el/oroi-sunallagon</li>
              </ul>
            </li>
          </ul>

          <p>
            Μεταδεδομένα για κάθε έγγραφο, όπως η "κατηγορία", η "ημερομηνία ισχύος" και ο "τίτλος" του, εξήχθησαν
            μέσω Τεχνητής Νοημοσύνης (ΤΝ).
          </p>

          <h2>Ορισμοί Κατηγοριών Εγγράφων</h2>

          <p>Οι κατηγορίες που χρησιμοποιήθηκαν και οι ορισμοί τους είναι οι εξής:</p>
          <ul>
            <li>
              <strong>CustomerGuide:</strong> Οδηγίες για την διευκόλυνση των πελατών της τράπεζας
              κατά τη διενέργεια ραντεβού ή συνναλαγών.
            </li>
            <li>
              <strong>DeltioPliroforisisPeriTelon:</strong> Έγγραφα με τίτλο "Δελτίο Πληροφόρησης
              περί Τελών".
            </li>
            <li>
              <strong>Disclosure:</strong> Έγγραφα ενημέρωσης πελάτη για υποχρεώσεις, κινδύνους και
              διαφάνεια όρων (αποποιήσεις ευθυνών, γνωστοποιήσεις), εκτός από Δελτία Πληροφόρησης
              περί Τελών.
            </li>
            <li>
              <strong>GeneralTermsContract:</strong> Γενικοί όροι σύμβασης και συναλλαγών μεταξύ
              πελάτη και τράπεζας.
            </li>
            <li>
              <strong>InterestRates:</strong> Έγγραφα που περιέχουν πληροφορίες για επιτόκια
              καταθέσεων, δανείων και άλλων τραπεζικών προϊόντων.
            </li>
            <li>
              <strong>PaymentFees:</strong> Πίνακες τελών και προμηθειών για πληρωμές, μεταφορές και
              υπηρεσίες σε συγκεκριμένους παραλήπτες.
            </li>
            <li>
              <strong>PriceList:</strong> Γενικός τιμοκατάλογος τραπεζικών προϊόντων και υπηρεσιών
              με βασικές χρεώσεις και επιτόκια.
            </li>
            <li>
              <strong>PriceListExclusive:</strong> Ειδικός τιμοκατάλογος για premium
              προϊόντα/υπηρεσίες (π.χ. private banking, gold accounts).
            </li>
          </ul>
        </div>
      </div>
    </main>
  );
}
