"""
Monte Carlo Simulation Engine for Stranded Capacity Estimation
===============================================================
No Country Project - Épica 2 (Data Science & Modelado Estadístico)

Este módulo implementa la simulación de Monte Carlo para calcular distribuciones
de probabilidad y percentiles de confianza (P10, P50, P90) para las pérdidas financieras
y megavatios varados en data centers de IA.
"""

import numpy as np
from typing import Dict, Any, Optional

# Benchmark defaults alignment
COOLING_STATS = {
    "air-cooled": {
        "pue_mean": 1.58, "pue_std": 0.05, "pue_bounds": (1.30, 2.00),
        "stranded_pct_bounds": (12.0, 13.0),
        "capex_mean": 11_000_000.0, "capex_std": 500_000.0,
    },
    "liquid-cooled": {
        "pue_mean": 1.08, "pue_std": 0.02, "pue_bounds": (1.02, 1.20),
        "stranded_pct_bounds": (2.0, 5.0),
        "capex_mean": 17_500_000.0, "capex_std": 800_000.0,
    },
    "hybrid": {
        "pue_mean": 1.25, "pue_std": 0.03, "pue_bounds": (1.12, 1.45),
        "stranded_pct_bounds": (8.0, 10.0),
        "capex_mean": 13_500_000.0, "capex_std": 600_000.0,
    },
}


def run_monte_carlo_simulation(
    facility_mw: float,
    utilization_pct: float,
    cooling_type: str = "air-cooled",
    num_simulations: int = 10000,
    random_state: Optional[int] = 42,
) -> Dict[str, Any]:
    """
    Ejecuta N iteraciones de la simulación de Monte Carlo para estimar la distribución
    de pérdidas financieras y capacidad varada.

    Parameters:
    -----------
    facility_mw : float
        Capacidad nominal total del data center en Megavatios (MW).
    utilization_pct : float
        Utilización actual aproximada (0 - 100%).
    cooling_type : str
        Tipo de tecnología de enfriamiento ('air-cooled', 'liquid-cooled', 'hybrid').
    num_simulations : int
        Número de iteraciones estocásticas a ejecutar (por defecto 10,000).
    random_state : Optional[int]
        Semilla aleatoria para reproducibilidad.

    Returns:
    --------
    Dict[str, Any]
        Diccionario con percentiles P10, P50, P90, estadísticas resumidas
        y vectores de resultados.
    """
    if cooling_type not in COOLING_STATS:
        raise ValueError(f"Tipo de cooling no válido: {cooling_type}. Opciones: {list(COOLING_STATS.keys())}")

    if random_state is not None:
        np.random.seed(random_state)

    stats = COOLING_STATS[cooling_type]

    # 1. Muestreo estocástico de PUE (Distribución normal truncada)
    pue_sim = np.random.normal(stats["pue_mean"], stats["pue_std"], num_simulations)
    pue_sim = np.clip(pue_sim, stats["pue_bounds"][0], stats["pue_bounds"][1])

    # 2. Muestreo de % de Capacidad Varada (Uniforme + Penalización por bajo uso)
    min_pct, max_pct = stats["stranded_pct_bounds"]
    stranded_pct_sim = np.random.uniform(min_pct, max_pct, num_simulations)

    if utilization_pct < 50.0:
        penalty = (50.0 - utilization_pct) * 0.2
        stranded_pct_sim = np.clip(stranded_pct_sim + penalty, min_pct, max_pct + penalty)

    # 3. Muestreo de Tarifa Eléctrica USD/kWh (Normal truncada)
    elec_rate_sim = np.random.normal(0.12, 0.02, num_simulations)
    elec_rate_sim = np.clip(elec_rate_sim, 0.06, 0.25)

    # 4. Muestreo de Tarifa Colocation USD/kW/mes (Normal truncada)
    colo_rate_sim = np.random.normal(184.0, 15.0, num_simulations)
    colo_rate_sim = np.clip(colo_rate_sim, 120.0, 250.0)

    # 5. Muestreo de CAPEX por MW (Normal)
    capex_mw_sim = np.random.normal(stats["capex_mean"], stats["capex_std"], num_simulations)

    # 6. Cálculos estocásticos por iteración
    stranded_mw_sim = facility_mw * (stranded_pct_sim / 100.0)
    stranded_kw_sim = stranded_mw_sim * 1000.0

    # Límite Inferior (Floor - Incurred Inefficiency Cost)
    opex_energy_sim = stranded_kw_sim * 8760.0 * pue_sim * elec_rate_sim
    amortized_capex_sim = ((capex_mw_sim / 1000.0) * stranded_kw_sim) / 4.5
    loss_floor_sim = opex_energy_sim + amortized_capex_sim

    # Límite Superior (Ceiling - Colocation Opportunity Cost)
    loss_ceiling_sim = stranded_kw_sim * colo_rate_sim * 12.0

    # Pérdida Media Estimada
    loss_mid_sim = (loss_floor_sim + loss_ceiling_sim) / 2.0

    # Valor Recuperable (80%)
    recoverable_sim = loss_mid_sim * 0.80

    # ROI en meses (Remediación a $75k/MW)
    remediation_total = facility_mw * 75_000.0
    roi_months_sim = (remediation_total / np.maximum(recoverable_sim, 1.0)) * 12.0

    # 7. Extracción de percentiles P10, P50, P90
    results = {
        "facility_mw": facility_mw,
        "utilization_pct": utilization_pct,
        "cooling_type": cooling_type,
        "num_simulations": num_simulations,
        "percentiles": {
            "loss_mid_usd": {
                "p10": float(np.percentile(loss_mid_sim, 10)),
                "p50": float(np.percentile(loss_mid_sim, 50)),
                "p90": float(np.percentile(loss_mid_sim, 90)),
                "mean": float(np.mean(loss_mid_sim)),
                "std": float(np.std(loss_mid_sim)),
            },
            "loss_floor_usd": {
                "p10": float(np.percentile(loss_floor_sim, 10)),
                "p50": float(np.percentile(loss_floor_sim, 50)),
                "p90": float(np.percentile(loss_floor_sim, 90)),
            },
            "loss_ceiling_usd": {
                "p10": float(np.percentile(loss_ceiling_sim, 10)),
                "p50": float(np.percentile(loss_ceiling_sim, 50)),
                "p90": float(np.percentile(loss_ceiling_sim, 90)),
            },
            "stranded_mw": {
                "p10": float(np.percentile(stranded_mw_sim, 10)),
                "p50": float(np.percentile(stranded_mw_sim, 50)),
                "p90": float(np.percentile(stranded_mw_sim, 90)),
            },
            "roi_months": {
                "p10": float(np.percentile(roi_months_sim, 10)),
                "p50": float(np.percentile(roi_months_sim, 50)),
                "p90": float(np.percentile(roi_months_sim, 90)),
            },
        },
        "raw_simulations": {
            "loss_mid_usd": loss_mid_sim,
            "loss_floor_usd": loss_floor_sim,
            "loss_ceiling_usd": loss_ceiling_sim,
            "stranded_mw": stranded_mw_sim,
            "pue": pue_sim,
            "elec_rate": elec_rate_sim,
        },
    }

    return results


if __name__ == "__main__":
    print("--- Probando Simulación de Monte Carlo (10,000 iteraciones) ---")
    sim = run_monte_carlo_simulation(facility_mw=20.0, utilization_pct=75.0, cooling_type="air-cooled")
    p = sim["percentiles"]["loss_mid_usd"]
    print(f"Facility: 20 MW | Cooling: Air-Cooled | Utilización: 75%")
    print(f"Pérdida Financiera Mid P10: ${p['p10']:,.2f} USD")
    print(f"Pérdida Financiera Mid P50: ${p['p50']:,.2f} USD")
    print(f"Pérdida Financiera Mid P90: ${p['p90']:,.2f} USD")
