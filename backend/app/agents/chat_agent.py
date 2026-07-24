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

    def build_llm_context(self, mode, company_context=None):
        instructions = (
            "Provide educational stock-research information, not financial "
            "advice. Use supplied context when available. Do not invent facts "
            "or sources. If the available context is insufficient, state that "
            "limitation clearly."
        )
        context = {
            "instructions": instructions,
            "chat_mode": mode,
            "single_turn": True,
        }

        if company_context:
            context["company_profile"] = company_context

        return context

    def _limit_text(self, value):
        text = str(value).strip()
        if len(text) <= self.SUMMARY_LIMIT:
            return text
        return f"{text[: self.SUMMARY_LIMIT].rstrip()}..."
