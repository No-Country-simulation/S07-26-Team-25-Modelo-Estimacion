# Metodología de Curaduría y Generación de Dataset de Referencia
> **Entregable 2** | Documento de auditoría para el dataset de referencia de 5,000 centros de datos de IA y motor de Simulación de Monte Carlo.

---

## 1. Contexto y Objetivos de Auditoría

Este documento detalla la metodología empleada para recopilar, curar y modelar estocásticamente el dataset de referencia de centros de datos de alta densidad orientados a Inteligencia Artificial (`dataset_5000_datacenters.csv`).

El objetivo principal es proveer transparencia auditable sobre:
1. La procedencia de los datos base empíricos provenientes de literatura técnica pública.
2. La definición de las distribuciones de probabilidad utilizadas para la generación del dataset sintético reproducible.
3. La formulación matemática del motor de **Simulación de Monte Carlo** para el cálculo de los percentiles de confianza ($P_{10}$, $P_{50}$, $P_{90}$).

---

## 2. Fuentes Públicas Curadas (`benchmarks_reales.csv`)

Los parámetros de referencia fueron consolidados a partir de reportes técnicos y encuestas de la industria:

| Fuente Citada | Año | Variable Curada | Valor / Rango | Justificación Técnica |
| :--- | :---: | :--- | :---: | :--- |
| **Microsoft GFS** (Sankar & Vaid) | 2010 | Stranded Capacity (%) | 12.0% - 13.0% | Trace-driven analysis que demuestra el desperdicio por sobreprovisión para cargas pico en cooling tradicional. |
| **Supermicro Benchmark Report** | 2025 | PUE & Ahorro de Nodo | PUE 1.08 (Líquido) / 16% Ahorro | Mediciones en hardware H100/B200 demostrando eliminación del consumo térmico de ventiladores de servidor. |
| **Uptime Institute Survey** | 2024 | PUE Global de Referencia | PUE 1.58 (Aire) | Promedio de eficiencia energética en data centers comerciales tradicionales operando con Hot/Cold aisle. |
| **U.S. EIA Commercial Pricing** | 2026 | Tarifa Eléctrica ($C_{elec}$) | $0.12 USD/kWh | Precio comercial promedio de la energía eléctrica en EE.UU. para gran escala industrial/comercial. |
| **Nlyte & Colocation Index** | 2025/26 | Tarifa Oportunidad Colo ($R_{colo}$) | $184.00 USD/kW/mes | Benchmark de precio de alquiler de espacio energizado por kW mensual en el mercado de colocation. |

---

## 3. Distribuciones Estadísticas para el Dataset Sintético (5,000 Registros)

Para reflejar la heterogeneidad del parque instalado real de centros de datos sin sesgar el modelo, se aplicaron las siguientes funciones de densidad de probabilidad:

### A. Capacidad del Facility ($MW_{facility}$)
- **Distribución**: Log-Normal ($\mu = 2.8$, $\sigma = 0.8$), recortada en el rango $[1.0 \text{ MW}, 250.0 \text{ MW}]$.
- **Fundamento**: Refleja la dominancia de facilities medianos de 10-30 MW, con una cola larga hacia hyperscalers de 100+ MW.

### B. Tecnología de Enfriamiento (`cooling_type`)
- **Distribución**: Categórica discreta basada en penetración de mercado proyectada:
  - `air-cooled` (Aire Tradicional): **55%**
  - `hybrid` (Aire + Líquido): **30%**
  - `liquid-cooled` (Direct-to-Chip / Inmersión): **15%**

### C. Utilización Actual del Facility ($U\%$)
- **Distribución**: Normal truncada ($\mu = 72.0\%$, $\sigma = 12.0\%$), acotada en $[20.0\%, 98.0\%]$.
- **Penalización por bajo uso**: Si $U\% < 50\%$, se incrementa la capacidad varada estimada mediante la fórmula:
  $$\text{Penalty} = (50.0 - U\%) \times 0.2$$

### D. Eficiencia Energética ($PUE$)
- **Distribución**: Normal truncada por tecnología de enfriamiento:
  - `air-cooled`: $\mathcal{N}(\mu=1.58, \sigma=0.05)$, rango $[1.30, 2.00]$.
  - `hybrid`: $\mathcal{N}(\mu=1.25, \sigma=0.03)$, rango $[1.12, 1.45]$.
  - `liquid-cooled`: $\mathcal{N}(\mu=1.08, \sigma=0.02)$, rango $[1.02, 1.20]$.

### E. Tarifas Financieras
- **Tarifa Eléctrica ($C_{elec}$)**: $\mathcal{N}(\mu=\$0.12, \sigma=\$0.02)$, rango $[\$0.06, \$0.22]$.
- **Tarifa Colocation ($R_{colo}$)**: $\mathcal{N}(\mu=\$184.00, \sigma=\$15.00)$, rango $[\$120.00, \$250.00]$.

---

## 4. Formulación de la Simulación de Monte Carlo (Percentiles P10, P50, P90)

El script `monte_carlo_simulation.py` ejecuta $N = 10,000$ iteraciones por escenario muestreando independientemente los valores de las distribuciones.

Para cada iteración $k$:
1. $kW_{stranded, k} = MW_{facility} \times \left( \frac{\%Stranded_k}{100} \right) \times 1000$
2. $\text{Loss}_{floor, k} = (kW_{stranded, k} \times 8760 \times PUE_k \times C_{elec, k}) + \frac{(CAPEX_{MW, k} / 1000) \times kW_{stranded, k}}{4.5}$
3. $\text{Loss}_{ceiling, k} = kW_{stranded, k} \times R_{colo, k} \times 12$
4. $\text{Loss}_{mid, k} = \frac{\text{Loss}_{floor, k} + \text{Loss}_{ceiling, k}}{2}$

A partir de las $10,000$ iteraciones de $\text{Loss}_{mid}$, se ordenan los resultados $L_{(1)} \le L_{(2)} \le \dots \le L_{(10000)}$ y se obtienen los percentiles de confianza:
- **$P_{10}$ (Escenario Piso / Conservador)**: Percentil 10 de la distribución acumulada.
- **$P_{50}$ (Escenario Mediano / Probable)**: Percentil 50 (Mediana).
- **$P_{90}$ (Escenario Techo / Pesimista de Riesgo)**: Percentil 90.

---

## 5. Instrucciones de Reproducción

Para regenerar los datasets y verificar los resultados de auditoría:

```bash
# 1. Regenerar el dataset de 5,000 registros
python 02_dataset_referencia/generate_dataset.py

# 2. Ejecutar la simulación estocástica de Monte Carlo standalone
python 02_dataset_referencia/monte_carlo_simulation.py

# 3. Abrir el notebook de Análisis Exploratorio de Datos (EDA)
jupyter notebook 02_dataset_referencia/EDA.ipynb
```
