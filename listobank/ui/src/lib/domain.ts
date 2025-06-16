export const APP_NAME = "LISTOBANK";

export const ENTITY_FIELD = "bank";
export const ENTITY_SEARCH_KEY = "bank";
export const CATEGORY_FIELD = "category";
export const CATEGORY_SEARCH_KEY = "category";

export const ALL_ENTITIES = ["alpha", "attica", "eurobank", "nbg", "piraeus"];
export const ALL_CATEGORIES = [
  "CustomerGuide",
  "DeltioPliroforisisPeriTelon",
  "Disclosure",
  "GeneralTermsContract",
  "InterestRates",
  "PaymentFees",
  "PriceList",
  "PriceListExclusive",
  "Uncategorized",
];

// Default grouping field for the PDF library page
export const LIBRARY_TOP_LEVEL_FIELD = ENTITY_FIELD;

export const DATA_PATH_PREFIX = "/Users/iwa/ekpizo/bankfees/data/";

export const MEILI_INDEX = "bankfees";

export const ENTITY_LOGOS: Record<string, string> = {
  attica: "/bank-logos/attica-bank-logo.png",
  eurobank: "/bank-logos/eurobank-logo.png",
  nbg: "/bank-logos/nbg-logo.png",
  piraeus: "/bank-logos/piraeus-bank-logo.png",
  alpha: "/bank-logos/alpha-bank-logo.png",
};

export const DEFAULT_ENTITY_LOGO = "/bank-logos/generic-bank-logo.png";

export function getEntityLogoUrl(entityName: string): string {
  const normalized = entityName.toLowerCase().trim();
  return ENTITY_LOGOS[normalized] || DEFAULT_ENTITY_LOGO;
}
