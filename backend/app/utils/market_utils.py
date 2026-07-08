EXCHANGE_DISPLAY_NAMES = {
    "NMS": "NASDAQ",
    "NCM": "NASDAQ",
    "NGM": "NASDAQ",
    "NAS": "NASDAQ",
    "NYQ": "NYSE",
    "ASE": "NYSE American",
    "NSI": "NSE",
    "NSE": "NSE",
    "BSE": "BSE",
}


def normalize_ticker(ticker: str):
    return ticker.strip().upper() if ticker else ""


def normalize_exchange(exchange, ticker=None):
    normalized_ticker = normalize_ticker(ticker)

    if normalized_ticker.endswith(".NS"):
        return "NSE"

    if normalized_ticker.endswith(".BO"):
        return "BSE"

    cleaned_exchange = _clean_value(exchange)

    if not cleaned_exchange:
        return "US"

    exchange_code = str(cleaned_exchange).strip().upper()
    return EXCHANGE_DISPLAY_NAMES.get(exchange_code, cleaned_exchange)


def get_currency_symbol(currency: str):
    symbols = {
        "INR": "\u20b9",
        "USD": "$",
        "EUR": "\u20ac",
        "GBP": "\u00a3",
        "JPY": "\u00a5",
    }

    normalized_currency = currency.upper() if currency else "USD"
    return symbols.get(normalized_currency, normalized_currency)


def get_market_metadata(ticker: str, yfinance_info=None):
    normalized_ticker = normalize_ticker(ticker)
    info = yfinance_info if isinstance(yfinance_info, dict) else {}

    if normalized_ticker.endswith(".NS"):
        return {
            "market": "India",
            "country": "India",
            "exchange": "NSE",
            "currency": "INR",
            "currency_symbol": get_currency_symbol("INR"),
        }

    if normalized_ticker.endswith(".BO"):
        return {
            "market": "India",
            "country": "India",
            "exchange": "BSE",
            "currency": "INR",
            "currency_symbol": get_currency_symbol("INR"),
        }

    currency = _clean_value(info.get("currency")) or _clean_value(
        info.get("financialCurrency")
    ) or "USD"
    raw_exchange = (
        _clean_value(info.get("exchange"))
        or _clean_value(info.get("fullExchangeName"))
    )
    exchange = normalize_exchange(raw_exchange, normalized_ticker)

    return {
        "market": _clean_value(info.get("market")) or "United States",
        "country": _clean_value(info.get("country")) or "United States",
        "exchange": exchange,
        "currency": currency,
        "currency_symbol": get_currency_symbol(currency),
    }


def _clean_value(value):
    if value in (None, "", "N/A", "None"):
        return None

    return value
