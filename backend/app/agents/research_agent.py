class ResearchAgent:
    """
    Builds a rule-based research summary from stock, price history, and news data.
    """

    DISCLAIMER = (
        "This is for research and educational purposes only, not financial advice."
    )

    def generate_research_summary(self, stock_data, history_data, news_data):
        stock_data = stock_data or {}
        history_data = history_data or []
        news_data = news_data or []

        price_analysis = self._analyze_price_history(stock_data, history_data)
        sentiment_analysis = self._analyze_news_sentiment(news_data)
        valuation_snapshot = self._build_valuation_snapshot(stock_data)

        overall_view = self._get_overall_view(
            price_analysis["price_change_percent"],
            sentiment_analysis["dominant_sentiment"],
        )
        confidence = self._get_confidence(
            price_analysis,
            sentiment_analysis,
            history_data,
            news_data,
        )

        bullish_signals = self._get_bullish_signals(
            price_analysis, sentiment_analysis, valuation_snapshot
        )
        bearish_signals = self._get_bearish_signals(
            price_analysis, sentiment_analysis, valuation_snapshot
        )
        risk_factors = self._get_risk_factors(
            stock_data, news_data, valuation_snapshot
        )
        things_to_watch = self._get_things_to_watch(
            price_analysis, sentiment_analysis, valuation_snapshot
        )

        return {
            "ticker": stock_data.get("ticker"),
            "company_name": stock_data.get("company_name"),
            "overall_view": overall_view,
            "confidence": confidence,
            "price_analysis": price_analysis,
            "news_sentiment_analysis": sentiment_analysis,
            "valuation_snapshot": valuation_snapshot,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "risk_factors": risk_factors,
            "things_to_watch": things_to_watch,
            "analyst_style_summary": self._build_summary(
                stock_data,
                overall_view,
                confidence,
                price_analysis,
                sentiment_analysis,
                valuation_snapshot,
            ),
            "disclaimer": self.DISCLAIMER,
        }

    def _analyze_price_history(self, stock_data, history_data):
        if not history_data:
            latest_price = self._safe_number(stock_data.get("current_price"))

            return {
                "start_price": latest_price,
                "latest_price": latest_price,
                "price_change": 0.0,
                "price_change_percent": 0.0,
                "trend": "sideways",
            }

        start_price = self._safe_number(history_data[0].get("close"))
        latest_price = self._safe_number(history_data[-1].get("close"))
        price_change = round(latest_price - start_price, 2)

        if start_price:
            price_change_percent = round((price_change / start_price) * 100, 2)
        else:
            price_change_percent = 0.0

        if price_change_percent > 2:
            trend = "uptrend"
        elif price_change_percent < -2:
            trend = "downtrend"
        else:
            trend = "sideways"

        return {
            "start_price": start_price,
            "latest_price": latest_price,
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            "trend": trend,
        }

    def _analyze_news_sentiment(self, news_data):
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        total_polarity = 0.0

        for article in news_data:
            sentiment = (article.get("sentiment") or "neutral").lower()
            polarity = self._safe_number(article.get("polarity"))
            total_polarity += polarity

            if sentiment == "positive":
                positive_count += 1
            elif sentiment == "negative":
                negative_count += 1
            else:
                neutral_count += 1

        news_count = len(news_data)
        average_polarity = round(total_polarity / news_count, 3) if news_count else 0.0

        if positive_count > neutral_count and positive_count > negative_count:
            dominant_sentiment = "positive"
        elif negative_count > positive_count and negative_count > neutral_count:
            dominant_sentiment = "negative"
        else:
            dominant_sentiment = "neutral"

        return {
            "average_polarity": average_polarity,
            "positive_count": positive_count,
            "neutral_count": neutral_count,
            "negative_count": negative_count,
            "dominant_sentiment": dominant_sentiment,
        }

    def _build_valuation_snapshot(self, stock_data):
        pe_ratio = stock_data.get("pe_ratio")
        market_cap = stock_data.get("market_cap")

        if pe_ratio is None:
            valuation_comment = "P/E ratio is unavailable, so valuation risk is harder to judge."
        elif pe_ratio > 30:
            valuation_comment = "P/E ratio appears elevated, which may imply higher valuation expectations."
        elif pe_ratio < 15:
            valuation_comment = "P/E ratio appears moderate to low compared with common market benchmarks."
        else:
            valuation_comment = "P/E ratio appears reasonable based on a simple rule-based screen."

        return {
            "pe_ratio": pe_ratio,
            "market_cap": market_cap,
            "valuation_comment": valuation_comment,
        }

    def _get_overall_view(self, price_change_percent, dominant_sentiment):
        if price_change_percent > 2 and dominant_sentiment == "positive":
            return "bullish"

        if price_change_percent < -2 and dominant_sentiment == "negative":
            return "bearish"

        return "neutral"

    def _get_confidence(
        self, price_analysis, sentiment_analysis, history_data, news_data
    ):
        if not history_data or not news_data:
            return "low"

        trend = price_analysis["trend"]
        dominant_sentiment = sentiment_analysis["dominant_sentiment"]

        signals_agree = (
            trend == "uptrend"
            and dominant_sentiment == "positive"
        ) or (
            trend == "downtrend"
            and dominant_sentiment == "negative"
        )
        signals_conflict = (
            trend == "uptrend"
            and dominant_sentiment == "negative"
        ) or (
            trend == "downtrend"
            and dominant_sentiment == "positive"
        )

        if signals_agree:
            return "high"

        if signals_conflict:
            return "low"

        if trend in ["uptrend", "downtrend"] or dominant_sentiment in [
            "positive",
            "negative",
        ]:
            return "medium"

        return "low"

    def _get_bullish_signals(
        self, price_analysis, sentiment_analysis, valuation_snapshot
    ):
        bullish_signals = []

        if price_analysis["trend"] == "uptrend":
            bullish_signals.append("Price has moved up by more than 2% over the 1-month period.")

        if (
            sentiment_analysis["positive_count"]
            > sentiment_analysis["negative_count"]
        ):
            bullish_signals.append("Positive news count is higher than negative news count.")

        pe_ratio = valuation_snapshot["pe_ratio"]
        if pe_ratio is not None and pe_ratio < 15:
            bullish_signals.append("P/E ratio appears moderate to low in this rule-based screen.")

        return bullish_signals

    def _get_bearish_signals(
        self, price_analysis, sentiment_analysis, valuation_snapshot
    ):
        bearish_signals = []

        if price_analysis["trend"] == "downtrend":
            bearish_signals.append("Price has moved down by more than 2% over the 1-month period.")

        if (
            sentiment_analysis["negative_count"]
            > sentiment_analysis["positive_count"]
        ):
            bearish_signals.append("Negative news count is higher than positive news count.")

        pe_ratio = valuation_snapshot["pe_ratio"]
        if pe_ratio is not None and pe_ratio > 30:
            bearish_signals.append("P/E ratio appears elevated in this rule-based screen.")

        return bearish_signals

    def _get_risk_factors(self, stock_data, news_data, valuation_snapshot):
        risk_factors = []
        pe_ratio = valuation_snapshot["pe_ratio"]

        if pe_ratio is None:
            risk_factors.append("P/E ratio is missing or unavailable.")
        elif pe_ratio > 30:
            risk_factors.append("P/E ratio is high, which may increase valuation risk.")

        if len(news_data) < 3:
            risk_factors.append("News coverage is limited because fewer than 3 articles were found.")

        if stock_data.get("market_cap") is None:
            risk_factors.append("Market cap is unavailable, which limits company size analysis.")

        return risk_factors

    def _get_things_to_watch(
        self, price_analysis, sentiment_analysis, valuation_snapshot
    ):
        things_to_watch = []

        if price_analysis["trend"] == "uptrend":
            things_to_watch.append("Watch whether the 1-month price uptrend continues.")
        elif price_analysis["trend"] == "downtrend":
            things_to_watch.append("Watch whether the 1-month price downtrend stabilizes.")
        else:
            things_to_watch.append("Watch for a clearer breakout from the current sideways price trend.")

        dominant_sentiment = sentiment_analysis["dominant_sentiment"]
        things_to_watch.append(
            f"Monitor whether news sentiment remains {dominant_sentiment}."
        )

        pe_ratio = valuation_snapshot["pe_ratio"]
        if pe_ratio is None:
            things_to_watch.append("Watch for updated valuation metrics such as P/E ratio.")
        elif pe_ratio > 30:
            things_to_watch.append("Watch whether earnings growth can support the elevated P/E ratio.")
        else:
            things_to_watch.append("Watch valuation changes relative to future earnings updates.")

        return things_to_watch

    def _build_summary(
        self,
        stock_data,
        overall_view,
        confidence,
        price_analysis,
        sentiment_analysis,
        valuation_snapshot,
    ):
        company_name = stock_data.get("company_name") or stock_data.get("ticker") or "The company"

        return (
            f"{company_name} currently screens as {overall_view} with {confidence} confidence. "
            f"Over the 1-month period, the stock shows a {price_analysis['trend']} "
            f"with a {price_analysis['price_change_percent']}% price change. "
            f"News sentiment is {sentiment_analysis['dominant_sentiment']} with an average polarity "
            f"of {sentiment_analysis['average_polarity']}. "
            f"{valuation_snapshot['valuation_comment']}"
        )

    def _safe_number(self, value):
        if value is None:
            return 0.0

        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return 0.0
