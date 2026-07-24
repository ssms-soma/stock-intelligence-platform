from app.agents.chat_agent import ChatAgent
from app.agents.llm_agent import LLMAgent
from app.services.company_service import CompanyService
from app.services.rag_service import RAGService


class ChatService:
    def __init__(
        self,
        chat_agent=None,
        llm_agent=None,
        rag_service=None,
        company_service=None,
    ):
        self.chat_agent = chat_agent or ChatAgent()
        self.llm_agent = llm_agent or LLMAgent()
        self.rag_service = rag_service or RAGService()
        self.company_service = company_service or CompanyService()

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
        existing_warning=None,
    ):
        llm_result = self.llm_agent.answer_question(
            question=message,
            context=self.chat_agent.build_llm_context(
                mode=mode,
                company_context=company_context,
            ),
        )
        llm_warning = llm_result.get("warning")

        return self._response(
            answer=None if llm_warning else llm_result.get("response"),
            mode=mode,
            ticker=ticker,
            model=llm_result.get("model"),
            used_company_context=bool(company_context),
            warning=self._join_warnings(existing_warning, llm_warning),
        )

    def _company_chat(self, message, ticker):
        company_result = None
        lookup_warning = None

        try:
            company_result = self.company_service.get_company_profile(ticker)
            if isinstance(company_result, dict):
                lookup_warning = company_result.get("warning")
        except Exception:
            lookup_warning = "Company context is temporarily unavailable."

        company_context = self.chat_agent.build_company_context(company_result)
        if not company_context and not lookup_warning:
            lookup_warning = "Company context is unavailable for this ticker."

        return self._llm_chat(
            message=message,
            ticker=ticker,
            mode="company",
            company_context=company_context,
            existing_warning=lookup_warning,
        )

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
        warning=None,
        extra_metadata=None,
    ):
        metadata = {
            "model": model,
            "used_rag": used_rag,
            "used_company_context": used_company_context,
            "single_turn": True,
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
            if warning and warning not in unique_warnings:
                unique_warnings.append(str(warning))
        return " ".join(unique_warnings) or None
