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
        service = CompanyService()
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
        service = CompanyService()
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


if __name__ == "__main__":
    unittest.main()
