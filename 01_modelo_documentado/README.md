# Entregable 1: Modelo Documentado en Python / Notebook

## 📋 Descripción del Entregable
Este subdirectorio contiene la solución completa para el **Primer Entregable** del proyecto de estimación de *Stranded Capacity* para No Country:

> **Objetivo**: Modelo documentado en Python o notebook con supuestos explícitos y fuentes citadas.

---

## 🗂️ Archivos Contenidos

| Archivo | Descripción |
|---------|-------------|
| [`stranded_model.py`](stranded_model.py) | Implementación modular en Python de la clase `StrandedCapacityCalculator`, incluyendo tipado estático, validaciones y docstrings con citación formal de fuentes. |
| [`modelo_stranded_capacity.ipynb`](modelo_stranded_capacity.ipynb) | Jupyter Notebook interactivo con celdas teóricas (Markdown) que documentan los supuestos y fuentes, celdas de código de prueba para escenarios reales (15 MW en aire, líquido e híbrido) y gráficos comparativos. |
| [`DOCUMENTACION_MODELO.md`](DOCUMENTACION_MODELO.md) | Documento exhaustivo que detalla la matriz de supuestos termodinámicos, el desarrollo de las ecuaciones (metodología Floor & Ceiling), la justificación de rangos y la bibliografía citada. |

---

## ⚡ Formas de Uso

### 1. Ejecución mediante Jupyter Notebook
Para abrir y ejecutar el notebook interactivo:
```bash
jupyter notebook modelo_stranded_capacity.ipynb
```

### 2. Uso del Módulo Python en Scripts o Servicios
```python
from stranded_model import StrandedCapacityCalculator, CalculatorInput

calculator = StrandedCapacityCalculator()
input_data = CalculatorInput(
    facility_mw=15.0,
    utilization_pct=87.0,
    cooling_type="air-cooled"
)

response = calculator.calculate_from_object(input_data)
print(f"Stranded MW (Mid): {response.stranded_capacity_mw_range['mid']} MW")
print(f"Financial Loss (Mid): ${response.annual_financial_loss_usd.mid_usd_annual:,.2f} USD")
```

---

## 📚 Fuentes Bibliográficas Principales
1. **Microsoft GFS (Sankar & Vaid, 2010)**: *Trace-Driven Analysis of Data Center Power & Provisioning*.
2. **Supermicro (2025)**: *Green Computing & Liquid Cooling Benchmark Report*.
3. **Uptime Institute (2024)**: *Global Data Center Survey Results*.
4. **U.S. Energy Information Administration (EIA, 2026)**: *Commercial Electricity Rates*.
5. **Nlyte Software (2025/2026)**: *Colocation Pricing Benchmarks*.
