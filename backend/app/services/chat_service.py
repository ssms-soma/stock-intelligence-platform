from app.agents.chat_agent import ChatAgent
from app.agents.llm_agent import LLMAgent
from app.services.company_service import CompanyService
from app.services.news_service import NewsService
from app.services.rag_service import RAGService
from app.services.recommendation_service import RecommendationService
from app.services.research_service import ResearchService
from app.services.stock_service import StockService


class ChatService:
    def __init__(
        self,
        chat_agent=None,
        llm_agent=None,
        rag_service=None,
        company_service=None,
        stock_service=None,
        news_service=None,
        research_service=None,
        recommendation_service=None,
    ):
        self.chat_agent = chat_agent or ChatAgent()
        self.llm_agent = llm_agent or LLMAgent()
        self.rag_service = rag_service or RAGService()
        self.company_service = company_service or CompanyService()
        self.stock_service = stock_service or StockService()
        self.news_service = news_service or NewsService()
        self.research_service = research_service or ResearchService()
        self.recommendation_service = (
            recommendation_service or RecommendationService()
        )

    def chat(
        self,
        message,
        ticker=None,
        mode="auto",
        documents=None,
        top_k=None,
    ):
        cleaned_message = message.strip() if isinstance(message, str) else ""
        normalized_ticker = ticker.strip().upper() if isinstance(ticker, str) else None
        document_data = documents if isinstance(documents, list) else []

        if not cleaned_message:
            return self._response(
                mode=(mode or "auto").strip().lower(),
                ticker=normalized_ticker,
                warning="A non-empty chat message is required.",
            )

        selected_mode, mode_warning = self.chat_agent.select_mode(
            mode=mode,
            ticker=normalized_ticker,
            documents=document_data,
        )
        if mode_warning:
            return self._response(
                mode=selected_mode,
                ticker=normalized_ticker,
                warning=mode_warning,
            )

        if selected_mode == "rag":
            return self._rag_chat(
                message=cleaned_message,
                ticker=normalized_ticker,
                documents=document_data,
                top_k=top_k,
            )

        if selected_mode == "company":
            return self._company_chat(
                message=cleaned_message,
                ticker=normalized_ticker,
            )

        return self._llm_chat(
            message=cleaned_message,
            ticker=normalized_ticker,
            mode="llm",
        )

    def _llm_chat(
        self,
        message,
        ticker,
        mode,
        company_context=None,
        grounded_context=None,
        requested_sources=None,
        sources_used=None,
        context_status=None,
        existing_warning=None,
    ):
        llm_result = self.llm_agent.answer_question(
            question=message,
            context=self.chat_agent.build_llm_context(
                mode=mode,
                company_context=company_context,
                grounded_context=grounded_context,
                warnings=self._warning_list(existing_warning),
                requested_sources=requested_sources,
            ),
        )
        llm_warning = llm_result.get("warning")

        return self._response(
            answer=None if llm_warning else llm_result.get("response"),
            mode=mode,
            ticker=ticker,
            model=llm_result.get("model"),
            used_company_context=bool(company_context),
            sources_requested=requested_sources,
            sources_used=sources_used,
            context_status=context_status,
            warning=self._join_warnings(existing_warning, llm_warning),
        )

    def _company_chat(self, message, ticker):
        requested_sources = self.chat_agent.select_context_sources(message)
        grounded_context = {}
        context_status = {}
        sources_used = []
        warnings = []

        for source in requested_sources:
            context_value, source_warning = self._collect_context_source(
                source,
                ticker,
                grounded_context,
            )
            if context_value:
                grounded_context[source] = context_value
                sources_used.append(source)
                context_status[source] = (
                    "degraded" if source_warning else "available"
                )
            else:
                context_status[source] = "unavailable"

            if source_warning:
                warnings.append(f"{self._source_label(source)}: {source_warning}")
            elif not context_value:
                warnings.append(
                    f"{self._source_label(source)} is temporarily unavailable."
                )

        company_context = grounded_context.pop("company_profile", None)

        return self._llm_chat(
            message=message,
            ticker=ticker,
            mode="company",
            company_context=company_context,
            grounded_context=grounded_context,
            requested_sources=requested_sources,
            sources_used=sources_used,
            context_status=context_status,
            existing_warning=self._join_warnings(*warnings),
        )

    def _collect_context_source(self, source, ticker, collected_context):
        try:
            if source == "company_profile":
                result = self.company_service.get_company_profile(ticker)
                warning = result.get("warning") if isinstance(result, dict) else None
                return self.chat_agent.build_company_context(result), warning

            if source == "stock_metrics":
                result = self.stock_service.get_stock_data(ticker)
                warning = result.get("warning") if isinstance(result, dict) else None
                return self.chat_agent.build_market_context(result), warning

            if source == "price_history":
                period = "1mo"
                result = self.stock_service.get_stock_history(ticker, period=period)
                return self.chat_agent.summarize_price_history(result, period), None

            if source == "news":
                company = collected_context.get("company_profile") or {}
                query = company.get("name") or ticker
                result = self.news_service.get_stock_news(query, page_size=3)
                return (
                    self.chat_agent.build_news_context(result),
                    self.news_service.last_warning,
                )

            if source == "research":
                result = self.research_service.get_research_report(ticker)
                warnings = result.get("warnings") if isinstance(result, dict) else None
                return (
                    self.chat_agent.build_research_context(result),
                    self._join_warnings(warnings),
                )

            if source == "recommendations":
                result = self.recommendation_service.get_recommendations(ticker)
                warning = result.get("warning") if isinstance(result, dict) else None
                return self.chat_agent.build_recommendation_context(result), warning
        except Exception:
            return {}, "The provider request failed."

        return {}, "The context source is unsupported."

    def _rag_chat(self, message, ticker, documents, top_k):
        rag_result = self.rag_service.test_rag(
            query=message,
            documents=documents,
            top_k=top_k,
        )
        rag_metadata = (
            rag_result.get("metadata")
            if isinstance(rag_result.get("metadata"), dict)
            else {}
        )

        return self._response(
            answer=rag_result.get("answer"),
            mode="rag",
            ticker=ticker,
            sources=rag_result.get("sources") or [],
            model=rag_metadata.get("model"),
            used_rag=True,
            warning=rag_result.get("warning"),
            extra_metadata={
                "embedding_model": rag_metadata.get("embedding_model"),
                "retrieval_k": rag_metadata.get("retrieval_k"),
            },
        )

    def _response(
        self,
        mode,
        ticker,
        answer=None,
        sources=None,
        model=None,
        used_rag=False,
        used_company_context=False,
        sources_requested=None,
        sources_used=None,
        context_status=None,
        warning=None,
        extra_metadata=None,
    ):
        metadata = {
            "model": model,
            "used_rag": used_rag,
            "used_company_context": used_company_context,
            "single_turn": True,
            "sources_requested": sources_requested or [],
            "sources_used": sources_used or [],
            "context_status": context_status or {},
        }
        if extra_metadata:
            metadata.update(
                {
                    key: value
                    for key, value in extra_metadata.items()
                    if value is not None
                }
            )

        return {
            "answer": answer,
            "mode": mode,
            "ticker": ticker,
            "sources": sources or [],
            "metadata": metadata,
            "warning": warning,
        }

    @staticmethod
    def _join_warnings(*warnings):
        unique_warnings = []
        for warning in warnings:
            values = warning if isinstance(warning, list) else [warning]
            for value in values:
                if value and value not in unique_warnings:
                    unique_warnings.append(str(value))
        return " ".join(unique_warnings) or None

    @staticmethod
    def _warning_list(warning):
        return [warning] if warning else []

    @staticmethod
    def _source_label(source):
        return source.replace("_", " ").capitalize()
