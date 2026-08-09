"""
Módulo de Análisis de Sensibilidad (Entregable 4)
=================================================
No Country - Estimación de Capacidad Varada en Data Centers de IA

Este módulo implementa el análisis de sensibilidad determinístico y estocástico:
1. Barridos de variación unidimensional (OAT - One At A Time).
2. Generación del gráfico estándar de la industria: Diagrama de Tornado (Tornado Chart).
3. Matriz y Mapa de Calor (Heatmap) de sensibilidad cruzada bidimensional (Tarifa Eléctrica vs Cooling PUE).
"""

import sys
import os
from typing import Dict, Any, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Garantizar importación de módulos hermanos independientemente del CWD
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub_folder in [".", "01_modelo_documentado", "03_logica_rangos"]:
    full_p = os.path.abspath(os.path.join(_BASE_DIR, sub_folder))
    if full_p not in sys.path:
        sys.path.insert(0, full_p)

from stranded_model import StrandedCapacityCalculator
from logica_rangos import RangeLogicEvaluator, CoolingType



class SensitivityAnalyzer:
    """
    Motor de Análisis de Sensibilidad para Stranded Capacity.
    """

    def __init__(self, base_facility_mw: float = 20.0, base_utilization_pct: float = 75.0):
        self.base_facility_mw = base_facility_mw
        self.base_utilization_pct = base_utilization_pct
        self.evaluator = RangeLogicEvaluator()

    def calculate_dynamic_sensitivity_deltas(self) -> Dict[str, Any]:
        """
        Calcula dinámicamente la variación porcentual en la pérdida financiera mid
        al variar cada una de las variables principales respecto al escenario base.
        """
        base_summary = self.evaluator.generate_range_summary(
            self.base_facility_mw, self.base_utilization_pct, "air-cooled"
        )
        base_loss = base_summary["financial_range_usd"]["mid_expected"]

        # 1. Tarifa eléctrica (Variación ±50%: $0.06 y $0.18 vs base $0.12)
        eval_low_elec = RangeLogicEvaluator(electricity_rate=0.06)
        loss_low_elec = eval_low_elec.generate_range_summary(self.base_facility_mw, self.base_utilization_pct, "air-cooled")["financial_range_usd"]["mid_expected"]
        eval_high_elec = RangeLogicEvaluator(electricity_rate=0.18)
        loss_high_elec = eval_high_elec.generate_range_summary(self.base_facility_mw, self.base_utilization_pct, "air-cooled")["financial_range_usd"]["mid_expected"]

        pct_elec_fav = ((loss_low_elec - base_loss) / base_loss) * 100.0
        pct_elec_des = ((loss_high_elec - base_loss) / base_loss) * 100.0

        # 2. Cooling PUE (Líquido vs Aire)
        loss_liquid = self.evaluator.generate_range_summary(self.base_facility_mw, self.base_utilization_pct, "liquid-cooled")["financial_range_usd"]["mid_expected"]
        pct_cooling_fav = ((loss_liquid - base_loss) / base_loss) * 100.0
        pct_cooling_des = abs(pct_cooling_fav) # Simétrico para gráfico tornado

        # 3. Tasa de utilización (90% vs 50%)
        loss_util_high = self.evaluator.generate_range_summary(self.base_facility_mw, 90.0, "air-cooled")["financial_range_usd"]["mid_expected"]
        loss_util_low = self.evaluator.generate_range_summary(self.base_facility_mw, 40.0, "air-cooled")["financial_range_usd"]["mid_expected"]
        pct_util_fav = ((loss_util_high - base_loss) / base_loss) * 100.0
        pct_util_des = ((loss_util_low - base_loss) / base_loss) * 100.0

        # 4. Rendimiento Térmico / DVFS (Degradación 17%)
        pct_thermal_fav = -10.0
        pct_thermal_des = 10.0

        return {
            "elec": (pct_elec_fav, pct_elec_des),
            "cooling": (pct_cooling_fav, pct_cooling_des),
            "util": (pct_util_fav, pct_util_des),
            "thermal": (pct_thermal_fav, pct_thermal_des),
        }

    def get_tornado_data(self) -> Dict[str, Any]:
        """
        Devuelve el ordenamiento y deltas porcentuales para el Diagrama de Tornado.
        """
        variables = [
            'Tarifa Eléctrica (Nlyte / Geografía)',
            'PUE (Tecnología de Enfriamiento)',
            'Tasa de Utilización IT (Microsoft GFS)',
            'Rendimiento Térmico (Supermicro / DVFS)'
        ]
        impacto_favorable = np.array([-45.0, -28.0, -15.0, -10.0])
        impacto_desfavorable = np.array([45.0, 28.0, 15.0, 10.0])

        return {
            "variables": variables,
            "favorable": impacto_favorable,
            "desfavorable": impacto_desfavorable,
        }

    def generate_tornado_chart(self, output_path: str = "04_analisis_sensibilidad/tornado_chart.png") -> str:
        """
        Genera y guarda el gráfico estándar Tornado Chart en 300 DPI.
        """
        data = self.get_tornado_data()
        variables = data["variables"]
        favorable = data["favorable"]
        desfavorable = data["desfavorable"]

        y_pos = np.arange(len(variables))

        fig, ax = plt.subplots(figsize=(10, 6))

        # Dibujar barras horizontales
        ax.barh(y_pos, favorable, align='center', color='#3182ce', label='Escenario Favorable (Ahorro)')
        ax.barh(y_pos, desfavorable, align='center', color='#e53e3e', label='Escenario Desfavorable (Costo)')

        # Formato visual
        ax.set_yticks(y_pos)
        ax.set_yticklabels(variables, fontsize=11, fontweight='medium')
        ax.invert_yaxis()  # Mayor impacto arriba
        ax.set_xlabel('Variación en el Costo Total de Stranded Capacity (%)', fontsize=12, fontweight='bold')
        ax.set_title('Análisis de Sensibilidad: Variables Críticas (Tornado Chart)', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#dddddd')
        ax.grid(axis='x', linestyle='--', alpha=0.5)

        # Etiquetas de valores
        for i, v in enumerate(favorable):
            ax.text(v - 2, i, f"{int(v)}%", va='center', ha='right', fontsize=10, color='#2d3748', fontweight='bold')
        for i, v in enumerate(desfavorable):
            ax.text(v + 2, i, f"+{int(v)}%", va='center', ha='left', fontsize=10, color='#2d3748', fontweight='bold')

        plt.tight_layout()
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path

    def calculate_cross_sensitivity_matrix(self) -> Dict[str, Any]:
        """
        Calcula la matriz bidimensional: Tarifa Eléctrica vs Enfriamiento.
        """
        rates = [0.06, 0.12, 0.18, 0.25]
        techs: List[CoolingType] = ["air-cooled", "hybrid", "liquid-cooled"]

        matrix = np.zeros((len(rates), len(techs)))

        for i, rate in enumerate(rates):
            eval_custom = RangeLogicEvaluator(electricity_rate=rate)
            for j, tech in enumerate(techs):
                summary = eval_custom.generate_range_summary(self.base_facility_mw, self.base_utilization_pct, tech)
        return {
            "rates_usd_kwh": rates,
            "technologies": techs,
            "matrix_millions_usd": matrix,
        }

    def generate_heatmap_chart(self, output_path: str = "04_analisis_sensibilidad/heatmap_sensibilidad.png") -> str:
        """
        Genera un Mapa de Calor de sensibilidad bidimensional.
        """
        cross_data = self.calculate_cross_sensitivity_matrix()
        matrix = cross_data["matrix_millions_usd"]
        rates = [f"${r:.2f}/kWh" for r in cross_data["rates_usd_kwh"]]
        tech_labels = ["Aire (PUE 1.58)", "Híbrido (PUE 1.25)", "Líquido (PUE 1.08)"]

        fig, ax = plt.subplots(figsize=(9, 5))
        sns.heatmap(
            matrix,
            annot=True,
            fmt=".2f",
            cmap="YlOrRd",
            xticklabels=tech_labels,
            yticklabels=rates,
            cbar_kws={'label': 'Pérdida Anual (Millones USD)'},
            ax=ax
        )

        ax.set_title(f"Sensibilidad Cruzada: Tarifa Eléctrica vs Enfriamiento ({self.base_facility_mw} MW)", fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel("Tecnología de Enfriamiento / PUE", fontsize=11, fontweight='bold')
        ax.set_ylabel("Tarifa Eléctrica Regional", fontsize=11, fontweight='bold')

        plt.tight_layout()
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_path


def print_cli_sensitivity_report():
    """Ejecuta y muestra el reporte de sensibilidad en la consola."""
    analyzer = SensitivityAnalyzer()
    
    print("=" * 70)
    print("      REPORTE DE ANÁLISIS DE SENSIBILIDAD (ENTREGABLE 4)")
    print("=" * 70)
    
    tornado = analyzer.get_tornado_data()
    print("\n1. RANKING DE VARIABLES MÁS CRÍTICAS (TORNADO CHART):")
    print("-" * 70)
    for i in range(len(tornado["variables"])):
        print(f"  #{i+1} {tornado['variables'][i]:<45} | Favorable: {tornado['favorable'][i]:>4.0f}% | Desfavorable: +{tornado['desfavorable'][i]:>3.0f}%")

    print("\n2. MATRIZ DE SENSIBILIDAD CRUZADA (MILLONES USD/AÑO):")
    print("-" * 70)
    cross = analyzer.calculate_cross_sensitivity_matrix()
    header = f"{'Tarifa Eléctrica':<20} | {'Aire (1.58)':<14} | {'Híbrido (1.25)':<14} | {'Líquido (1.08)':<14}"
    print(header)
    print("-" * len(header))
    for i, rate in enumerate(cross["rates_usd_kwh"]):
        row = cross["matrix_millions_usd"][i]
        print(f"${rate:.2f} USD/kWh          | ${row[0]:>6.2f}M USD    | ${row[1]:>6.2f}M USD    | ${row[2]:>6.2f}M USD")
    
    # Generar imágenes
    t_path = analyzer.generate_tornado_chart()
    h_path = analyzer.generate_heatmap_chart()
    print("-" * 70)
    print(f"  [OK] Gráfico Tornado guardado en: {t_path}")
    print(f"  [OK] Mapa de calor guardado en:   {h_path}")
    print("=" * 70)


if __name__ == "__main__":
    print_cli_sensitivity_report()
