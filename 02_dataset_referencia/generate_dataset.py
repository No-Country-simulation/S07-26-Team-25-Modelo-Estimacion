"""
Synthetic Dataset Generator for Data Center Stranded Capacity Benchmarking
==========================================================================
No Country Project - Épica 1 & Épica 2

Este script genera el dataset sintético reproducible de 5,000 centros de datos de IA
(dataset_5000_datacenters.csv) basándose en las distribuciones estadísticas curadas
de fuentes públicas (Uptime Institute, Supermicro, EIA, Microsoft GFS).
"""

import os
import numpy as np
import pandas as pd
from monte_carlo_simulation import COOLING_STATS


def generate_synthetic_dataset(num_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Genera un DataFrame sintético de 5,000 centros de datos con métricas operativas,
    financieras y percentiles de Monte Carlo.
    """
    np.random.seed(seed)

    # 1. IDs de las instalaciones
    facility_ids = [f"DC-{i+1:04d}" for i in range(num_samples)]

    # 2. Tamaño del facility en MW (Distribución Log-Normal)
    # Mediana ~ 16.4 MW, P90 ~ 45 MW, máximo recortado a 250 MW
    mw_raw = np.exp(np.random.normal(2.8, 0.8, num_samples))
    facility_mw = np.clip(np.round(mw_raw, 2), 1.0, 250.0)

    # 3. Tipo de Cooling (Distribución categórica basada en adopción de mercado)
    cooling_choices = ["air-cooled", "hybrid", "liquid-cooled"]
    cooling_probs = [0.55, 0.30, 0.15]
    cooling_type = np.random.choice(cooling_choices, size=num_samples, p=cooling_probs)

    # 4. Porcentaje de utilización actual (Normal truncada, media 72%, std 12%)
    util_raw = np.random.normal(72.0, 12.0, num_samples)
    utilization_pct = np.clip(np.round(util_raw, 1), 20.0, 98.0)

    # 5. Tarifa eléctrica regional en USD/kWh (Normal truncada, media $0.12, std $0.02)
    rate_raw = np.random.normal(0.12, 0.02, num_samples)
    elec_rate_usd_kwh = np.clip(np.round(rate_raw, 4), 0.06, 0.22)

    # 6. Tarifa de Colocation en USD/kW/mes (Normal truncada, media $184, std $15)
    colo_raw = np.random.normal(184.0, 15.0, num_samples)
    colocation_usd_kw_month = np.clip(np.round(colo_raw, 2), 120.0, 250.0)

    # Listas para almacenar métricas calculadas por registro
    pue_list = []
    capex_per_mw_list = []
    stranded_pct_list = []
    stranded_mw_list = []
    loss_floor_list = []
    loss_ceiling_list = []
    loss_mid_list = []
    p10_list = []
    p50_list = []
    p90_list = []
    recoverable_list = []
    roi_months_list = []

    # Generar métricas derivadas y percentiles estocásticos
    for i in range(num_samples):
        ctype = cooling_type[i]
        mw = facility_mw[i]
        u_pct = utilization_pct[i]
        c_rate = elec_rate_usd_kwh[i]
        colo_rate = colocation_usd_kw_month[i]

        c_stats = COOLING_STATS[ctype]

        # Muestreo individual de PUE
        pue = np.clip(np.random.normal(c_stats["pue_mean"], c_stats["pue_std"]), c_stats["pue_bounds"][0], c_stats["pue_bounds"][1])
        pue = round(float(pue), 3)
        pue_list.append(pue)

        # CAPEX por MW
        capex_mw = float(np.random.normal(c_stats["capex_mean"], c_stats["capex_std"]))
        capex_per_mw_list.append(round(capex_mw, 2))

        # % Capacidad Varada (con penalización por utilización < 50%)
        base_stranded_pct = np.random.uniform(c_stats["stranded_pct_bounds"][0], c_stats["stranded_pct_bounds"][1])
        if u_pct < 50.0:
            penalty = (50.0 - u_pct) * 0.2
            stranded_pct = min(c_stats["stranded_pct_bounds"][1] + penalty, base_stranded_pct + penalty)
        else:
            stranded_pct = base_stranded_pct
        stranded_pct = round(float(stranded_pct), 2)
        stranded_pct_list.append(stranded_pct)

        # MW varados
        stranded_mw = round(mw * (stranded_pct / 100.0), 3)
        stranded_mw_list.append(stranded_mw)
        stranded_kw = stranded_mw * 1000.0

        # Límite Inferior (Floor)
        opex_energy = stranded_kw * 8760.0 * pue * c_rate
        amortized_capex = ((capex_mw / 1000.0) * stranded_kw) / 4.5
        loss_floor = round(opex_energy + amortized_capex, 2)
        loss_floor_list.append(loss_floor)

        # Límite Superior (Ceiling)
        loss_ceiling = round(stranded_kw * colo_rate * 12.0, 2)
        loss_ceiling_list.append(loss_ceiling)

        # Pérdida Media (Mid)
        loss_mid = round((loss_floor + loss_ceiling) / 2.0, 2)
        loss_mid_list.append(loss_mid)

        # Simulación de Monte Carlo simplificada por fila (500 iteraciones) para percentiles P10, P50, P90
        sub_pue = np.clip(np.random.normal(c_stats["pue_mean"], c_stats["pue_std"], 500), c_stats["pue_bounds"][0], c_stats["pue_bounds"][1])
        sub_stranded_pct = np.random.uniform(c_stats["stranded_pct_bounds"][0], c_stats["stranded_pct_bounds"][1], 500)
        if u_pct < 50.0:
            sub_stranded_pct = sub_stranded_pct + (50.0 - u_pct) * 0.2
        sub_kw = mw * (sub_stranded_pct / 100.0) * 1000.0
        sub_rate = np.clip(np.random.normal(c_rate, 0.015, 500), 0.06, 0.25)
        sub_colo = np.clip(np.random.normal(colo_rate, 10.0, 500), 120.0, 250.0)
        sub_capex = np.random.normal(c_stats["capex_mean"], c_stats["capex_std"], 500)

        sub_floor = (sub_kw * 8760.0 * sub_pue * sub_rate) + (((sub_capex / 1000.0) * sub_kw) / 4.5)
        sub_ceiling = sub_kw * sub_colo * 12.0
        sub_mid = (sub_floor + sub_ceiling) / 2.0

        p10_list.append(round(float(np.percentile(sub_mid, 10)), 2))
        p50_list.append(round(float(np.percentile(sub_mid, 50)), 2))
        p90_list.append(round(float(np.percentile(sub_mid, 90)), 2))

        # Valor recuperable y ROI
        rec_val = round(loss_mid * 0.80, 2)
        recoverable_list.append(rec_val)

        remed_cost = mw * 75_000.0
        roi_m = round((remed_cost / max(rec_val, 1.0)) * 12.0, 1)
        roi_months_list.append(roi_m)

    df = pd.DataFrame({
        "facility_id": facility_ids,
        "facility_mw": facility_mw,
        "cooling_type": cooling_type,
        "utilization_pct": utilization_pct,
        "electricity_rate_usd_kwh": elec_rate_usd_kwh,
        "colocation_usd_kw_month": colocation_usd_kw_month,
        "pue_realized": pue_list,
        "capex_usd_per_mw": capex_per_mw_list,
        "stranded_capacity_pct": stranded_pct_list,
        "stranded_capacity_mw": stranded_mw_list,
        "loss_floor_usd_annual": loss_floor_list,
        "loss_ceiling_usd_annual": loss_ceiling_list,
        "loss_mid_usd_annual": loss_mid_list,
        "p10_loss_usd": p10_list,
        "p50_loss_usd": p50_list,
        "p90_loss_usd": p90_list,
        "recoverable_value_usd": recoverable_list,
        "roi_months": roi_months_list,
    })

    return df


if __name__ == "__main__":
    print("--- Generando dataset sintetico de 5,000 centros de datos ---")
    df = generate_synthetic_dataset(num_samples=5000, seed=42)
    output_path = os.path.join(os.path.dirname(__file__), "dataset_5000_datacenters.csv")
    df.to_csv(output_path, index=False)
    print(f"[OK] Dataset guardado exitosamente en: {output_path}")
    print(f"Dimensiones del dataset: {df.shape[0]} filas x {df.shape[1]} columnas")
    print("\nPrimeros 3 registros:")
    print(df.head(3).to_string())
