import unittest

from app.agents.company_agent import CompanyAgent


class CompanyAgentTests(unittest.TestCase):
    def test_known_company_name_is_available_without_info(self):
        self.assertEqual(
            CompanyAgent()._get_known_company_name("RELIANCE.NS"),
            "Reliance Industries Limited",
        )

    def test_safe_call_logs_external_failure_without_traceback(self):
        agent = CompanyAgent()

        with self.assertLogs(
            "app.agents.company_agent",
            level="WARNING",
        ) as captured:
            result = agent._safe_call(
                lambda: (_ for _ in ()).throw(ConnectionError("reset")),
                timeout_seconds=1,
                label="info",
                ticker="TEST",
            )

        self.assertIsNone(result)
        self.assertEqual(
            captured.output,
            [
                "WARNING:app.agents.company_agent:"
                "yfinance info unavailable for TEST (ConnectionError)"
            ],
        )
        self.assertNotIn("Traceback", captured.output[0])


if __name__ == "__main__":
    unittest.main()
