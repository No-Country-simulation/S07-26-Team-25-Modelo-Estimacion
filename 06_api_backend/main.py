"""
FastAPI Backend - Stranded Capacity Estimation API
===================================================
No Country Project - Entregable 6: API REST & Backend Services

Esta API expone el motor matemático determinístico (Floor & Ceiling) y
el motor de simulación de Monte Carlo para la estimación de Stranded Capacity
en Data Centers de Inteligencia Artificial.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Asegurar importación de módulos del proyecto
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "01_modelo_documentado"))
sys.path.append(str(ROOT_DIR / "02_dataset_referencia"))

from stranded_model import (
    StrandedCapacityCalculator,
    CalculatorInput,
    CalculatorOutput,
    COOLING_BENCHMARKS,
)
from monte_carlo_simulation import run_monte_carlo_simulation


# Función auxiliar para convertir tipos de datos de NumPy a tipos nativos de Python para JSON
def sanitize_numpy(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: sanitize_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_numpy(v) for v in obj]
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Stranded Capacity Estimation API",
    description=(
        "API REST para cuantificar la Capacidad Varada (Stranded Capacity) "
        "y el impacto financiero en Data Centers de IA (No Country - Team 25)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar middleware CORS para comunicación con Streamlit o clientes externos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del motor
calculator = StrandedCapacityCalculator()


class MonteCarloInput(BaseModel):
    facility_mw: float = Field(..., gt=0, description="Tamaño total de la instalación en MW")
    utilization_pct: float = Field(..., ge=0, le=100, description="Utilización actual (0 - 100%)")
    cooling_type: str = Field("air-cooled", description="Tipo de cooling: 'air-cooled', 'liquid-cooled', 'hybrid'")
    num_simulations: int = Field(5000, ge=100, le=50000, description="Número de simulaciones (100 a 50,000)")


@app.get("/", tags=["Health Check & Metadata"])
def read_root():
    """Retorna información general y estado del servicio API."""
    return {
        "status": "online",
        "service": "Stranded Capacity Estimation API",
        "version": "1.0.0",
        "team": "No Country - Team 25",
        "docs": "/docs",
        "endpoints": [
            "GET /api/v1/benchmarks",
            "POST /api/v1/calculate",
            "POST /api/v1/monte-carlo"
        ]
    }


@app.get("/api/v1/benchmarks", tags=["Benchmarks"])
def get_benchmarks():
    """Retorna la matriz de benchmarks de enfriamiento y constantes de la industria."""
    return {
        "cooling_benchmarks": COOLING_BENCHMARKS,
        "colocation_rate_usd_kw_month": 184.0,
        "electricity_rate_usd_kwh": 0.12,
        "industry_utilization_target_pct": 85.0
    }


@app.post(
    "/api/v1/calculate",
    response_model=CalculatorOutput,
    status_code=status.HTTP_200_OK,
    tags=["Estimación Determinística"]
)
def calculate_stranded_capacity(input_data: CalculatorInput):
    """
    Calcula el Stranded Capacity y el impacto financiero determinístico
    basado en la metodología de rangos (Floor & Ceiling).
    """
    try:
        result = calculator.calculate(
            facility_mw=input_data.facility_mw,
            utilization_pct=input_data.utilization_pct,
            cooling_type=input_data.cooling_type
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el cálculo: {str(e)}"
        )


@app.post("/api/v1/monte-carlo", tags=["Simulación Estocástica"])
def simulate_monte_carlo(input_data: MonteCarloInput):
    """
    Ejecuta una simulación estocástica de Monte Carlo para obtener distribuciones
    de probabilidad (Percentiles P10, P50, P90).
    """
    try:
        sim_results = run_monte_carlo_simulation(
            facility_mw=input_data.facility_mw,
            utilization_pct=input_data.utilization_pct,
            cooling_type=input_data.cooling_type.lower(),
            num_simulations=input_data.num_simulations
        )
        return sanitize_numpy(sim_results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al ejecutar la simulación de Monte Carlo: {str(e)}"
        )
