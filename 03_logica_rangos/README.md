# Entregable 3: Lógica de Rangos y Cálculo de Límites

> **Proyecto:** No Country - Estimación de Capacidad Varada (*Stranded Capacity*) en Data Centers de IA  
> **Directorio:** `03_logica_rangos/`  

---

## 📌 Visión General

Este entregable documenta e implementa la **Lógica de Rangos** que alimenta la calculadora de *Stranded Capacity*. 

A diferencia de los modelos tradicionales que ofrecen estimaciones puntuales rígidas y generan una "falsa precisión", nuestro modelo adopta un enfoque basado en intervalos defensables y auditables (**Floor & Ceiling**), respaldados por la volatilidad térmica real (DVFS), disparidad geográfica de costos energéticos e imperfecciones de medición telemetrada *Behind-The-Meter*.

---

## 📁 Estructura del Entregable

| Archivo | Descripción |
| :--- | :--- |
| **[`DOCUMENTACION_RANGOS.md`](DOCUMENTACION_RANGOS.md)** | Documento teórico y metodológico de referencia. Explica las fuentes académicas, la justificación de negocio, las ecuaciones del Floor y Ceiling, y el uso de percentiles Monte Carlo (P10, P50, P90). |
| **[`logica_rangos.py`](logica_rangos.py)** | Módulo ejecutable en Python. Contiene la clase `RangeLogicEvaluator` para calcular límites físicos y financieros determinísticos (Floor, Mid, Ceiling) y simulaciones estocásticas. |
| **[`logica_rangos.ipynb`](logica_rangos.ipynb)** | Jupyter Notebook interactivo con gráficos comparativos, explicaciones paso a paso y demostración de percentiles de probabilidad. |
| **`README.md`** | Este documento de navegación y guía rápida. |

---

## 📐 Resumen del Modelo de Suelo y Techo (Floor & Ceiling)

```
[ Límite Inferior: Floor ] ---------- [ Valor Central: Mid ] ---------- [ Límite Superior: Ceiling ]
    Costo Incurrido Real                  Promedio Aritmético                Costo de Oportunidad
  OPEX Energía + CAPEX Amort.              (Floor + Ceiling) / 2               Colocation Market Rate
```

1. **Límite Inferior (Floor - Costo Incurrido Real):**
   $$\text{Loss}_{\text{Floor}} = (\text{kW Varados} \times 8760 \times \text{PUE} \times \text{Tarifa Eléctrica}) + \frac{\text{CAPEX Total Varado}}{\text{Ciclo de Vida (4.5 años)}}$$
   *Refleja el flujo de caja real que pierde la empresa por mantener encendida la potencia ineficiente.*

2. **Límite Superior (Ceiling - Costo de Oportunidad):**
   $$\text{Loss}_{\text{Ceiling}} = \text{kW Varados} \times \$184.00 \text{ USD/kW/mes} \times 12 \text{ meses}$$
   *Refleja el ingreso bruto no percibido por no comercializar esa potencia en el mercado de Colocation.*

3. **Percentiles Estocásticos (Monte Carlo):**
   - **P10 (Optimista / Suelo):** Mínima pérdida probable bajo condiciones ideales de PUE y baja tarifa eléctrica.
   - **P50 (Mediana / Base):** Estimación representativa para presupuestación anual.
   - **P90 (Pesimista / Techo):** Escenario conservador ante picos tarifarios o degradación del PUE.

---

## 🚀 Cómo Ejecutar

### 1. Ejecutar el Script en Consola
Para ver un reporte completo en terminal para facilities de prueba (Aire vs. Líquido):

```bash
python 03_logica_rangos/logica_rangos.py
```

### 2. Abrir el Jupyter Notebook
Para visualizar los gráficos y ejecutar de manera interactiva:

```bash
jupyter notebook 03_logica_rangos/logica_rangos.ipynb
```
