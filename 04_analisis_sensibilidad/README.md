# Entregable 4: Análisis de Sensibilidad y Diagrama de Tornado

> **Proyecto:** No Country - Estimación de Capacidad Varada (*Stranded Capacity*) en Data Centers de IA  
> **Directorio:** `04_analisis_sensibilidad/`  

---

## 📌 Visión General

Este entregable responde cuantitativamente a la pregunta clave para ejecutivos (CFO / COO / Directores de Operaciones):

> *"¿Qué variables mueven más el resultado de las pérdidas financieras por Stranded Capacity y por qué?"*

Se clasifican las variables independientes de mayor a menor sensibilidad utilizando el estándar visual de la industria (**Tornado Chart**), y se evalúa la sensibilidad cruzada bidimensional (Tarifa Eléctrica vs. Tecnología de Enfriamiento).

---

## 📁 Estructura del Entregable

| Archivo | Descripción |
| :--- | :--- |
| **[`ANALISIS_SENSIBILIDAD.md`](ANALISIS_SENSIBILIDAD.md)** | Documento formal y auditable que justifica el ranking de elasticidad de variables con fuentes citadas (Nlyte, Supermicro, Microsoft GFS, Uptime, EIA). |
| **[`analisis_sensibilidad.py`](analisis_sensibilidad.py)** | Módulo ejecutable en Python. Contiene la clase `SensitivityAnalyzer` para calcular variaciones OAT, matrices cruzadas y generar gráficos en alta resolución. |
| **[`analisis_sensibilidad.ipynb`](analisis_sensibilidad.ipynb)** | Jupyter Notebook interactivo con renderizado del Tornado Chart y mapas de calor (Heatmaps). |
| **[`tornado_chart.png`](tornado_chart.png)** | Gráfico del Diagrama de Tornado en 300 DPI. |
| **[`heatmap_sensibilidad.png`](heatmap_sensibilidad.png)** | Mapa de calor bidimensional en 300 DPI. |
| **`README.md`** | Este documento de navegación y guía rápida. |

---

## 📊 Ranking de Sensibilidad (Tornado Chart Summary)

1. **Tarifa Eléctrica / Ubicación Geográfica ($\pm 45\%$):**  
   *Mayor Impacto.* El costo no escala linealmente, sino de forma exponencial por densidad del rack. En regiones costosas ($0.25 USD/kWh), el costo operativo por rack puede cuadruplicarse respecto a regiones de bajo costo.
2. **PUE / Tecnología de Enfriamiento ($\pm 28\%$):**  
   *Alto Impacto.* Pasar de aire (PUE 1.58) a líquido (PUE 1.08) reduce el consumo de soporte y elimina hasta un 16% de consumo parasitario por ventiladores en chasis.
3. **Tasa de Utilización IT ($\pm 15\%$):**  
   *Impacto Medio-Alto.* Define la sobre-provisión estructural inmovilizada (hasta 13% de ineficiencia por aprovisionamiento defensivo pico).
4. **Rendimiento Térmico / DVFS ($\pm 10\%$):**  
   *Impacto Medio.* El *throttling* térmico en aire (>71°C) degrada el rendimiento computacional hasta en un 17%, obligando a encender más procesadores.

---

## 🚀 Cómo Ejecutar

### 1. Ejecutar el Script en Consola
Para generar los gráficos en alta resolución y visualizar las tablas en la terminal:

```bash
python 04_analisis_sensibilidad/analisis_sensibilidad.py
```

### 2. Abrir el Jupyter Notebook
Para explorar las visualizaciones de manera interactiva:

```bash
jupyter notebook 04_analisis_sensibilidad/analisis_sensibilidad.ipynb
```
