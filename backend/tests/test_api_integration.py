import unittest

from fastapi.testclient import TestClient

from app.main import app


class APIIntegrationSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_ticker_resolution_endpoint(self):
        response = self.client.get(
            "/api/search/resolve",
            params={"query": "Apple"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["resolved"])
        self.assertEqual(response.json()["ticker"], "AAPL")


if __name__ == "__main__":
    unittest.main()
