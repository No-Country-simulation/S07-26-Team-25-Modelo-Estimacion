from dataclasses import dataclass
from typing import Dict, Any, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ==========================================
# 1. MODELOS DE DATOS
# ==========================================

CoolingType = Literal["air-cooled", "liquid-cooled", "hybrid"]

class CalculatorInput(BaseModel):
    facility_mw: float = Field(..., gt=0, description="Tamaño total de la instalación (MW)")
    utilization_pct: float = Field(..., ge=0, le=100, description="Utilización actual (0-100%)")
    cooling_type: CoolingType = Field(..., description="Arquitectura de enfriamiento")

class LossRange(BaseModel):
    min_usd_annual: float
    mid_usd_annual: float
    max_usd_annual: float

class KPIs(BaseModel):
    usd_per_lost_mw: float
    current_utilization_pct: float
    industry_benchmark_utilization_pct: float
    effective_capacity_mw: float
    paid_capacity_mw: float

class CalculatorOutput(BaseModel):
    facility_size_mw: float
    stranded_capacity_pct_range: Dict[str, float]
    stranded_capacity_mw_range: Dict[str, float]
    annual_financial_loss_usd: LossRange
    potential_recoverable_value_usd: float
    estimated_recovery_time_months: Dict[str, float]
    kpis: KPIs
    assumptions_summary: Dict[str, Any]

# ==========================================
# 2. NUEVA MATRIZ DE SUPUESTOS (Actualizada)
# ==========================================

COOLING_BENCHMARKS = {
    "air-cooled": {
        "pue_ref": 1.58,
        "stranded_pct_range": {"min": 12.0, "mid": 12.5, "max": 13.0},
        "ccf_typical": 3.9,
        "capex_per_mw": 11000000.0,  # Promedio de $10M - $12M
    },
    "liquid-cooled": {
        "pue_ref": 1.08, 
        "stranded_pct_range": {"min": 2.0, "mid": 3.5, "max": 5.0}, # < 5%
        "ccf_typical": 1.2,
        "capex_per_mw": 17500000.0,  # Promedio de $15M - $20M
    },
    "hybrid": {
        "pue_ref": 1.25,
        "stranded_pct_range": {"min": 8.0, "mid": 9.0, "max": 10.0},
        "ccf_typical": 1.8,
        "capex_per_mw": 13500000.0,  # Promedio de $12M - $15M
    },
}

# Parámetros Financieros (Nuevo Modelo)
COLOCATION_RATE_PER_KW_MONTH = 184.0  # Límite Superior (Techo)
ELECTRICITY_RATE_PER_KWH = 0.12       # Asumido como promedio ($/kWh)
LIFECYCLE_YEARS = 4.5                 # Promedio del ciclo de vida (3 a 6 años)
HOURS_PER_YEAR = 8760
BENCHMARK_UTILIZATION_PCT = 85.0      
REMEDIATION_COST_PER_MW = 75000.0     

# ==========================================
# 3. LÓGICA CORE DE ESTIMACIÓN
# ==========================================

def calculate_stranded_capacity(input_data: CalculatorInput) -> CalculatorOutput:
    cooling_info = COOLING_BENCHMARKS.get(input_data.cooling_type)
    if not cooling_info:
        raise ValueError(f"Tipo de cooling no válido: {input_data.cooling_type}")

    # A. Porcentajes de Stranded Capacity
    pct_min = cooling_info["stranded_pct_range"]["min"]
    pct_mid = cooling_info["stranded_pct_range"]["mid"]
    pct_max = cooling_info["stranded_pct_range"]["max"]

    if input_data.utilization_pct < 50.0:
        gap_penalty = (50.0 - input_data.utilization_pct) * 0.2
        pct_mid = min(pct_max, pct_mid + gap_penalty)

    # B. Megavatios Varados
    mw_min = input_data.facility_mw * (pct_min / 100.0)
    mw_mid = input_data.facility_mw * (pct_mid / 100.0)
    mw_max = input_data.facility_mw * (pct_max / 100.0)

    # C. Pérdida Financiera Anual ($ USD) - NUEVA METODOLOGÍA
    stranded_kw_mid = mw_mid * 1000.0
    
    # Límite Inferior (Floor Formula): OPEX de energía + CAPEX amortizado
    opex_energy = stranded_kw_mid * HOURS_PER_YEAR * cooling_info["pue_ref"] * ELECTRICITY_RATE_PER_KWH
    amortized_capex = (cooling_info["capex_per_mw"] / 1000.0 * stranded_kw_mid) / LIFECYCLE_YEARS
    loss_min = opex_energy + amortized_capex

    # Límite Superior: Costo de Oportunidad (Colocation)
    loss_max = stranded_kw_mid * COLOCATION_RATE_PER_KW_MONTH * 12.0
    
    # Media Financiera
    loss_mid = (loss_min + loss_max) / 2.0

    # D. Valor Recuperable (80% del valor varado medio)
    recoverable_value = loss_mid * 0.80

    # E. Tiempo de Recuperación (ROI)
    total_remediation_cost = input_data.facility_mw * REMEDIATION_COST_PER_MW
    recovery_months_mid = (total_remediation_cost / recoverable_value) * 12.0 if recoverable_value > 0 else 0

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
            "cooling_type": input_data.cooling_type,
            "pue_reference": cooling_info["pue_ref"],
            "ccf_typical": cooling_info["ccf_typical"],
            "financial_floor_formula": "OPEX Energy + Amortized CAPEX",
            "colocation_rate_used": f"${COLOCATION_RATE_PER_KW_MONTH}/kW/mo",
        },
    )

# ==========================================
# 4. API (FastAPI)
# ==========================================

app = FastAPI(title="Stranded Capacity API", version="2.0.0")

@app.post("/api/v1/calculate", response_model=CalculatorOutput)
def calculate_endpoint(payload: CalculatorInput):
    try:
        return calculate_stranded_capacity(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))