import Link from "next/link";
import { BankLogo } from "./bank-logo";

interface BankHeaderProps {
  title: string;
  subtitle?: string;
}

export function BankHeader({ title, subtitle }: BankHeaderProps) {
  return (
    <div className="flex items-center gap-6 mb-8">
      <Link href="/">
        <div className="font-mono text-2xl font-bold border-2 border-black p-4">LISTOBANK</div>
      </Link>
      <div>
        <h1 className="text-3xl font-bold">{title}</h1>
        {subtitle && <p className="text-slate-600">{subtitle}</p>}
      </div>
    </div>
  );
}
