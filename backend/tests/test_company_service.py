import unittest
from unittest.mock import Mock

from app.services.company_service import CompanyService


class CompanyServiceCacheTests(unittest.TestCase):
    def test_valid_company_profile_is_cached(self):
        service = CompanyService()
        service.company_agent = Mock()
        service.company_agent.get_company_profile.return_value = {
            "ticker": "AMZN",
            "company_profile": {
                "long_name": "Amazon.com, Inc.",
                "sector": "Consumer Cyclical",
            },
            "source": "yfinance",
        }

        first = service.get_company_profile("amzn")
        second = service.get_company_profile("AMZN")

        self.assertEqual(first, second)
        service.company_agent.get_company_profile.assert_called_once_with("AMZN")

    def test_warning_profile_is_not_cached(self):
        service = CompanyService(stock_service=Mock())
        service.stock_service.get_stock_data.return_value = {}
        service.company_agent = Mock()
        service.company_agent.get_company_profile.return_value = {
            "ticker": "AMZN",
            "company_profile": {"long_name": "Amazon.com, Inc."},
            "warning": "Company profile is temporarily unavailable.",
        }

        service.get_company_profile("AMZN")
        service.get_company_profile("AMZN")

        self.assertEqual(service.company_agent.get_company_profile.call_count, 2)

    def test_empty_profile_is_not_cached(self):
        service = CompanyService(stock_service=Mock())
        service.stock_service.get_stock_data.return_value = {}
        service.company_agent = Mock()
        service.company_agent.get_company_profile.return_value = {
            "ticker": "AMZN",
            "company_profile": {
                "long_name": None,
                "sector": None,
                "industry": None,
            },
            "source": "yfinance",
        }

        service.get_company_profile("AMZN")
        service.get_company_profile("AMZN")

        self.assertEqual(service.company_agent.get_company_profile.call_count, 2)

    def test_degraded_profile_keeps_identity_and_adds_stock_metadata(self):
        company_agent = Mock()
        company_agent.get_company_profile.return_value = {
            "ticker": "RELIANCE.NS",
            "company_profile": {
                "ticker": "RELIANCE.NS",
                "name": "Reliance Industries Limited",
                "country": "India",
                "business_summary": None,
            },
            "warning": "Company profile is temporarily unavailable.",
        }
        stock_service = Mock()
        stock_service.get_stock_data.return_value = {
            "company_name": "Reliance Industries Limited",
            "sector": "Energy",
            "country": "India",
            "market": "India",
            "exchange": "NSE",
            "currency": "INR",
        }
        service = CompanyService(
            company_agent=company_agent,
            stock_service=stock_service,
        )

        result = service.get_company_profile("reliance.ns")
        profile = result["company_profile"]

        self.assertEqual(profile["name"], "Reliance Industries Limited")
        self.assertEqual(profile["sector"], "Energy")
        self.assertEqual(profile["exchange"], "NSE")
        self.assertEqual(profile["currency"], "INR")
        self.assertIsNone(profile["business_summary"])
        self.assertIn("temporarily unavailable", result["warning"])
        stock_service.get_stock_data.assert_called_once_with("RELIANCE.NS")


if __name__ == "__main__":
    unittest.main()
