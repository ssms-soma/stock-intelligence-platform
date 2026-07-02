const MARKET_RULES = [
  {
    matches: (ticker) => ticker.endsWith(".NS"),
    market: "India",
    exchange: "NSE",
    country: "India",
    countryLabel: "India",
    currency: "INR",
    currencySymbol: "\u20B9",
    flag: "\uD83C\uDDEE\uD83C\uDDF3",
  },
  {
    matches: (ticker) => ticker.endsWith(".BO"),
    market: "India",
    exchange: "BSE",
    country: "India",
    countryLabel: "India",
    currency: "INR",
    currencySymbol: "\u20B9",
    flag: "\uD83C\uDDEE\uD83C\uDDF3",
  },
];

const DEFAULT_MARKET = {
  market: "United States",
  exchange: "NASDAQ/NYSE",
  country: "United States",
  countryLabel: "United States",
  currency: "USD",
  currencySymbol: "$",
  flag: "\uD83C\uDDFA\uD83C\uDDF8",
};

function getCurrencySymbol(currency) {
  const symbols = {
    INR: "\u20B9",
    USD: "$",
    EUR: "\u20AC",
    GBP: "\u00A3",
    JPY: "\u00A5",
  };

  return symbols[currency] ?? currency ?? DEFAULT_MARKET.currencySymbol;
}

function getFlag(country) {
  if (country === "India") {
    return "\uD83C\uDDEE\uD83C\uDDF3";
  }

  if (country === "United States") {
    return "\uD83C\uDDFA\uD83C\uDDF8";
  }

  return "";
}

export function getMarketInfo(ticker = "", backendMetadata = null) {
  const normalizedTicker =
    typeof ticker === "string" ? ticker.trim().toUpperCase() : "";
  const matchedRule = MARKET_RULES.find((rule) => rule.matches(normalizedTicker));
  const fallbackMarketInfo = matchedRule ?? DEFAULT_MARKET;
  const metadata =
    backendMetadata && typeof backendMetadata === "object" ? backendMetadata : {};
  const currency = metadata.currency || fallbackMarketInfo.currency;
  const country = metadata.country || fallbackMarketInfo.country;
  const market = metadata.market || fallbackMarketInfo.market;
  const exchange = metadata.exchange || fallbackMarketInfo.exchange;
  const currencySymbol =
    metadata.currency_symbol ||
    metadata.currencySymbol ||
    getCurrencySymbol(currency) ||
    fallbackMarketInfo.currencySymbol;

  return {
    ticker: normalizedTicker,
    market,
    exchange,
    country,
    countryLabel: country || fallbackMarketInfo.countryLabel,
    currency,
    currencySymbol,
    flag: metadata.flag || getFlag(country) || fallbackMarketInfo.flag,
  };
}

export function formatCurrencyByTicker(value, ticker, backendMetadata = null) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const numberValue = Number(value);
  const marketInfo = getMarketInfo(ticker, backendMetadata);

  if (!Number.isFinite(numberValue)) {
    return "N/A";
  }

  return `${marketInfo.currencySymbol}${numberValue.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatCurrencyByMetadata(value, backendMetadata, ticker = "") {
  return formatCurrencyByTicker(value, ticker, backendMetadata);
}

export function formatMarketLabel(ticker, backendMetadata = null) {
  const marketInfo = getMarketInfo(ticker, backendMetadata);

  if (!marketInfo.market || marketInfo.market === "United States") {
    return `${marketInfo.flag} US Market`;
  }

  return `${marketInfo.flag} ${marketInfo.exchange || marketInfo.market}`;
}
