import type { FC } from "react"
import Image from "next/image"
import { getEntityLogoUrl } from "@/lib/domain"

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
  const logoUrl = getEntityLogoUrl(normalizedBankName)

  return (
    <div className={`flex items-center justify-center bg-white rounded-md m-0.5 ${className}`}>
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

// Deprecated local logo mapping kept for backward compatibility
