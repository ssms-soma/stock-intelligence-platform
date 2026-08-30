import unittest

from app.agents.chat_agent import ChatAgent


class ChatAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = ChatAgent()

    def test_auto_mode_selection(self):
        self.assertEqual(
            self.agent.select_mode("AUTO", documents=[{"text": "sample"}]),
            ("rag", None),
        )
        self.assertEqual(
            self.agent.select_mode("auto", ticker="INFY.NS", documents=[]),
            ("company", None),
        )
        self.assertEqual(
            self.agent.select_mode("auto", documents=[]),
            ("llm", None),
        )

    def test_explicit_modes_require_inputs(self):
        rag_mode, rag_warning = self.agent.select_mode("rag", documents=[])
        company_mode, company_warning = self.agent.select_mode(
            "company",
            ticker=None,
        )

        self.assertEqual(rag_mode, "rag")
        self.assertIn("document", rag_warning)
        self.assertEqual(company_mode, "company")
        self.assertIn("ticker", company_warning)

    def test_builds_allowlisted_bounded_company_context(self):
        long_summary = "x" * (ChatAgent.SUMMARY_LIMIT + 100)
        result = {
            "company_profile": {
                "ticker": "INFY.NS",
                "name": "Infosys Limited",
                "sector": "Technology",
                "business_summary": long_summary,
                "website": "https://example.test",
                "price_target": {"mean": 100},
            }
        }

        context = self.agent.build_company_context(result)

        self.assertEqual(context["ticker"], "INFY.NS")
        self.assertEqual(context["name"], "Infosys Limited")
        self.assertLessEqual(
            len(context["business_summary"]),
            ChatAgent.SUMMARY_LIMIT + 3,
        )
        self.assertNotIn("website", context)
        self.assertNotIn("price_target", context)

    def test_rejects_profile_without_informative_context(self):
        context = self.agent.build_company_context(
            {"company_profile": {"ticker": "INFY.NS", "country": "India"}}
        )

        self.assertEqual(context, {})

    def test_selects_question_aware_company_context(self):
        self.assertEqual(
            self.agent.select_context_sources("What does Apple do?"),
            ["company_profile"],
        )
        self.assertEqual(
            self.agent.select_context_sources(
                "How has Apple stock performed recently?"
            ),
            ["stock_metrics", "price_history"],
        )
        self.assertEqual(
            self.agent.select_context_sources("What is the latest Apple news?"),
            ["company_profile", "news"],
        )
        self.assertEqual(
            self.agent.select_context_sources(
                "What recent news should investors care about?"
            ),
            ["company_profile", "news"],
        )
        self.assertEqual(
            self.agent.select_context_sources(
                "What risks should an investor watch?"
            ),
            ["company_profile", "news", "research"],
        )
        self.assertEqual(
            self.agent.select_context_sources("Should I buy Apple?"),
            list(self.agent.CONTEXT_SOURCES),
        )

    def test_summarizes_price_history_safely(self):
        summary = self.agent.summarize_price_history(
            [
                {"close": 100},
                {"close": None},
                {"close": 110},
                {"close": 105},
            ],
            period="1mo",
        )

        self.assertEqual(
            summary,
            {
                "period": "1mo",
                "data_points": 3,
                "start_price": 100.0,
                "end_price": 105.0,
                "absolute_move": 5.0,
                "percentage_move": 5.0,
                "highest_close": 110.0,
                "lowest_close": 100.0,
                "trend": "UP",
            },
        )
        self.assertEqual(self.agent.summarize_price_history([]), {})
        self.assertIsNone(
            self.agent.summarize_price_history(
                [{"close": 0}, {"close": 2}]
            )["percentage_move"]
        )


if __name__ == "__main__":
    unittest.main()
