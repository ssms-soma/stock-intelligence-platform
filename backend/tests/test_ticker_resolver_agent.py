import unittest

from app.agents.ticker_resolver_agent import TickerResolverAgent


class TickerResolverAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = TickerResolverAgent()

    def test_resolves_known_company_aliases(self):
        cases = {
            "Infosys": "INFY.NS",
            "Reliance": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "Tata Consultancy": "TCS.NS",
            "Apple": "AAPL",
            "Microsoft": "MSFT",
            "Tesla": "TSLA",
        }

        for query, expected_ticker in cases.items():
            with self.subTest(query=query):
                result = self.agent.resolve(query)
                self.assertTrue(result["resolved"])
                self.assertEqual(result["ticker"], expected_ticker)
                self.assertEqual(result["source"], "known_mapping")
                self.assertEqual(result["confidence"], "high")

    def test_alias_matching_is_case_insensitive_and_normalizes_spacing(self):
        result = self.agent.resolve("  tata   CONSULTANCY  ")

        self.assertEqual(result["ticker"], "TCS.NS")
        self.assertEqual(result["name"], "Tata Consultancy Services Limited")

    def test_ampersand_and_and_aliases_match(self):
        ampersand = self.agent.resolve("Larsen & Toubro")
        word = self.agent.resolve("Larsen and Toubro")

        self.assertEqual(ampersand["ticker"], "LT.NS")
        self.assertEqual(word["ticker"], "LT.NS")

    def test_preserves_exact_ticker_input(self):
        cases = {
            "AAPL": "AAPL",
            "infy.ns": "INFY.NS",
            "RELIANCE.BO": "RELIANCE.BO",
            "BRK-B": "BRK-B",
        }

        for query, expected_ticker in cases.items():
            with self.subTest(query=query):
                result = self.agent.resolve(query)
                self.assertTrue(result["resolved"])
                self.assertEqual(result["ticker"], expected_ticker)
                self.assertEqual(result["source"], "ticker_input")

    def test_blank_input_is_unresolved(self):
        result = self.agent.resolve("   ")

        self.assertFalse(result["resolved"])
        self.assertIsNone(result["ticker"])
        self.assertIn("enter", result["warning"].lower())

    def test_unknown_multi_word_input_is_unresolved(self):
        result = self.agent.resolve("some unknown company")

        self.assertFalse(result["resolved"])
        self.assertIsNone(result["ticker"])
        self.assertIn("Could not resolve", result["warning"])

    def test_unknown_one_word_ticker_shaped_input_is_preserved(self):
        result = self.agent.resolve("example")

        self.assertTrue(result["resolved"])
        self.assertEqual(result["ticker"], "EXAMPLE")
        self.assertEqual(result["source"], "ticker_input")


if __name__ == "__main__":
    unittest.main()
