const MARKET_RULES = [
  {
    matches: (ticker) => ticker.endsWith(".NS"),
    market: "NSE",
    country: "IN",
    countryLabel: "India",
    currency: "INR",
    currencySymbol: "\u20B9",
    flag: "\uD83C\uDDEE\uD83C\uDDF3",
  },
];

const DEFAULT_MARKET = {
  market: "NASDAQ/NYSE",
  country: "US",
  countryLabel: "United States",
  currency: "USD",
  currencySymbol: "$",
  flag: "\uD83C\uDDFA\uD83C\uDDF8",
};

export function getMarketInfo(ticker = "") {
  const normalizedTicker =
    typeof ticker === "string" ? ticker.trim().toUpperCase() : "";
  const matchedRule = MARKET_RULES.find((rule) => rule.matches(normalizedTicker));
  const marketInfo = matchedRule ?? DEFAULT_MARKET;

  return {
    ticker: normalizedTicker,
    ...marketInfo,
  };
}

export function formatCurrencyByTicker(value, ticker) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const numberValue = Number(value);
  const marketInfo = getMarketInfo(ticker);

  if (!Number.isFinite(numberValue)) {
    return "N/A";
  }

  return `${marketInfo.currencySymbol}${numberValue.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatMarketLabel(ticker) {
  const marketInfo = getMarketInfo(ticker);

  if (!marketInfo.market || marketInfo.market === "NASDAQ/NYSE") {
    return `${marketInfo.flag} US Market`;
  }

  return `${marketInfo.flag} ${marketInfo.market}`;
}
