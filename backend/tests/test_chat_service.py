import unittest

from app.services.chat_service import ChatService


class FakeLLMAgent:
    def __init__(self, warning=None):
        self.warning = warning
        self.calls = []

    def answer_question(self, question, context=None):
        self.calls.append((question, context))
        return {
            "response": "Test answer",
            "model": "test-chat-model",
            "warning": self.warning,
        }


class FakeCompanyService:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def get_company_profile(self, ticker):
        self.calls.append(ticker)
        if self.error:
            raise self.error
        return self.result


class FakeRAGService:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def test_rag(self, query, documents, top_k=None):
        self.calls.append(
            {"query": query, "documents": documents, "top_k": top_k}
        )
        return self.result


class FakeStockService:
    def __init__(self, stock=None, history=None, error=None):
        self.stock = stock if stock is not None else {}
        self.history = history if history is not None else []
        self.error = error
        self.stock_calls = []
        self.history_calls = []

    def get_stock_data(self, ticker):
        self.stock_calls.append(ticker)
        if self.error:
            raise self.error
        return self.stock

    def get_stock_history(self, ticker, period="6mo"):
        self.history_calls.append((ticker, period))
        if self.error:
            raise self.error
        return self.history


class FakeNewsService:
    def __init__(self, articles=None, warning=None, error=None):
        self.articles = articles if articles is not None else []
        self.last_warning = warning
        self.error = error
        self.calls = []

    def get_stock_news(self, query, page_size=10):
        self.calls.append((query, page_size))
        if self.error:
            raise self.error
        return self.articles


class FakeResearchService:
    def __init__(self, result=None, error=None):
        self.result = result if result is not None else {}
        self.error = error
        self.calls = []

    def get_research_report(self, ticker):
        self.calls.append(ticker)
        if self.error:
            raise self.error
        return self.result


class FakeRecommendationService:
    def __init__(self, result=None, error=None):
        self.result = result if result is not None else {}
        self.error = error
        self.calls = []

    def get_recommendations(self, ticker):
        self.calls.append(ticker)
        if self.error:
            raise self.error
        return self.result


class ChatServiceTests(unittest.TestCase):
    def _service(
        self,
        llm_agent=None,
        company_service=None,
        rag_service=None,
        stock_service=None,
        news_service=None,
        research_service=None,
        recommendation_service=None,
    ):
        return ChatService(
            llm_agent=llm_agent or FakeLLMAgent(),
            company_service=company_service
            or FakeCompanyService({"company_profile": {}}),
            rag_service=rag_service
            or FakeRAGService(
                {
                    "answer": "RAG answer",
                    "sources": [],
                    "metadata": {},
                    "warning": None,
                }
            ),
            stock_service=stock_service or FakeStockService(),
            news_service=news_service or FakeNewsService(),
            research_service=research_service or FakeResearchService(),
            recommendation_service=(
                recommendation_service or FakeRecommendationService()
            ),
        )

    def test_plain_llm_branch(self):
        llm_agent = FakeLLMAgent()
        result = self._service(llm_agent=llm_agent).chat(
            message="Explain diversification.",
            mode="llm",
        )

        self.assertEqual(result["answer"], "Test answer")
        self.assertEqual(result["mode"], "llm")
        self.assertFalse(result["metadata"]["used_rag"])
        self.assertFalse(result["metadata"]["used_company_context"])
        self.assertIn("instructions", llm_agent.calls[0][1])
        self.assertEqual(
            set(result),
            {"answer", "mode", "ticker", "sources", "metadata", "warning"},
        )

    def test_company_context_branch(self):
        llm_agent = FakeLLMAgent()
        company_service = FakeCompanyService(
            {
                "company_profile": {
                    "ticker": "INFY.NS",
                    "name": "Infosys Limited",
                    "sector": "Technology",
                    "business_summary": "Technology consulting services.",
                }
            }
        )
        service = self._service(
            llm_agent=llm_agent,
            company_service=company_service,
        )

        result = service.chat(
            message="What does this company do?",
            ticker="infy.ns",
            mode="auto",
        )

        self.assertEqual(result["mode"], "company")
        self.assertEqual(result["ticker"], "INFY.NS")
        self.assertTrue(result["metadata"]["used_company_context"])
        self.assertEqual(company_service.calls, ["INFY.NS"])
        profile = llm_agent.calls[0][1]["company_profile"]
        self.assertEqual(profile["name"], "Infosys Limited")
        self.assertEqual(result["metadata"]["sources_used"], ["company_profile"])
        self.assertEqual(
            result["metadata"]["context_status"],
            {"company_profile": "available"},
        )

    def test_performance_question_uses_only_stock_and_history(self):
        llm_agent = FakeLLMAgent()
        stock_service = FakeStockService(
            stock={"ticker": "AAPL", "current_price": 110, "previous_close": 108},
            history=[{"close": 100}, {"close": 110}],
        )
        result = self._service(
            llm_agent=llm_agent,
            stock_service=stock_service,
        ).chat(
            message="How has Apple stock performed recently?",
            ticker="AAPL",
            mode="company",
        )

        self.assertEqual(
            result["metadata"]["sources_used"],
            ["stock_metrics", "price_history"],
        )
        context = llm_agent.calls[0][1]
        self.assertEqual(context["price_history"]["percentage_move"], 10.0)
        self.assertNotIn("company_profile", context)

    def test_news_question_uses_company_and_recent_news(self):
        llm_agent = FakeLLMAgent()
        company_service = FakeCompanyService(
            {"company_profile": {"ticker": "AAPL", "name": "Apple Inc."}}
        )
        news_service = FakeNewsService(
            [{"title": "Apple launches product", "source": "Wire"}]
        )
        result = self._service(
            llm_agent=llm_agent,
            company_service=company_service,
            news_service=news_service,
        ).chat(
            message="What is the latest Apple news?",
            ticker="AAPL",
            mode="company",
        )

        self.assertEqual(
            result["metadata"]["sources_used"],
            ["company_profile", "news"],
        )
        self.assertEqual(news_service.calls, [("Apple Inc.", 3)])
        self.assertEqual(llm_agent.calls[0][1]["news"][0]["source"], "Wire")

    def test_broad_investment_question_uses_all_available_sources(self):
        llm_agent = FakeLLMAgent()
        service = self._service(
            llm_agent=llm_agent,
            company_service=FakeCompanyService(
                {"company_profile": {"ticker": "AAPL", "name": "Apple Inc."}}
            ),
            stock_service=FakeStockService(
                stock={"ticker": "AAPL", "current_price": 110},
                history=[{"close": 100}, {"close": 110}],
            ),
            news_service=FakeNewsService([{"title": "Apple update"}]),
            research_service=FakeResearchService(
                {
                    "research_summary": {
                        "overall_view": "mixed",
                        "risk_factors": ["Valuation"],
                    }
                }
            ),
            recommendation_service=FakeRecommendationService(
                {"recommendations": ["MSFT"], "method": "rule_based"}
            ),
        )

        result = service.chat("Should I buy Apple?", ticker="AAPL", mode="company")

        self.assertEqual(
            result["metadata"]["sources_used"],
            list(service.chat_agent.CONTEXT_SOURCES),
        )
        self.assertIn("buy/sell", llm_agent.calls[0][1]["instructions"])

    def test_unavailable_news_is_reported_without_failing_chat(self):
        result = self._service(
            company_service=FakeCompanyService(
                {"company_profile": {"ticker": "AAPL", "name": "Apple Inc."}}
            ),
            news_service=FakeNewsService(
                [],
                warning="News providers are temporarily unavailable.",
            ),
        ).chat("What is the latest Apple news?", ticker="AAPL", mode="company")

        self.assertEqual(result["answer"], "Test answer")
        self.assertEqual(result["metadata"]["sources_used"], ["company_profile"])
        self.assertEqual(result["metadata"]["context_status"]["news"], "unavailable")
        self.assertIn("News providers", result["warning"])

    def test_unavailable_stock_is_reported_without_failing_chat(self):
        result = self._service(
            stock_service=FakeStockService(error=RuntimeError("offline")),
        ).chat(
            "How has Apple stock performed recently?",
            ticker="AAPL",
            mode="company",
        )

        self.assertEqual(result["answer"], "Test answer")
        self.assertEqual(result["metadata"]["sources_used"], [])
        self.assertEqual(
            result["metadata"]["context_status"],
            {"stock_metrics": "unavailable", "price_history": "unavailable"},
        )
        self.assertIn("provider request failed", result["warning"])

    def test_company_lookup_falls_back_with_warning(self):
        llm_agent = FakeLLMAgent()
        company_service = FakeCompanyService(
            result={
                "company_profile": {"ticker": "UNKNOWN"},
                "warning": "Company profile unavailable.",
            }
        )
        result = self._service(
            llm_agent=llm_agent,
            company_service=company_service,
        ).chat(
            message="What does this company do?",
            ticker="UNKNOWN",
            mode="company",
        )

        self.assertEqual(result["answer"], "Test answer")
        self.assertFalse(result["metadata"]["used_company_context"])
        self.assertIn("Company profile unavailable", result["warning"])
        self.assertNotIn("company_profile", llm_agent.calls[0][1])

    def test_rag_delegation_preserves_sources(self):
        sources = [{"document_id": "doc-1", "chunk_id": "doc-1:chunk:0"}]
        rag_service = FakeRAGService(
            {
                "answer": "Grounded answer",
                "sources": sources,
                "metadata": {
                    "model": "test-chat-model",
                    "embedding_model": "test-embedding-model",
                    "retrieval_k": 2,
                },
                "warning": None,
            }
        )
        documents = [{"document_id": "doc-1", "text": "Evidence"}]

        result = self._service(rag_service=rag_service).chat(
            message="Question",
            ticker="TEST",
            mode="auto",
            documents=documents,
            top_k=2,
        )

        self.assertEqual(result["mode"], "rag")
        self.assertIs(result["sources"], sources)
        self.assertTrue(result["metadata"]["used_rag"])
        self.assertEqual(result["metadata"]["retrieval_k"], 2)
        self.assertEqual(result["metadata"]["sources_used"], [])
        self.assertEqual(result["metadata"]["context_status"], {})
        self.assertEqual(rag_service.calls[0]["documents"], documents)

    def test_invalid_explicit_modes_return_warning_without_dependencies(self):
        llm_agent = FakeLLMAgent()
        rag_service = FakeRAGService({})
        service = self._service(
            llm_agent=llm_agent,
            rag_service=rag_service,
        )

        no_documents = service.chat("Question", mode="rag")
        no_ticker = service.chat("Question", mode="company")

        self.assertIn("document", no_documents["warning"])
        self.assertIn("ticker", no_ticker["warning"])
        self.assertEqual(llm_agent.calls, [])
        self.assertEqual(rag_service.calls, [])

    def test_llm_unavailable_returns_warning_and_no_answer(self):
        result = self._service(
            llm_agent=FakeLLMAgent("Chat model unavailable.")
        ).chat(
            message="Question",
            mode="llm",
        )

        self.assertIsNone(result["answer"])
        self.assertEqual(result["warning"], "Chat model unavailable.")


if __name__ == "__main__":
    unittest.main()
