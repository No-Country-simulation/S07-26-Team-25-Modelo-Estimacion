# Entregable 5: Documento de Supuestos Auditables para Publicación

> **Proyecto:** No Country — Estimación de Capacidad Varada (*Stranded Capacity*) en Data Centers de IA  
> **Ubicación:** `05_documento_supuestos/`  
> **Estado:**  Completado y Listo para Auditoría / Publicación  

---

## 📌 Descripción General

El **Entregable 5** constituye la síntesis metodológica y auditable definitiva del proyecto. Consolida en un único cuerpo documental listo para publicación académica e industrial toda la investigación, supuestos, ecuaciones, distribuciones estocásticas, análisis de sensibilidad y referencias bibliográficas desarrolladas a lo largo de los **Entregables 1, 2, 3 y 4**.

Este entregable provee la máxima transparencia matemática e institucional para respaldar las salidas de la calculadora de *Stranded Capacity* ante auditores independientes, directores financieros (CFO) y comités de inversión (COO).

---

## 📂 Contenido del Entregable

```
05_documento_supuestos/
├── README.md                                 # Este archivo (Guía de navegación del Entregable 5)
├── DOCUMENTO_SUPUESTOS_AUDITABLE.md         # Documento técnico maestro auditable con supuestos y ecuaciones
├── resumen_ejecutivo_publicable.md          # Resumen ejecutivo orientado a C-Level (CFO/COO)
└── referencias_bibliograficas.bib           # Base de datos bibliográfica BibTeX formal (Citas IEEE/ACM)
```

---

## 📄 Resumen de Documentos

### 1. `DOCUMENTO_SUPUESTOS_AUDITABLE.md`
El documento maestro de auditoría técnica y matemática. Incluye:
* **Marco Teórico:** Desacople physical-operational, *Max-Power Provisioning* y *DVFS Throttling*.
* **Matriz de Supuestos:** Tabla unificada con PUE, % Stranded, CCF, CAPEX/MW y Ahorro energéticos por cooling type (`air-cooled`, `hybrid`, `liquid-cooled`).
* **Desarrollo Matemático Completo:** Ecuaciones de MW varados, Floor (OPEX+CAPEX amortizado), Ceiling (Tarifa Colocation $184/kW/mes), Mid, ROI y Simulación Monte Carlo.
* **Protocolo de Auditoría:** Checklist de verificación y matriz de elasticidad bidimensional.
* **Bibliografía:** 8 fuentes citadas detalladamente (Microsoft GFS, Uptime Institute, Supermicro, EIA, Nlyte, Gartner, NVIDIA, IEEE/ACM).

### 2. `resumen_ejecutivo_publicable.md`
Síntesis ejecutiva de alto nivel formulada para tomadores de decisiones. Presenta la justificación financiera para la adopción de refrigeración líquida (*Direct-to-Chip*), mostrando el ahorro anual de **$3.67M USD** para facilities de 20 MW y el ROI de remediación en **4.2 meses**.

### 3. `referencias_bibliograficas.bib`
Archivo de citas bibliográficas estándar BibTeX con las 8 referencias clave de la industria, estructuradas adecuadamente para su importación en LaTeX, Pandoc o gestores como Zotero y Mendeley.

---

## 🛠️ Verificación Automatizada

Para ejecutar la suite integral de verificación que audita los 5 entregables del proyecto:

```bash
# Ejecutar verificación de todos los entregables (incluyendo Entregable 5)
python verify_all_entregable5.py
```

---

## 🔗 Vinculación con los demás Entregables

* ➡️ **Entregable 1:** [`../01_modelo_documentado/`](../01_modelo_documentado/) — Motor matemático en Python (`stranded_model.py`)
* ➡️ **Entregable 2:** [`../02_dataset_referencia/`](../02_dataset_referencia/) — Dataset de 5,000 DCs y Monte Carlo (`monte_carlo_simulation.py`)
* ➡️ **Entregable 3:** [`../03_logica_rangos/`](../03_logica_rangos/) — Demostración de límites Floor & Ceiling (`logica_rangos.py`)
* ➡️ **Entregable 4:** [`../04_analisis_sensibilidad/`](../04_analisis_sensibilidad/) — Tornado Chart y Elasticidad (`analisis_sensibilidad.py`)
