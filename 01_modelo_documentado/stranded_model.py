"""
Stranded Capacity Estimation Model for AI Data Centers
======================================================
No Country Project - Estimación de Capacidad Varada

Este módulo implementa el motor de estimación determinístico basado en la metodología
de rangos "Floor & Ceiling" para calcular el desperdicio estructural de potencia (Stranded Capacity)
y su correspondiente impacto financiero en data centers de alta densidad de IA.

Fuentes y Supuestos Citados:
---------------------------
1. Microsoft GFS (Sankar & Vaid, 2010): Trace-Driven Analysis of Data Center Power.
   - Demuestra que el aprovisionamiento 'Max-Power' genera hasta un 13% de capacidad varada por sobre-provisión.
2. Supermicro (2025): High-Density AI Data Center & Cooling Benchmark Report.
   - Benchmark de PUE: Aire = 1.58, Híbrido = 1.25, Líquido (Direct-to-Chip) = 1.08.
   - Demuestra hasta un 16% de ahorro en consumo de nodo al eliminar ventiladores de IT en cooling líquido.
3. Uptime Institute (2024): Global Data Center Survey.
   - PUE global de referencia para instalaciones por aire = 1.58.
4. U.S. Energy Information Administration (EIA, 2026): Commercial Electricity Rates.
   - Tarifa eléctrica de referencia comercial promedio = $0.12 USD/kWh.
5. Nlyte Software / Colocation Market Benchmarks (2025/2026):
   - Tarifa de oportunidad de mercado para Colocation = $184.00 USD/kW/mes ($2,208 USD/kW/año).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Literal, Optional
from pydantic import BaseModel, Field

CoolingType = Literal["air-cooled", "liquid-cooled", "hybrid"]

# ==========================================
# 1. MATRIZ DE BENCHMARKS Y CONSTANTES
# ==========================================

COOLING_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "air-cooled": {
        "name": "Aire Tradicional (Hot/Cold Aisle)",
        "pue_ref": 1.58,
        "stranded_pct_range": {"min": 12.0, "mid": 12.5, "max": 13.0},
        "ccf_typical": 3.9,
        "capex_per_mw": 11_000_000.0,  # $11M USD por MW
        "source": "Microsoft GFS (2010) & Uptime Institute (2024)"
    },
    "liquid-cooled": {
        "name": "Líquido Direct-to-Chip / Inmersión",
        "pue_ref": 1.08,
        "stranded_pct_range": {"min": 2.0, "mid": 3.5, "max": 5.0},
        "ccf_typical": 1.2,
        "capex_per_mw": 17_500_000.0,  # $17.5M USD por MW
        "source": "Supermicro (2025) Liquid Cooling Benchmark"
    },
    "hybrid": {
        "name": "Híbrido (Aire + Líquido)",
        "pue_ref": 1.25,
        "stranded_pct_range": {"min": 8.0, "mid": 9.0, "max": 10.0},
        "ccf_typical": 1.8,
        "capex_per_mw": 13_500_000.0,  # $13.5M USD por MW
        "source": "EIA (2026) & Industry Hybrid Benchmarks"
    },
}

# Parámetros Financieros y Operativos Globales
COLOCATION_RATE_PER_KW_MONTH: float = 184.0  # Techo: Costo de oportunidad en Colocation ($/kW/mes)
ELECTRICITY_RATE_PER_KWH: float = 0.12       # Tarifa promedio de energía ($/kWh)
LIFECYCLE_YEARS: float = 4.5                 # Periodo de amortización de infraestructura (años)
HOURS_PER_YEAR: int = 8760                   # Horas en un año no bisiesto
BENCHMARK_UTILIZATION_PCT: float = 85.0      # Meta óptima de utilización en la industria (%)
REMEDIATION_COST_PER_MW: float = 75_000.0    # Costo de implementación de DCIM y telemetría ($/MW)
RECOVERABLE_FACTOR: float = 0.80             # 80% de la capacidad varada es recuperable


# ==========================================
# 2. MODELOS DE DATOS (PYDANTIC)
# ==========================================

class CalculatorInput(BaseModel):
    """Modelo de entrada para la calculadora de Stranded Capacity."""
    facility_mw: float = Field(..., gt=0, description="Tamaño total de la instalación en Megavatios (MW)")
    utilization_pct: float = Field(..., ge=0, le=100, description="Utilización actual aproximada (0 - 100%)")
    cooling_type: CoolingType = Field(..., description="Tipo de tecnología de enfriamiento")


class LossRange(BaseModel):
    """Rango de pérdida financiera anual estimada en dólares USD."""
    min_usd_annual: float = Field(..., description="Límite Inferior (Piso): OPEX de energía + CAPEX amortizado")
    mid_usd_annual: float = Field(..., description="Estimación Media (Promedio de Floor & Ceiling)")
    max_usd_annual: float = Field(..., description="Límite Superior (Techo): Costo de Oportunidad Colocation")


class KPIs(BaseModel):
    """Indicadores Clave de Desempeño (KPIs) calculados."""
    usd_per_lost_mw: float = Field(..., description="Costo financiero anual por MW perdido ($/MW)")
    current_utilization_pct: float = Field(..., description="Utilización declarada del facility (%)")
    industry_benchmark_utilization_pct: float = Field(..., description="Benchmark objetivo de la industria (85%)")
    effective_capacity_mw: float = Field(..., description="Capacidad MW realmente aprovechada en producción")
    paid_capacity_mw: float = Field(..., description="Capacidad total contratada y pagada (MW)")


class CalculatorOutput(BaseModel):
    """Modelo de respuesta completo devuelto por el modelo."""
    facility_size_mw: float
    cooling_type: str
    stranded_capacity_pct_range: Dict[str, float]
    stranded_capacity_mw_range: Dict[str, float]
    annual_financial_loss_usd: LossRange
    potential_recoverable_value_usd: float
    estimated_recovery_time_months: Dict[str, float]
    kpis: KPIs
    assumptions_summary: Dict[str, Any]


# ==========================================
# 3. MOTOR MATEMÁTICO (CLASE PRINCIPAL)
# ==========================================

class StrandedCapacityCalculator:
    """
    Calculadora determinística de Stranded Capacity y Pérdidas Financieras.
    
    Implementa el modelo de rangos con límites explícitos:
    - Floor: Refleja el costo incurrido real (Energía ociosa consumida a través del PUE + Amortización de CAPEX).
    - Ceiling: Refleja la pérdida de ingresos equivalente por no alquilar esa potencia a precio de Colocation.
    """

    def __init__(
        self,
        electricity_rate: float = ELECTRICITY_RATE_PER_KWH,
        colocation_rate: float = COLOCATION_RATE_PER_KW_MONTH,
        lifecycle_years: float = LIFECYCLE_YEARS,
    ):
        self.electricity_rate = electricity_rate
        self.colocation_rate = colocation_rate
        self.lifecycle_years = lifecycle_years

    def calculate(
        self,
        facility_mw: Any,
        utilization_pct: Optional[float] = None,
        cooling_type: Optional[CoolingType] = None,
    ) -> CalculatorOutput:
        """
        Ejecuta la estimación de Stranded Capacity recibiendo parámetros primitivos o un objeto CalculatorInput.
        """
        if isinstance(facility_mw, CalculatorInput):
            return self.calculate_from_object(facility_mw)
            
        if utilization_pct is None or cooling_type is None:
            raise ValueError("Se requieren utilization_pct y cooling_type cuando facility_mw es numérico.")

        input_obj = CalculatorInput(
            facility_mw=facility_mw,
            utilization_pct=utilization_pct,
            cooling_type=cooling_type,
        )
        return self.calculate_from_object(input_obj)

    def calculate_from_object(self, input_data: CalculatorInput) -> CalculatorOutput:
        """
        Ejecuta la estimación a partir de un objeto validado CalculatorInput.
        """
        cooling_info = COOLING_BENCHMARKS.get(input_data.cooling_type)
        if not cooling_info:
            raise ValueError(f"Tipo de cooling no soportado: {input_data.cooling_type}")

        # A. Porcentaje de Stranded Capacity (Rangos)
        pct_min = cooling_info["stranded_pct_range"]["min"]
        pct_mid = cooling_info["stranded_pct_range"]["mid"]
        pct_max = cooling_info["stranded_pct_range"]["max"]

        # Penalización por baja utilización (<50%)
        # Si el facility opera muy por debajo de su capacidad, aumenta la ineficiencia estructural
        if input_data.utilization_pct < 50.0:
            gap_penalty = (50.0 - input_data.utilization_pct) * 0.2
            pct_mid = min(pct_max, pct_mid + gap_penalty)

        # B. Megavatios (MW) Varados
        mw_min = input_data.facility_mw * (pct_min / 100.0)
        mw_mid = input_data.facility_mw * (pct_mid / 100.0)
        mw_max = input_data.facility_mw * (pct_max / 100.0)

        stranded_kw_mid = mw_mid * 1000.0

        # C. Pérdida Financiera Anual ($ USD) - Metodología Floor & Ceiling
        # Límite Inferior (Floor): OPEX Eléctrico de Potencia Varada + CAPEX Amortizado
        opex_energy = (
            stranded_kw_mid
            * HOURS_PER_YEAR
            * cooling_info["pue_ref"]
            * self.electricity_rate
        )
        amortized_capex = (
            (cooling_info["capex_per_mw"] / 1000.0 * stranded_kw_mid)
            / self.lifecycle_years
        )
        loss_min = opex_energy + amortized_capex

        # Límite Superior (Ceiling): Costo de Oportunidad Colocation
        loss_max = stranded_kw_mid * self.colocation_rate * 12.0

        # Estimación Media (Mid)
        loss_mid = (loss_min + loss_max) / 2.0

        # D. Valor Recuperable Potencial (80% del valor medio varado)
        recoverable_value = loss_mid * RECOVERABLE_FACTOR

        # E. Tiempo de Recuperación de Inversión (ROI en meses)
        total_remediation_cost = input_data.facility_mw * REMEDIATION_COST_PER_MW
        recovery_months_mid = (
            (total_remediation_cost / recoverable_value) * 12.0
            if recoverable_value > 0
            else 0.0
        )

        # F. KPIs
        effective_capacity_mw = input_data.facility_mw * (input_data.utilization_pct / 100.0)
        usd_per_lost_mw = loss_mid / mw_mid if mw_mid > 0 else 0.0

        kpis = KPIs(
            usd_per_lost_mw=round(usd_per_lost_mw, 2),
            current_utilization_pct=input_data.utilization_pct,
            industry_benchmark_utilization_pct=BENCHMARK_UTILIZATION_PCT,
            effective_capacity_mw=round(effective_capacity_mw, 2),
            paid_capacity_mw=input_data.facility_mw,
        )

        return CalculatorOutput(
            facility_size_mw=input_data.facility_mw,
            cooling_type=input_data.cooling_type,
            stranded_capacity_pct_range={
                "min": round(pct_min, 1),
                "mid": round(pct_mid, 1),
                "max": round(pct_max, 1),
            },
            stranded_capacity_mw_range={
                "min": round(mw_min, 2),
                "mid": round(mw_mid, 2),
                "max": round(mw_max, 2),
            },
            annual_financial_loss_usd=LossRange(
                min_usd_annual=round(loss_min, 2),
                mid_usd_annual=round(loss_mid, 2),
                max_usd_annual=round(loss_max, 2),
            ),
            potential_recoverable_value_usd=round(recoverable_value, 2),
            estimated_recovery_time_months={
                "min_months": round(recovery_months_mid * 0.6, 1),
                "mid_months": round(recovery_months_mid, 1),
                "max_months": round(recovery_months_mid * 1.5, 1),
            },
            kpis=kpis,
            assumptions_summary={
                "cooling_technology": cooling_info["name"],
                "pue_reference": cooling_info["pue_ref"],
                "ccf_typical": cooling_info["ccf_typical"],
                "electricity_rate_usd_kwh": self.electricity_rate,
                "colocation_rate_usd_kw_month": self.colocation_rate,
                "floor_formula": "OPEX Energy + Amortized CAPEX",
                "ceiling_formula": "Stranded kW * Colocation Rate * 12",
                "academic_sources": [
                    cooling_info["source"],
                    "Microsoft GFS (Sankar & Vaid 2010)",
                    "Uptime Institute 2024 Global Survey",
                ],
            },
        )


# ==========================================
# 4. DEMO Y VERIFICACIÓN
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("DEMO: STRANDED CAPACITY CALCULATOR")
    print("=" * 60)

    calculator = StrandedCapacityCalculator()
    facility_size = 15.0  # MW
    utilization = 87.0    # 87%

    for cooling in ["air-cooled", "hybrid", "liquid-cooled"]:
        res = calculator.calculate(facility_size, utilization, cooling)
        print(f"\n--- Tecnología: {cooling.upper()} ({res.assumptions_summary['cooling_technology']}) ---")
        print(f"Capacidad Instalada: {res.facility_size_mw} MW | Utilización: {utilization}%")
        print(f"PUE Referencia: {res.assumptions_summary['pue_reference']}")
        print(f"Stranded Capacity (%): {res.stranded_capacity_pct_range['mid']}% (Rango: {res.stranded_capacity_pct_range['min']}% - {res.stranded_capacity_pct_range['max']}%)")
        print(f"Stranded Capacity (MW): {res.stranded_capacity_mw_range['mid']} MW")
        print(f"Pérdida Financiera Anual USD (Mid): ${res.annual_financial_loss_usd.mid_usd_annual:,.2f}")
        print(f"  - Floor (Piso Incurre): ${res.annual_financial_loss_usd.min_usd_annual:,.2f}")
        print(f"  - Ceiling (Techo Colocation): ${res.annual_financial_loss_usd.max_usd_annual:,.2f}")
        print(f"Valor Recuperable Potencial: ${res.potential_recoverable_value_usd:,.2f}")
        print(f"Tiempo de Recuperación ROI: {res.estimated_recovery_time_months['mid_months']} meses")
        print(f"Costo por MW Perdido: ${res.kpis.usd_per_lost_mw:,.2f} USD/MW")
