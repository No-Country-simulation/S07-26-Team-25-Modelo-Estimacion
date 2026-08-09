import json
from typing import Dict, Union

class StrandedCapacityAPI:
    """
    Motor de cálculo (Backend) para la calculadora de Stranded Capacity.
    Diseñado bajo principios de Clean Architecture para ser consumido por 
    cualquier frontend (Streamlit, React, Vue) o expuesto vía FastAPI/Flask.
    """
    def __init__(self):
        # Matriz de Supuestos (Single Source of Truth)
        self.cooling_matrix = {
            'Air Traditional': {'pue': 1.58, 'stranded_pct_range': (0.12, 0.13), 'tco_10yr_per_mw': (6500000, 11000000)},
            'Hibrido': {'pue': 1.25, 'stranded_pct_range': (0.08, 0.10), 'tco_10yr_per_mw': (11000000, 13000000)},
            'Liquid Direct-to-Chip': {'pue': 1.10, 'stranded_pct_range': (0.01, 0.05), 'tco_10yr_per_mw': (8000000, 14000000)}
        }
        # Techo de mercado Colocation: $184/kW/mes convertido a USD/MW/año
        self.colocation_ceiling_usd_mw_year = 184 * 1000 * 12 

    def calculate(self, capacity_mw: float, utilization_pct: float, cooling_type: str) -> Dict[str, Union[str, Dict]]:
        """
        Ejecuta el cálculo determinístico de Floor & Ceiling.
        Retorna un diccionario (JSON-friendly) estructurado.
        """
        # 1. Validaciones de Seguridad (Evitar crashes en el frontend)
        if cooling_type not in self.cooling_matrix:
            raise ValueError(f"Tipo de enfriamiento inválido. Opciones: {list(self.cooling_matrix.keys())}")
        if not (0 <= utilization_pct <= 100):
            raise ValueError("La tasa de utilización debe estar entre 0 y 100")

        # 2. Extracción de Parámetros
        utilization_rate = utilization_pct / 100.0
        params = self.cooling_matrix[cooling_type]
        pue = params['pue']
        factor_min, factor_max = params['stranded_pct_range']
        
        # 3. Lógica de Negocio: Cálculo Físico (MW)
        unutilized_capacity = capacity_mw * (1 - utilization_rate)
        stranded_mw_min = unutilized_capacity * factor_min * pue
        stranded_mw_max = unutilized_capacity * factor_max * pue
        
        # 4. Lógica de Negocio: Cálculo Financiero (Floor y Ceiling)
        tco_annual_min = params['tco_10yr_per_mw'][0] / 10
        tco_annual_max = params['tco_10yr_per_mw'][1] / 10
        
        loss_min = stranded_mw_min * tco_annual_min
        loss_max = stranded_mw_max * tco_annual_max
        
        colocation_cost = capacity_mw * self.colocation_ceiling_usd_mw_year
        internal_cost_est = (capacity_mw * tco_annual_max)
        margin_vs_colo = ((colocation_cost - internal_cost_est) / colocation_cost) * 100
        
        # 5. Estructuración del Payload (Respuesta API)
        return {
            "status": "success",
            "inputs": {
                "capacity_mw": capacity_mw,
                "utilization_pct": utilization_pct,
                "cooling_type": cooling_type
            },
            "results": {
                "stranded_capacity_mw": {
                    "min": round(stranded_mw_min, 3),
                    "max": round(stranded_mw_max, 3)
                },
                "financial_loss_usd_annual": {
                    "min": round(loss_min, 2),
                    "max": round(loss_max, 2)
                },
                "margin_vs_colocation_pct": round(margin_vs_colo, 2)
            },
            "metadata": {
                "pue_applied": pue,
                "colocation_ceiling_usd": self.colocation_ceiling_usd_mw_year
            }
        }

# Bloque de prueba de ejecución local
if __name__ == '__main__':
    api = StrandedCapacityAPI()
    resultado = api.calculate(capacity_mw=15.0, utilization_pct=87.0, cooling_type='Air Traditional')
    print(json.dumps(resultado, indent=2))
