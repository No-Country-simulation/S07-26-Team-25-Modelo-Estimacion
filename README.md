# Stranded Capacity Estimator for High-Density AI Data Centers
> **No Country Project** | Estimación de Capacidad Varada y Eficiencia Financiera en Infraestructura de Cómputo de Alta Densidad.

## 📌 Contexto del Proyecto

En la infraestructura moderna de Inteligencia Artificial (AI Data Centers), existe un desperdicio estructural crítico denominado **Stranded Capacity** (Capacidad Varada). Ocurre cuando la potencia eléctrica pagada y aprovisionada ($CAPEX$ de soporte) no produce trabajo útil debido a que las capas físicas y operativas del facility no están coordinadas.

Este proyecto desarrolla un **modelo de estimación de rangos (Floor & Ceiling)** auditable, transparente y basado en datos públicos de la industria (Uptime Institute, Microsoft GFS, Supermicro, EIA), que permite a un operador entender el orden de magnitud de su ineficiencia financiera sin revelar información confidencial.

---

## 🎯 Requerimientos del Modelo

### Inputs
1. **Tamaño del Facility en MW** ($MW > 0$)
2. **Utilización Aproximada Actual** ($0\% - 100\%$)
3. **Tipo de Cooling**: `air-cooled` (Aire Tradicional), `liquid-cooled` (Direct-to-Chip / Inmersión), `hybrid` (Híbrido)

### Outputs
1. **Stranded Capacity estimada en % y MW** (Rangos Min, Mid, Max)
2. **Pérdida Financiera Anual estimada en Rango USD** (Metodología Floor & Ceiling)
3. **Valor Recuperable Potencial** ($USD$)
4. **Tiempo Estimado de Recuperación / ROI** (Meses)
5. **KPIs**: USD por MW perdido, Utilización Actual vs Benchmark (85%), Capacidad Efectiva vs Capacidad Pagada.

---

## 📂 Estructura del Repositorio (`Entregables/`)

El repositorio está organizado por entregables modulares:

```
Entregables/
├── README.md                                 # Este archivo (Visión General y Guía del Proyecto)
├── 01_modelo_documentado/
│   ├── README.md                             # Guía específica del Entregable 1
│   ├── stranded_model.py                     # Motor matemático en Python (Clase modular)
│   ├── modelo_stranded_capacity.ipynb        # Jupyter Notebook ejecutable con análisis e interacciones
│   └── DOCUMENTACION_MODELO.md               # Supuestos explícitos, ecuaciones y fuentes citadas
├── 02_dataset_referencia/
│   ├── benchmarks_reales.csv                 # Datos curados de fuentes públicas (Uptime, Supermicro, EIA, Microsoft)
│   ├── monte_carlo_simulation.py             # Motor de Simulación de Monte Carlo (Percentiles P10, P50, P90)
│   ├── generate_dataset.py                   # Generador del dataset sintético reproducible
│   ├── dataset_5000_datacenters.csv          # Dataset de 5,000 centros de datos con métricas estocásticas
│   ├── METODOLOGIA_DATASET.md                # Metodología auditable y distribuciones de probabilidad
│   └── EDA.ipynb                             # Notebook de Análisis Exploratorio de Datos y Campanas de Gauss
├── 03_logica_rangos/
│   ├── README.md                             # Guía específica del Entregable 3
│   ├── logica_rangos.py                      # Módulo de cálculo determinístico y estocástico de rangos
│   ├── logica_rangos.ipynb                   # Jupyter Notebook con gráficos de Floor, Ceiling y Monte Carlo
│   └── DOCUMENTACION_RANGOS.md               # Justificación teórica de rangos y ecuaciones de límites
├── 04_analisis_sensibilidad/
│   ├── README.md                             # Guía específica del Entregable 4
│   ├── analisis_sensibilidad.py              # Módulo de sensibilidad y generador del Tornado Chart
│   ├── analisis_sensibilidad.ipynb           # Jupyter Notebook interactivo con Tornado Chart y Heatmap
│   ├── tornado_chart.png                     # Diagrama de Tornado en alta resolución (300 DPI)
│   ├── heatmap_sensibilidad.png              # Mapa de calor bidimensional (300 DPI)
│   └── ANALISIS_SENSIBILIDAD.md              # Clasificación y justificación de variables por impacto
└── 05_documento_supuestos/
    ├── README.md                             # Guía específica del Entregable 5
    ├── DOCUMENTO_SUPUESTOS_AUDITABLE.md         # Documento técnico auditable para publicación
    ├── resumen_ejecutivo_publicable.md          # Resumen ejecutivo para C-Level (CFO/COO)
    └── referencias_bibliograficas.bib           # Base de datos bibliográfica BibTeX formal (IEEE/ACM)
```

---

## 📊 Estado de los Entregables

| # | Entregable | Estado | Ubicación |
|---|------------|--------|-----------|
| 1 | Modelo documentado en Python / Notebook con supuestos y fuentes |  Completado | [`01_modelo_documentado/`](01_modelo_documentado/) |
| 2 | Dataset de referencia de fuentes públicas con metodología |  Completado | [`02_dataset_referencia/`](02_dataset_referencia/) |
| 3 | Lógica de rangos (Límites Floor & Ceiling) |  Completado | [`03_logica_rangos/`](03_logica_rangos/) |
| 4 | Análisis de sensibilidad (Tornado Chart / Variables clave) |  Completado | [`04_analisis_sensibilidad/`](04_analisis_sensibilidad/) |
| 5 | Documento de supuestos auditable para publicación |  Completado | [`05_documento_supuestos/`](05_documento_supuestos/) |
| 6 | API (FastAPI) y backend para el frontend de la calculadora | ⏳ Pendiente | `06_api_backend/` |

---

## 🛠️ Instalación y Uso

### Prerrequisitos
- Python 3.9+
- Jupyter Notebook / JupyterLab (opcional, para visualizar notebooks)

### 1. Crear y Activar Entorno Virtual (`venv`)

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar el Proyecto / Pruebas

**Ejecutar suite de pruebas unitarias:**
```bash
python test_stranded_model.py
```

**Ejecutar el Jupyter Notebook interactivo:**
```bash
jupyter notebook 01_modelo_documentado/modelo_stranded_capacity.ipynb
```

**Uso como módulo Python:**
```python
import sys
sys.path.append("01_modelo_documentado")
from stranded_model import StrandedCapacityCalculator

calculator = StrandedCapacityCalculator()
result = calculator.calculate(
    facility_mw=15.0,
    utilization_pct=87.0,
    cooling_type="air-cooled"
)
print(result)
```

---

## 📄 Licencia y Créditos
Proyecto desarrollado para **No Country** - Simulación de Infraestructura y Data Science.
Fuentes de Datos: Uptime Institute (2024), Microsoft GFS (Sankar & Vaid 2010), Supermicro (2025), U.S. EIA (2026), Nlyte Software.
