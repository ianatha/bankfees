import { BankLogo } from "./bank-logo"

interface BankHeaderProps {
  title: string
  subtitle?: string
}

export function BankHeader({ title, subtitle }: BankHeaderProps) {
  return (
    <div className="flex items-center gap-6 mb-8">
      <div className="flex gap-3">
        <BankLogo bankName="alpha" size="md" />
        <BankLogo bankName="attica" size="md" />
        <BankLogo bankName="eurobank" size="md" />
        <BankLogo bankName="nbg" size="md" />
        <BankLogo bankName="piraeus" size="md" />
      </div>
      <div>
        <h1 className="text-3xl font-bold">{title}</h1>
        {subtitle && <p className="text-slate-600">{subtitle}</p>}
      </div>
    </div>
  )
}
