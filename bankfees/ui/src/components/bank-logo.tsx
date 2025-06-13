import type { FC } from "react"
import Image from "next/image"

interface BankLogoProps {
  bankName: string
  size?: "sm" | "md" | "lg"
  className?: string
}

export const BankLogo: FC<BankLogoProps> = ({ bankName, size = "md", className = "" }) => {
  const normalizedBankName = bankName.toLowerCase().trim()

  // Size mappings
  const sizes = {
    sm: 24,
    md: 32,
    lg: 48,
  }

  const logoSize = sizes[size]

  // Get the appropriate logo URL based on bank name
  const logoUrl = getBankLogoUrl(normalizedBankName)

  return (
    <div className={`flex items-center justify-center bg-white rounded-md p-1 ${className}`}>
      <Image
        src={logoUrl || "/placeholder.svg"}
        alt={`${bankName} logo`}
        width={logoSize}
        height={logoSize}
        className="object-contain"
      />
    </div>
  )
}

// Helper function to get the logo URL for a bank
export function getBankLogoUrl(bankName: string): string {
  switch (bankName) {
    case "attica":
      return "/bank-logos/attica-bank-logo.png"
    case "eurobank":
      return "/bank-logos/eurobank-logo.png"
    case "nbg":
      return "/bank-logos/nbg-logo.png"
    case "piraeus":
      return "/bank-logos/piraeus-bank-logo.png"
    case "alpha":
      return "/bank-logos/alpha-bank-logo.png"
    default:
      return "/bank-logos/generic-bank-logo.png"
  }
}
