import re


class TickerResolverAgent:
    COMPANY_CATALOG = (
        {
            "ticker": "INFY.NS",
            "name": "Infosys Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("Infosys", "Infosys Limited"),
        },
        {
            "ticker": "RELIANCE.NS",
            "name": "Reliance Industries Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("Reliance", "Reliance Industries", "Reliance Industries Limited"),
        },
        {
            "ticker": "TCS.NS",
            "name": "Tata Consultancy Services Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": (
                "TCS",
                "Tata Consultancy",
                "Tata Consultancy Services",
                "Tata Consultancy Services Limited",
            ),
        },
        {
            "ticker": "HDFCBANK.NS",
            "name": "HDFC Bank Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("HDFC Bank", "HDFC Bank Limited"),
        },
        {
            "ticker": "ICICIBANK.NS",
            "name": "ICICI Bank Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("ICICI Bank", "ICICI Bank Limited"),
        },
        {
            "ticker": "WIPRO.NS",
            "name": "Wipro Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("Wipro", "Wipro Limited"),
        },
        {
            "ticker": "HCLTECH.NS",
            "name": "HCL Technologies Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("HCL", "HCL Tech", "HCL Technologies"),
        },
        {
            "ticker": "BHARTIARTL.NS",
            "name": "Bharti Airtel Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("Airtel", "Bharti Airtel"),
        },
        {
            "ticker": "SBIN.NS",
            "name": "State Bank of India",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("SBI", "State Bank of India"),
        },
        {
            "ticker": "ITC.NS",
            "name": "ITC Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("ITC", "ITC Limited"),
        },
        {
            "ticker": "LT.NS",
            "name": "Larsen & Toubro Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("L&T", "L and T", "Larsen and Toubro", "Larsen & Toubro"),
        },
        {
            "ticker": "AXISBANK.NS",
            "name": "Axis Bank Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("Axis Bank", "Axis Bank Limited"),
        },
        {
            "ticker": "KOTAKBANK.NS",
            "name": "Kotak Mahindra Bank Limited",
            "exchange": "NSE",
            "country": "India",
            "currency": "INR",
            "aliases": ("Kotak Bank", "Kotak Mahindra Bank"),
        },
        {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Apple", "Apple Inc", "Apple Inc."),
        },
        {
            "ticker": "MSFT",
            "name": "Microsoft Corporation",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Microsoft", "Microsoft Corporation"),
        },
        {
            "ticker": "TSLA",
            "name": "Tesla, Inc.",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Tesla", "Tesla Inc", "Tesla Inc."),
        },
        {
            "ticker": "AMZN",
            "name": "Amazon.com, Inc.",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Amazon", "Amazon.com"),
        },
        {
            "ticker": "GOOGL",
            "name": "Alphabet Inc.",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Google", "Alphabet", "Alphabet Inc", "Alphabet Inc."),
        },
        {
            "ticker": "META",
            "name": "Meta Platforms, Inc.",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Meta", "Facebook", "Meta Platforms"),
        },
        {
            "ticker": "NVDA",
            "name": "NVIDIA Corporation",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Nvidia", "NVIDIA Corporation"),
        },
        {
            "ticker": "NFLX",
            "name": "Netflix, Inc.",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Netflix", "Netflix Inc", "Netflix Inc."),
        },
        {
            "ticker": "AMD",
            "name": "Advanced Micro Devices, Inc.",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("AMD", "Advanced Micro Devices"),
        },
        {
            "ticker": "INTC",
            "name": "Intel Corporation",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "aliases": ("Intel", "Intel Corporation"),
        },
    )

    TICKER_PATTERN = re.compile(r"^[A-Z0-9^][A-Z0-9.^=-]{0,19}$")

    def __init__(self):
        self._aliases = self._build_alias_index()

    def resolve(self, query: str):
        original_query = query if isinstance(query, str) else ""
        cleaned_query = self._normalize_spaces(original_query)

        if not cleaned_query:
            return self._unresolved(original_query, "Please enter a company name or ticker.")

        known_company = self._aliases.get(self._normalize_alias(cleaned_query))
        if known_company:
            return self._known_company_response(original_query, known_company)

        normalized_ticker = cleaned_query.upper()
        if self.TICKER_PATTERN.fullmatch(normalized_ticker):
            return {
                "query": original_query,
                "resolved": True,
                "ticker": normalized_ticker,
                "name": None,
                "exchange": None,
                "country": None,
                "currency": None,
                "confidence": "high",
                "source": "ticker_input",
            }

        return self._unresolved(
            original_query,
            "Could not resolve company name to ticker.",
        )

    def _build_alias_index(self):
        aliases = {}
        for company in self.COMPANY_CATALOG:
            for alias in company["aliases"]:
                aliases[self._normalize_alias(alias)] = company
        return aliases

    def _known_company_response(self, query, company):
        return {
            "query": query,
            "resolved": True,
            "ticker": company["ticker"],
            "name": company["name"],
            "exchange": company["exchange"],
            "country": company["country"],
            "currency": company["currency"],
            "confidence": "high",
            "source": "known_mapping",
        }

    def _unresolved(self, query, warning):
        return {
            "query": query,
            "resolved": False,
            "ticker": None,
            "name": None,
            "exchange": None,
            "country": None,
            "currency": None,
            "confidence": None,
            "source": None,
            "warning": warning,
        }

    def _normalize_alias(self, value):
        normalized = self._normalize_spaces(value).casefold()
        normalized = normalized.replace("&", " and ")
        normalized = re.sub(r"[,.]", "", normalized)
        return self._normalize_spaces(normalized)

    @staticmethod
    def _normalize_spaces(value):
        return " ".join(value.strip().split()) if isinstance(value, str) else ""
