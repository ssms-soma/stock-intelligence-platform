import math


class ChatAgent:
    VALID_MODES = {"auto", "llm", "company", "rag"}
    SUMMARY_LIMIT = 2_000

    COMPANY_FIELDS = (
        "ticker",
        "name",
        "sector",
        "industry",
        "country",
        "exchange",
        "currency",
        "market",
        "employees",
        "short_summary",
        "business_summary",
    )
    INFORMATIVE_COMPANY_FIELDS = (
        "name",
        "sector",
        "industry",
        "employees",
        "short_summary",
        "business_summary",
    )
    CONTEXT_SOURCES = (
        "company_profile",
        "stock_metrics",
        "price_history",
        "news",
        "research",
        "recommendations",
    )

    def select_mode(self, mode, ticker=None, documents=None):
        normalized_mode = (mode or "auto").strip().lower()
        has_ticker = bool(ticker and ticker.strip())
        has_documents = bool(documents)

        if normalized_mode not in self.VALID_MODES:
            return normalized_mode, (
                "Unsupported chat mode. Use auto, llm, company, or rag."
            )

        if normalized_mode == "auto":
            if has_documents:
                return "rag", None
            if has_ticker:
                return "company", None
            return "llm", None

        if normalized_mode == "rag" and not has_documents:
            return "rag", "RAG mode requires at least one document."

        if normalized_mode == "company" and not has_ticker:
            return "company", "Company mode requires a ticker."

        return normalized_mode, None

    def build_company_context(self, company_result):
        if not isinstance(company_result, dict):
            return {}

        profile = company_result.get("company_profile")
        if not isinstance(profile, dict):
            return {}

        if not any(profile.get(field) for field in self.INFORMATIVE_COMPANY_FIELDS):
            return {}

        context = {}
        for field in self.COMPANY_FIELDS:
            value = profile.get(field)
            if value in (None, "", "N/A"):
                continue

            if field in {"short_summary", "business_summary"}:
                value = self._limit_text(value)

            context[field] = value

        return context

    def select_context_sources(self, question):
        text = str(question or "").strip().lower()

        broad_terms = (
            "should i buy",
            "should i sell",
            "invest in",
            "investment case",
            "investment thesis",
            "worth buying",
            "recommend",
            "valuation",
            "outlook",
        )
        risk_terms = ("risk", "risks", "watch", "concern", "challenge")
        news_terms = ("news", "headline", "latest", "recent event", "happened")
        performance_terms = (
            "perform",
            "performance",
            "stock price",
            "price trend",
            "return",
            "gained",
            "fallen",
        )
        movement_terms = ("why is", "moving", "price move", "move today")
        company_terms = (
            "what does",
            "company do",
            "business",
            "products",
            "services",
            "sector",
            "industry",
            "explain",
        )

        if any(term in text for term in broad_terms):
            return list(self.CONTEXT_SOURCES)
        if any(term in text for term in movement_terms):
            return ["stock_metrics", "price_history", "news", "research"]
        if any(term in text for term in risk_terms):
            return ["company_profile", "news", "research"]
        if any(term in text for term in news_terms):
            return ["company_profile", "news"]
        if any(term in text for term in performance_terms):
            return ["stock_metrics", "price_history"]
        if any(term in text for term in company_terms):
            return ["company_profile"]

        return [
            "company_profile",
            "stock_metrics",
            "price_history",
            "news",
            "research",
        ]

    def build_market_context(self, stock_data):
        if not isinstance(stock_data, dict):
            return {}

        fields = (
            "ticker",
            "company_name",
            "current_price",
            "previous_close",
            "price_change",
            "price_change_percent",
            "market_cap",
            "pe_ratio",
            "fifty_two_week_high",
            "fifty_two_week_low",
            "volume",
            "market",
            "exchange",
            "currency",
        )
        return self._clean_mapping(stock_data, fields)

    def summarize_price_history(self, history_data, period="1mo"):
        rows = history_data if isinstance(history_data, list) else []
        closes = []
        for row in rows:
            value = row.get("close") if isinstance(row, dict) else None
            number = self._safe_number(value)
            if number is not None:
                closes.append(number)

        if not closes:
            return {}

        start_price = closes[0]
        end_price = closes[-1]
        absolute_move = end_price - start_price
        percentage_move = (
            (absolute_move / start_price) * 100 if start_price != 0 else None
        )
        if percentage_move is None or abs(percentage_move) < 0.5:
            trend = "FLAT"
        elif percentage_move > 0:
            trend = "UP"
        else:
            trend = "DOWN"

        return {
            "period": period,
            "data_points": len(closes),
            "start_price": round(start_price, 2),
            "end_price": round(end_price, 2),
            "absolute_move": round(absolute_move, 2),
            "percentage_move": (
                round(percentage_move, 2) if percentage_move is not None else None
            ),
            "highest_close": round(max(closes), 2),
            "lowest_close": round(min(closes), 2),
            "trend": trend,
        }

    def build_news_context(self, articles, limit=3):
        normalized = []
        for article in articles if isinstance(articles, list) else []:
            if not isinstance(article, dict) or not article.get("title"):
                continue
            item = self._clean_mapping(
                article,
                ("title", "source", "published_at", "description", "sentiment"),
            )
            if item.get("description"):
                item["description"] = self._limit_text(item["description"], 400)
            normalized.append(item)
            if len(normalized) >= limit:
                break
        return normalized

    def build_research_context(self, research_result):
        if not isinstance(research_result, dict):
            return {}
        summary = research_result.get("research_summary")
        if not isinstance(summary, dict):
            return {}

        context = self._clean_mapping(
            summary,
            ("overall_view", "confidence", "price_analysis", "news_sentiment_analysis", "valuation_snapshot"),
        )
        for field in (
            "bullish_signals",
            "bearish_signals",
            "risk_factors",
            "things_to_watch",
        ):
            values = summary.get(field)
            if isinstance(values, list) and values:
                context[field] = [str(value) for value in values[:5]]
        analyst_summary = summary.get("analyst_style_summary")
        if analyst_summary:
            context["analyst_style_summary"] = self._limit_text(
                analyst_summary,
                800,
            )
        return context

    def build_recommendation_context(self, recommendation_result):
        if not isinstance(recommendation_result, dict):
            return {}

        context = self._clean_mapping(
            recommendation_result,
            ("method", "sector", "industry", "market", "signals"),
        )
        details = recommendation_result.get("recommendation_details")
        if isinstance(details, list) and details:
            context["related_companies"] = [
                self._clean_mapping(
                    detail,
                    ("ticker", "name", "reason", "confidence", "basis"),
                )
                for detail in details[:5]
                if isinstance(detail, dict)
            ]
        elif recommendation_result.get("recommendations"):
            context["related_companies"] = list(
                recommendation_result["recommendations"][:5]
            )
        if context:
            context["framing"] = (
                "Rule-based research signals and related companies; not a buy/sell recommendation."
            )
        return context

    def build_llm_context(
        self,
        mode,
        company_context=None,
        grounded_context=None,
        warnings=None,
        requested_sources=None,
    ):
        instructions = (
            "Answer the user's specific question using only the supplied application "
            "context. Distinguish available facts from missing data and state material "
            "uncertainty. Do not invent stock prices, financials, news, company facts, "
            "or sources. Do not call data real-time unless the context explicitly says "
            "it is current. Never promise returns or give absolute buy/sell guarantees. "
            "Provide concise, useful educational stock research rather than generic advice."
        )
        context = {
            "instructions": instructions,
            "chat_mode": mode,
            "single_turn": True,
            "context_requested": requested_sources or [],
        }

        if company_context:
            context["company_profile"] = company_context
        if grounded_context:
            context.update(grounded_context)
        if warnings:
            context["warnings_and_unavailable_sources"] = list(warnings)

        return context

    def _limit_text(self, value, limit=None):
        text = str(value).strip()
        maximum = limit or self.SUMMARY_LIMIT
        if len(text) <= maximum:
            return text
        return f"{text[:maximum].rstrip()}..."

    @staticmethod
    def _safe_number(value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) else None

    @staticmethod
    def _clean_mapping(source, fields):
        return {
            field: source[field]
            for field in fields
            if source.get(field) not in (None, "", "N/A", [], {})
        }
