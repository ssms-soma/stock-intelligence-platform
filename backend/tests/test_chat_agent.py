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


if __name__ == "__main__":
    unittest.main()
