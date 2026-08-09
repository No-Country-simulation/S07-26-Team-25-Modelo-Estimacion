"""
Módulo de Lógica de Rangos y Cálculo de Límites (Entregable 3)
=============================================================
No Country - Estimación de Capacidad Varada en Data Centers de IA

Este módulo implementa el cálculo de rangos determinísticos (Floor & Ceiling)
y estocásticos (Monte Carlo P10/P50/P90) para evaluar el desaprovechamiento
de potencia eléctrica y pérdidas financieras asociadas.

Conceptos Clave:
- Floor (Límite Inferior): Costo incurrido real (OPEX energético de PUE + CAPEX amortizado).
- Mid (Valor Medio): Promedio de Floor y Ceiling.
- Ceiling (Límite Superior): Costo de oportunidad en mercado de Colocation ($184 USD/kW/mes).
- Monte Carlo (Estocástico): Distribución de percentiles de confianza (P10, P50, P90).
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Literal, Tuple
import numpy as np

CoolingType = Literal["air-cooled", "hybrid", "liquid-cooled"]

# ==========================================
# BENCHMARKS DE REFERENCIA Y CONSTANTES
# ==========================================

RANGE_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "air-cooled": {
        "name": "Aire Tradicional (Hot/Cold Aisle)",
        "pue": 1.58,
        "stranded_pct": {"min": 12.0, "mid": 12.5, "max": 13.0},
        "capex_per_mw": 11_000_000.0,
        "source": "Microsoft GFS (2010) & Uptime Institute (2024)",
    },
    "hybrid": {
        "name": "Híbrido (Aire + Líquido)",
        "pue": 1.25,
        "stranded_pct": {"min": 8.0, "mid": 9.0, "max": 10.0},
        "capex_per_mw": 13_500_000.0,
        "source": "EIA (2026) & Industry Hybrid Benchmarks",
    },
    "liquid-cooled": {
        "name": "Líquido Direct-to-Chip / Inmersión",
        "pue": 1.08,
        "stranded_pct": {"min": 2.0, "mid": 3.5, "max": 5.0},
        "capex_per_mw": 17_500_000.0,
        "source": "Supermicro AI Benchmark (2025)",
    },
}

# Parámetros por defecto
ELECTRICITY_RATE_USD_KWH: float = 0.12     # Tarifa energía promedio ($/kWh)
COLOCATION_RATE_USD_KW_MONTH: float = 184.0 # Tarifa Colocation techo ($/kW/mes)
HARDWARE_LIFECYCLE_YEARS: float = 4.5       # Período amortización CAPEX (años)
HOURS_PER_YEAR: float = 8760.0              # Horas en un año


@dataclass
class PhysicalRangeResult:
    """Resultado del cálculo de capacidad varada física en MW y %."""
    pct_min: float
    pct_mid: float
    pct_max: float
    mw_min: float
    mw_mid: float
    mw_max: float
    kw_mid: float


@dataclass
class FinancialRangeResult:
    """Resultado del cálculo de límites financieros (Floor, Mid, Ceiling)."""
    floor_usd_annual: float   # Costo Incurrido Real (OPEX + CAPEX)
    mid_usd_annual: float     # Promedio entre Floor y Ceiling
    ceiling_usd_annual: float # Costo de Oportunidad Colocation
    opex_energy_usd: float    # Componente OPEX del Floor
    amortized_capex_usd: float# Componente CAPEX del Floor
    cost_per_lost_mw_usd: float # KPI: Costo Anual por MW Perdido


@dataclass
class StochasticRangeResult:
    """Percentiles estocásticos derivados de Simulación Monte Carlo."""
    p10_usd_annual: float
    p50_usd_annual: float
    p90_usd_annual: float
    mean_usd_annual: float
    std_usd_annual: float


class RangeLogicEvaluator:
    """
    Evaluador especializado de la Lógica de Rangos para estimación de Stranded Capacity.
    """

    def __init__(
        self,
        electricity_rate: float = ELECTRICITY_RATE_USD_KWH,
        colocation_rate: float = COLOCATION_RATE_USD_KW_MONTH,
        lifecycle_years: float = HARDWARE_LIFECYCLE_YEARS,
    ):
        self.electricity_rate = electricity_rate
        self.colocation_rate = colocation_rate
        self.lifecycle_years = lifecycle_years

    def calculate_physical_range(
        self, facility_mw: float, utilization_pct: float, cooling_type: CoolingType
    ) -> PhysicalRangeResult:
        """
        Calcula los límites físicos de potencia varada (MW y %).
        """
        bench = RANGE_BENCHMARKS.get(cooling_type)
        if not bench:
            raise ValueError(f"Tipo de cooling desconocido: {cooling_type}")

        pct_min = bench["stranded_pct"]["min"]
        pct_mid = bench["stranded_pct"]["mid"]
        pct_max = bench["stranded_pct"]["max"]

        # Penalización por baja utilización (<50%)
        if utilization_pct < 50.0:
            penalty = (50.0 - utilization_pct) * 0.2
            pct_mid = min(pct_max, pct_mid + penalty)

        mw_min = facility_mw * (pct_min / 100.0)
        mw_mid = facility_mw * (pct_mid / 100.0)
        mw_max = facility_mw * (pct_max / 100.0)
        kw_mid = mw_mid * 1000.0

        return PhysicalRangeResult(
            pct_min=round(pct_min, 2),
            pct_mid=round(pct_mid, 2),
            pct_max=round(pct_max, 2),
            mw_min=round(mw_min, 2),
            mw_mid=round(mw_mid, 2),
            mw_max=round(mw_max, 2),
            kw_mid=round(kw_mid, 2),
        )

    def calculate_financial_range(
        self, facility_mw: float, physical_res: PhysicalRangeResult, cooling_type: CoolingType
    ) -> FinancialRangeResult:
        """
        Calcula los límites financieros determinísticos Floor y Ceiling.
        """
        bench = RANGE_BENCHMARKS[cooling_type]
        pue = bench["pue"]
        capex_mw = bench["capex_per_mw"]
        kw_mid = physical_res.kw_mid

        # 1. FLOOR (Costo Incurrido Real)
        opex_energy = kw_mid * HOURS_PER_YEAR * pue * self.electricity_rate
        amortized_capex = ((capex_mw / 1000.0) * kw_mid) / self.lifecycle_years
        floor_val = opex_energy + amortized_capex

        # 2. CEILING (Costo Oportunidad Colocation)
        ceiling_val = kw_mid * self.colocation_rate * 12.0

        # 3. MID (Punto Medio)
        mid_val = (floor_val + ceiling_val) / 2.0

        # KPI: Costo Anual por MW perdido
        cost_per_mw = mid_val / physical_res.mw_mid if physical_res.mw_mid > 0 else 0.0

        return FinancialRangeResult(
            floor_usd_annual=round(floor_val, 2),
            mid_usd_annual=round(mid_val, 2),
            ceiling_usd_annual=round(ceiling_val, 2),
            opex_energy_usd=round(opex_energy, 2),
            amortized_capex_usd=round(amortized_capex, 2),
            cost_per_lost_mw_usd=round(cost_per_mw, 2),
        )

    def calculate_stochastic_range(
        self,
        facility_mw: float,
        cooling_type: CoolingType,
        num_simulations: int = 5000,
        seed: int = 42,
    ) -> StochasticRangeResult:
        """
        Ejecuta simulación de Monte Carlo para derivar percentiles P10, P50 y P90.
        """
        np.random.seed(seed)
        bench = RANGE_BENCHMARKS[cooling_type]
        
        # Muestreo estocástico
        pue_sim = np.random.normal(bench["pue"], 0.04, num_simulations)
        pue_sim = np.clip(pue_sim, 1.02, 2.00)

        min_pct, max_pct = bench["stranded_pct"]["min"], bench["stranded_pct"]["max"]
        stranded_pct_sim = np.random.uniform(min_pct, max_pct, num_simulations)
        
        kw_sim = facility_mw * (stranded_pct_sim / 100.0) * 1000.0

        elec_sim = np.clip(np.random.normal(self.electricity_rate, 0.02, num_simulations), 0.06, 0.25)
        colo_sim = np.clip(np.random.normal(self.colocation_rate, 15.0, num_simulations), 120.0, 250.0)

        floor_sim = (kw_sim * HOURS_PER_YEAR * pue_sim * elec_sim) + (((bench["capex_per_mw"] / 1000.0) * kw_sim) / self.lifecycle_years)
        ceiling_sim = kw_sim * colo_sim * 12.0
        mid_sim = (floor_sim + ceiling_sim) / 2.0

        return StochasticRangeResult(
            p10_usd_annual=round(float(np.percentile(mid_sim, 10)), 2),
            p50_usd_annual=round(float(np.percentile(mid_sim, 50)), 2),
            p90_usd_annual=round(float(np.percentile(mid_sim, 90)), 2),
            mean_usd_annual=round(float(np.mean(mid_sim)), 2),
            std_usd_annual=round(float(np.std(mid_sim)), 2),
        )

    def generate_range_summary(
        self, facility_mw: float, utilization_pct: float, cooling_type: CoolingType
    ) -> Dict[str, Any]:
        """
        Genera un reporte resumido completo combinando límites físicos, determinísticos y estocásticos.
        """
        phys = self.calculate_physical_range(facility_mw, utilization_pct, cooling_type)
        fin = self.calculate_financial_range(facility_mw, phys, cooling_type)
        stoch = self.calculate_stochastic_range(facility_mw, cooling_type)

        bench = RANGE_BENCHMARKS[cooling_type]

        return {
            "facility_mw": facility_mw,
            "utilization_pct": utilization_pct,
            "cooling_type": cooling_type,
            "cooling_name": bench["name"],
            "pue_ref": bench["pue"],
            "physical_range": {
                "stranded_pct": {"min": phys.pct_min, "mid": phys.pct_mid, "max": phys.pct_max},
                "stranded_mw": {"min": phys.mw_min, "mid": phys.mw_mid, "max": phys.mw_max},
            },
            "financial_range_usd": {
                "floor_incurred": fin.floor_usd_annual,
                "mid_expected": fin.mid_usd_annual,
                "ceiling_opportunity": fin.ceiling_usd_annual,
                "opex_energy_component": fin.opex_energy_usd,
                "amortized_capex_component": fin.amortized_capex_usd,
                "cost_per_mw_lost": fin.cost_per_lost_mw_usd,
            },
            "stochastic_percentiles_usd": {
                "p10_optimistic": stoch.p10_usd_annual,
                "p50_median": stoch.p50_usd_annual,
                "p90_conservative": stoch.p90_usd_annual,
            },
        }


def print_cli_report(facility_mw: float = 15.0, utilization_pct: float = 80.0, cooling_type: CoolingType = "air-cooled"):
    """Imprime un reporte en consola de la lógica de rangos."""
    evaluator = RangeLogicEvaluator()
    summary = evaluator.generate_range_summary(facility_mw, utilization_pct, cooling_type)

    print("=" * 70)
    print("      REPORTE DE LÓGICA DE RANGOS: STRANDED CAPACITY (ENTREGABLE 3)")
    print("=" * 70)
    print(f"Facility: {summary['facility_mw']} MW  |  Utilización: {summary['utilization_pct']}%")
    print(f"Tecnología: {summary['cooling_name']} (PUE: {summary['pue_ref']})")
    print("-" * 70)
    print("1. RANGO FÍSICO DE CAPACIDAD VARADA:")
    print(f"   - Porcentaje: {summary['physical_range']['stranded_pct']['min']}% -> {summary['physical_range']['stranded_pct']['mid']}% -> {summary['physical_range']['stranded_pct']['max']}%")
    print(f"   - Megavatios: {summary['physical_range']['stranded_mw']['min']} MW -> {summary['physical_range']['stranded_mw']['mid']} MW -> {summary['physical_range']['stranded_mw']['max']} MW")
    print("-" * 70)
    print("2. LÍMITES FINANCIEROS ANUALES (DETERMINÍSTICOS):")
    print(f"   - FLOOR (Costo Incurrido Real):    ${summary['financial_range_usd']['floor_incurred']:>15,.2f} USD")
    print(f"     * OPEX Energía:                 ${summary['financial_range_usd']['opex_energy_component']:>15,.2f} USD")
    print(f"     * Amortización CAPEX:           ${summary['financial_range_usd']['amortized_capex_component']:>15,.2f} USD")
    print(f"   - MID (Punto Medio Esperado):      ${summary['financial_range_usd']['mid_expected']:>15,.2f} USD")
    print(f"   - CEILING (Costo Oportunidad):     ${summary['financial_range_usd']['ceiling_opportunity']:>15,.2f} USD")
    print(f"   - KPI Costo por MW Perdido:        ${summary['financial_range_usd']['cost_per_mw_lost']:>15,.2f} USD/MW")
    print("-" * 70)
    print("3. RANGOS ESTOCÁSTICOS (MONTE CARLO 5,000 ITERACIONES):")
    print(f"   - P10 (Optimista / Suelo):         ${summary['stochastic_percentiles_usd']['p10_optimistic']:>15,.2f} USD")
    print(f"   - P50 (Mediana / Base):            ${summary['stochastic_percentiles_usd']['p50_median']:>15,.2f} USD")
    print(f"   - P90 (Pesimista / Techo):         ${summary['stochastic_percentiles_usd']['p90_conservative']:>15,.2f} USD")
    print("=" * 70)


if __name__ == "__main__":
    print_cli_report(facility_mw=15.0, utilization_pct=80.0, cooling_type="air-cooled")
    print("\n")
    print_cli_report(facility_mw=15.0, utilization_pct=80.0, cooling_type="liquid-cooled")
