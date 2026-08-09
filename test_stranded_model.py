import sys
import os
import unittest
from pydantic import ValidationError

# Añadir 01_modelo_documentado al PATH de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "01_modelo_documentado")))

from stranded_model import (
    StrandedCapacityCalculator,
    CalculatorInput,
    CalculatorOutput,
    COOLING_BENCHMARKS,
    ELECTRICITY_RATE_PER_KWH,
    COLOCATION_RATE_PER_KW_MONTH,
    LIFECYCLE_YEARS,
    RECOVERABLE_FACTOR,
    REMEDIATION_COST_PER_MW,
)


class TestStrandedCapacityCalculator(unittest.TestCase):
    """Suite de pruebas para validar el modelo de Stranded Capacity."""

    def setUp(self):
        self.calculator = StrandedCapacityCalculator()

    def test_default_instantiation(self):
        """Verifica que la calculadora se instancie con los valores por defecto esperados."""
        self.assertEqual(self.calculator.electricity_rate, ELECTRICITY_RATE_PER_KWH)
        self.assertEqual(self.calculator.colocation_rate, COLOCATION_RATE_PER_KW_MONTH)
        self.assertEqual(self.calculator.lifecycle_years, LIFECYCLE_YEARS)

    def test_valid_cooling_types(self):
        """Verifica que los tres tipos de cooling válidos generen salidas correctas."""
        cooling_types = ["air-cooled", "hybrid", "liquid-cooled"]
        for cooling in cooling_types:
            with self.subTest(cooling_type=cooling):
                result = self.calculator.calculate(facility_mw=10.0, utilization_pct=85.0, cooling_type=cooling)
                self.assertIsInstance(result, CalculatorOutput)
                self.assertEqual(result.facility_size_mw, 10.0)
                self.assertEqual(result.cooling_type, cooling)
                self.assertIn("min", result.stranded_capacity_pct_range)
                self.assertIn("mid", result.stranded_capacity_pct_range)
                self.assertIn("max", result.stranded_capacity_pct_range)

    def test_stranded_capacity_mw_calculation(self):
        """Verifica el cálculo de MW varados según los porcentajes definidos."""
        facility_mw = 20.0
        utilization = 80.0
        cooling = "air-cooled"

        result = self.calculator.calculate(facility_mw=facility_mw, utilization_pct=utilization, cooling_type=cooling)

        pct_min = result.stranded_capacity_pct_range["min"]
        pct_mid = result.stranded_capacity_pct_range["mid"]
        pct_max = result.stranded_capacity_pct_range["max"]

        expected_mw_min = round(facility_mw * (pct_min / 100.0), 2)
        expected_mw_mid = round(facility_mw * (pct_mid / 100.0), 2)
        expected_mw_max = round(facility_mw * (pct_max / 100.0), 2)

        self.assertEqual(result.stranded_capacity_mw_range["min"], expected_mw_min)
        self.assertEqual(result.stranded_capacity_mw_range["mid"], expected_mw_mid)
        self.assertEqual(result.stranded_capacity_mw_range["max"], expected_mw_max)

    def test_low_utilization_penalty(self):
        """Verifica que utilizaciones menores al 50% incrementen la penalización en pct_mid."""
        facility_mw = 10.0
        cooling = "air-cooled"

        # Caso base (>= 50%)
        res_normal = self.calculator.calculate(facility_mw=facility_mw, utilization_pct=60.0, cooling_type=cooling)
        # Caso con penalización (< 50%)
        res_low_util = self.calculator.calculate(facility_mw=facility_mw, utilization_pct=30.0, cooling_type=cooling)

        base_pct_mid = COOLING_BENCHMARKS["air-cooled"]["stranded_pct_range"]["mid"]
        gap_penalty = (50.0 - 30.0) * 0.2  # 20 * 0.2 = 4.0%
        expected_pct_mid = min(COOLING_BENCHMARKS["air-cooled"]["stranded_pct_range"]["max"], base_pct_mid + gap_penalty)

        self.assertEqual(res_normal.stranded_capacity_pct_range["mid"], base_pct_mid)
        self.assertEqual(res_low_util.stranded_capacity_pct_range["mid"], expected_pct_mid)

    def test_financial_loss_formulas(self):
        """Verifica las fórmulas de Floor, Ceiling y Mid para pérdidas financieras."""
        facility_mw = 15.0
        utilization = 87.0
        cooling = "hybrid"

        result = self.calculator.calculate(facility_mw=facility_mw, utilization_pct=utilization, cooling_type=cooling)

        mw_mid = result.stranded_capacity_mw_range["mid"]
        kw_mid = mw_mid * 1000.0
        pue = COOLING_BENCHMARKS[cooling]["pue_ref"]
        capex_mw = COOLING_BENCHMARKS[cooling]["capex_per_mw"]

        # Floor: OPEX Energía + CAPEX amortizado
        opex_energy = kw_mid * 8760 * pue * self.calculator.electricity_rate
        amortized_capex = (capex_mw / 1000.0 * kw_mid) / self.calculator.lifecycle_years
        expected_floor = round(opex_energy + amortized_capex, 2)

        # Ceiling: Costo Oportunidad Colocation
        expected_ceiling = round(kw_mid * self.calculator.colocation_rate * 12.0, 2)

        # Mid: Promedio Floor & Ceiling
        expected_mid = round((expected_floor + expected_ceiling) / 2.0, 2)

        self.assertEqual(result.annual_financial_loss_usd.min_usd_annual, expected_floor)
        self.assertEqual(result.annual_financial_loss_usd.max_usd_annual, expected_ceiling)
        self.assertEqual(result.annual_financial_loss_usd.mid_usd_annual, expected_mid)

    def test_recoverable_value_and_roi(self):
        """Verifica el cálculo del valor recuperable (80%) y el ROI en meses."""
        facility_mw = 10.0
        utilization = 80.0
        cooling = "liquid-cooled"

        result = self.calculator.calculate(facility_mw=facility_mw, utilization_pct=utilization, cooling_type=cooling)

        loss_mid = result.annual_financial_loss_usd.mid_usd_annual
        expected_recoverable = round(loss_mid * RECOVERABLE_FACTOR, 2)
        self.assertAlmostEqual(result.potential_recoverable_value_usd, expected_recoverable, delta=0.02)

        total_remediation_cost = facility_mw * REMEDIATION_COST_PER_MW
        expected_roi_mid = round((total_remediation_cost / expected_recoverable) * 12.0, 1)
        self.assertAlmostEqual(result.estimated_recovery_time_months["mid_months"], expected_roi_mid, delta=0.1)

    def test_invalid_inputs_raise_errors(self):
        """Verifica que entradas inválidas disparen excepciones de Pydantic o ValueError."""
        # facility_mw <= 0
        with self.assertRaises(ValidationError):
            self.calculator.calculate(facility_mw=0.0, utilization_pct=80.0, cooling_type="air-cooled")

        with self.assertRaises(ValidationError):
            self.calculator.calculate(facility_mw=-5.0, utilization_pct=80.0, cooling_type="air-cooled")

        # utilization_pct fuera de [0, 100]
        with self.assertRaises(ValidationError):
            self.calculator.calculate(facility_mw=10.0, utilization_pct=-10.0, cooling_type="air-cooled")

        with self.assertRaises(ValidationError):
            self.calculator.calculate(facility_mw=10.0, utilization_pct=105.0, cooling_type="air-cooled")

        # cooling_type inválido
        with self.assertRaises((ValidationError, ValueError)):
            self.calculator.calculate(facility_mw=10.0, utilization_pct=80.0, cooling_type="geothermal")


if __name__ == "__main__":
    unittest.main()
