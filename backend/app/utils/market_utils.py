def normalize_ticker(ticker: str):
    return ticker.strip().upper() if ticker else ""


def get_currency_symbol(currency: str):
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
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
    exchange = (
        _clean_value(info.get("exchange"))
        or _clean_value(info.get("fullExchangeName"))
        or "NASDAQ/NYSE"
    )

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
