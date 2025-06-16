import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import {
  ENTITY_FIELD,
  ENTITY_SEARCH_KEY,
  CATEGORY_FIELD,
  CATEGORY_SEARCH_KEY,
} from "@/lib/domain"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface ParsedSearch {
  query: string
  filters: string[]
}

/**
 * Parse a user provided search string supporting gmail style operators.
 * Currently only `${ENTITY_SEARCH_KEY}:<name>` is recognised and converted to a
 * MeiliSearch filter. The returned `query` has these operators removed.
 */
export function parseSearchInput(input: string): ParsedSearch {
  let query = input
  const filters: string[] = []

  const entityRegex = new RegExp(`${ENTITY_SEARCH_KEY}:("[^\\"]+"|\\S+)`, "gi")
  const entityMatches = [...input.matchAll(entityRegex)]

  const categoryRegex = new RegExp(`${CATEGORY_SEARCH_KEY}:("[^\\"]+"|\\S+)`, "gi")
  const categoryMatches = [...input.matchAll(categoryRegex)]

  if (entityMatches.length > 0) {
    const entities = entityMatches.map((m) => m[1].replace(/^"|"$/g, ""))
    const filter = entities.map((e) => `${ENTITY_FIELD} = "${e}"`).join(" OR ")
    filters.push(filter)
    query = query.replace(entityRegex, "").replace(/\s+/g, " ")
  }

  if (categoryMatches.length > 0) {
    const categories = categoryMatches.map((m) => m[1].replace(/^"|"$/g, ""))
    const filter = categories
      .map((c) => `${CATEGORY_FIELD} = "${c}"`)
      .join(" OR ")
    filters.push(filter)
    query = query.replace(categoryRegex, "").replace(/\s+/g, " ")
  }

  return { query: query.trim(), filters }
}
