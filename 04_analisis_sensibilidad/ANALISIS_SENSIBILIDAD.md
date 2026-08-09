# Análisis de Sensibilidad: Variables Críticas y Factores de Impacto

> **Proyecto:** No Country - Estimación de Capacidad Varada (*Stranded Capacity*) en Data Centers de IA  
> **Entregable:** 4 - Análisis de Sensibilidad (Tornado Chart y Matriz de Elasticidad)  
> **Estado:** Documento Oficial de Referencia Metodológica  

---

## 1. Resumen Ejecutivo (El "Qué" y el "Por qué")

En la modelación técnico-económica de infraestructura crítica de Inteligencia Artificial, un **Análisis de Sensibilidad** permite responder a la pregunta fundamental del Comité de Inversiones (CFO / COO):

> *"Si los supuestos del escenario base fluctúan debido al mercado o la operación, ¿cuál variable genera la mayor variación en la pérdida financiera anual por Stranded Capacity y por qué?"*

Basándonos en la literatura científica y benchmarks de la industria (Uptime Institute, Microsoft GFS, Supermicro, EIA, Nlyte Software), las variables independientes se ordenan de **mayor a menor impacto porcentual sobre el costo total** en el siguiente **Diagrama de Tornado**:

```
                                 ESCENARIO FAVORABLE (AHORRO) <--- 0% ---> ESCENARIO DESFAVORABLE (COSTO)
Tarifa Eléctrica (Nlyte / Geografía)       [-45%] ==================|================== [+45%]
PUE (Tecnología de Enfriamiento)           [-28%] ===========|=========== [+28%]
Utilización IT (Microsoft GFS)             [-15%] ======|====== [+15%]
Rendimiento Térmico (Supermicro / DVFS)    [-10%] ===|=== [+10%]
```

---

## 2. Clasificación y Justificación de Variables por Impacto

### 🥇 1. Tarifa Eléctrica / Ubicación Geográfica (Mayor Impacto: $\pm 45\%$)
* **Métrica Evaluada:** Tarifa comercial de energía en USD/kWh (Escenario Base: **$0.12 USD/kWh**; Rango: $0.06 a $0.25 USD/kWh).
* **Justificación de Negocio:** La tarifa eléctrica es la variable más sensible porque el costo no escala de manera lineal con la geografía, sino exponencial en función de la densidad por rack. Según los datos de **Nlyte Software / Colocation Market Benchmarks**, el costo operativo anual de mantener un mismo rack de 60 kW de IA puede **cuadruplicarse** (pasando de **$51,116 USD** en regiones con PPA hidroeléctrico de bajo costo a **$207,934 USD** en mercados metropolitanos saturados).
* **Sensibilidad:** Una variación del $+50\%$ en la tarifa eléctrica incrementa el Floor de pérdida anual en aproximadamente $+45\%$.

---

### 🥈 2. Tecnología de Enfriamiento / PUE (Alto Impacto: $\pm 28\%$)
* **Métrica Evaluada:** Eficiencia de Enfriamiento PUE (Aire: **1.58**, Híbrido: **1.25**, Líquido Direct-to-Chip: **1.08**).
* **Justificación de Negocio:** La transición tecnológica de refrigeración por aire a líquida directa tiene un **doble impacto positivo**:
  1. Reduce directamente el multiplicador de energía consumida por la infraestructura de soporte (PUE cae de 1.58 a 1.08).
  2. Elimina los ventiladores parasitarios (*fans*) dentro del chasis del servidor, ahorrando hasta un **16%** del consumo total a nivel de nodo computacional (Supermicro 2025 AI Benchmark).
* **Sensibilidad:** Migrar un facility de 20 MW de Aire a Líquido reduce el Floor de pérdida financiera en más del **60%**, ahorrando más de **$3.3 Millones USD al año**.

---

### 🥉 3. Tasa de Utilización IT / Sobre-provisión (Impacto Medio-Alto: $\pm 15\%$)
* **Métrica Evaluada:** Porcentaje de carga útil activa ($0\%$ a $100\%$; Benchmark objetivo: **85%**).
* **Justificación de Negocio:** Dicta la cantidad base de hardware encendido e inactivo. Como demostró la investigación de **Microsoft GFS (Sankar & Vaid 2010)** mediante análisis de trazas en producciones reales, el aprovisionamiento defensivo bajo criterio de "Potencia Pico Teórica" genera de un **12% a un 13% de ineficiencia estructural permanente**, inmovilizando millones de dólares de CAPEX en infraestructura inutilizada.
* **Sensibilidad:** Operar por debajo del 50% de utilización gatilla una penalización progresiva de $+0.2\%$ de ineficiencia varada por cada punto porcentual de caída.

---

### 🏅 4. Rendimiento Térmico / DVFS Throttling (Impacto Medio: $\pm 10\%$)
* **Métrica Evaluada:** Límite térmico de operación del procesador GPU/CPU (°C) y margen térmico.
* **Justificación de Negocio:** En sistemas enfriados por aire tradicional, cuando los procesadores superan temperaturas críticas (~71°C), los algoritmos de escalado dinámico de voltaje y frecuencia (**DVFS**) reducen la frecuencia del chip (*thermal throttling*), degradando el rendimiento computacional hasta en un **17%**. Esto fuerza al operador a mantener más servidores encendidos para completar la misma carga de trabajo de entrenamiento/inferencia, elevando la potencia varada.
* **Sensibilidad:** La refrigeración líquida mantiene la temperatura estable entre 46°C y 54°C, eliminando por completo este margen de degradación.

---

## 3. Matriz de Elasticidad y Sensibilidad Cruzada (Bidimensional)

El impacto financiero no ocurre de forma aislada. La combinación de una **tarifa eléctrica alta** con una **tecnología de enfriamiento ineficiente (Aire)** genera una espiral de costos de ineficiencia.

La siguiente matriz ilustra la pérdida financiera anual estimada (en Millones USD) para un centro de datos de **20 MW** al **75% de utilización**, evaluando la interacción entre la **Tarifa Eléctrica ($/kWh)** y el **Tipo de Cooling / PUE**:

| Tarifa Eléctrica ($/kWh) | Aire (PUE 1.58) | Híbrido (PUE 1.25) | Líquido (PUE 1.08) | Ahorro Anual (Aire vs Líquido) |
| :---: | :---: | :---: | :---: | :---: |
| **$0.06 USD/kWh** | $3.58 M USD | $2.91 M USD | $1.41 M USD | **$2.17 M USD (-60.6%)** |
| **$0.12 USD/kWh** (Base) | $5.26 M USD | $3.91 M USD | $1.69 M USD | **$3.57 M USD (-67.8%)** |
| **$0.18 USD/kWh** | $6.94 M USD | $4.91 M USD | $1.97 M USD | **$4.97 M USD (-71.6%)** |
| **$0.25 USD/kWh** | $8.90 M USD | $6.08 M USD | $2.29 M USD | **$6.61 M USD (-74.2%)** |

> **Conclusión Clave para el CFO:** A mayor tarifa eléctrica regional, mayor es el retorno económico absoluto al migrar a tecnología de refrigeración líquida (*Direct-to-Chip*). En zonas de tarifas elevadas ($0.25/kWh), la adopción de cooling líquido evita pérdidas de hasta **$6.61M USD/año**.

---

## 4. Guía de Interpretación para la Calculadora

1. **Priorización de Inversiones (ROI de Remedación):**
   - El operador debe enfocarse primero en la variable de mayor elasticidad modificable: la **tecnología de enfriamiento y monitoreo DCIM**.
   - Mientras la tarifa eléctrica depende de la ubicación geográfica, el PUE y el control de *throttling* térmico son variables bajo el control operativo directo de la empresa.

2. **Regla de Decisión:**
   - Si la tarifa eléctrica regional supera los **$0.15 USD/kWh**, operar con refrigeración por aire tradicional genera un costo de ineficiencia que supera el umbral del 80% del mercado de Colocation, recomendando estratégicamente la migración a líquido o relocalización regional.
