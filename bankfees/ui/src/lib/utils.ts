import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface ParsedSearch {
  query: string
  filters: string[]
}

/**
 * Parse a user provided search string supporting gmail style operators.
 * Currently only `bank:<name>` is recognised and converted to a
 * MeiliSearch filter. The returned `query` has these operators removed.
 */
export function parseSearchInput(input: string): ParsedSearch {
  let query = input
  const filters: string[] = []

  const bankRegex = /bank:("[^"]+"|\S+)/i
  const match = input.match(bankRegex)
  if (match) {
    const value = match[1].replace(/^"|"$/g, "")
    filters.push(`bank = "${value}"`)
    query = query.replace(match[0], "").trim()
  }

  return { query: query.trim(), filters }
}
