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

  const bankRegex = /bank:("[^"]+"|\S+)/gi
  const bankMatches = [...input.matchAll(bankRegex)]

  if (bankMatches.length > 0) {
    const banks = bankMatches.map((m) => m[1].replace(/^"|"$/g, ""))
    const filter = banks.map((b) => `bank = "${b}"`).join(" OR ")
    filters.push(filter)
    query = query.replace(bankRegex, "").replace(/\s+/g, " ")
  }

  const categoryRegex = /category:("[^"]+"|\S+)/gi
  const categoryMatches = [...input.matchAll(categoryRegex)]
  if (categoryMatches.length > 0) {
    const categories = categoryMatches.map((m) => m[1].replace(/^"|"$/g, ""))
    const filter = categories.map((c) => `category = "${c}"`).join(" OR ")
    filters.push(filter)
    query = query.replace(categoryRegex, "").replace(/\s+/g, " ")
  }

  return { query: query.trim(), filters }
}
