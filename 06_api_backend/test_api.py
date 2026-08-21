"""
Unit Tests for FastAPI Backend (06_api_backend)
==============================================
Test suite validating HTTP endpoints, input validations, and error handling.
"""

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Asegurar path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "06_api_backend"))

from main import app


class TestFastAPIBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_read_root(self):
        """Verifica que el endpoint / responda 200 OK y estado online."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("version", data)

    def test_get_benchmarks(self):
        """Verifica que /api/v1/benchmarks devuelva las matrices esperadas."""
        response = self.client.get("/api/v1/benchmarks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cooling_benchmarks", data)
        self.assertIn("air-cooled", data["cooling_benchmarks"])

    def test_calculate_valid_input(self):
        """Verifica el cálculo determinístico con inputs válidos."""
        payload = {
            "facility_mw": 15.0,
            "utilization_pct": 87.0,
            "cooling_type": "air-cooled"
        }
        response = self.client.post("/api/v1/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stranded_capacity_mw_range", data)
        self.assertIn("annual_financial_loss_usd", data)
        self.assertIn("kpis", data)
        self.assertEqual(data["facility_size_mw"], 15.0)

    def test_calculate_invalid_utilization(self):
        """Verifica error de validación 422 cuando utilization_pct > 100."""
        payload = {
            "facility_mw": 15.0,
            "utilization_pct": 120.0,
            "cooling_type": "air-cooled"
        }
        response = self.client.post("/api/v1/calculate", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_calculate_invalid_facility_mw(self):
        """Verifica error de validación 422 cuando facility_mw <= 0."""
        payload = {
            "facility_mw": -5.0,
            "utilization_pct": 50.0,
            "cooling_type": "air-cooled"
        }
        response = self.client.post("/api/v1/calculate", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_monte_carlo_endpoint(self):
        """Verifica la ejecución de simulación de Monte Carlo por API."""
        payload = {
            "facility_mw": 10.0,
            "utilization_pct": 75.0,
            "cooling_type": "liquid-cooled",
            "num_simulations": 500
        }
        response = self.client.post("/api/v1/monte-carlo", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main()
