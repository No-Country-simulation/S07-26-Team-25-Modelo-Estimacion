# Metodología y Lógica de Rangos: Stranded Capacity

### 1. ¿Por qué el modelo se expresa como un rango (y no como un valor absoluto)?
En la gestión de infraestructura crítica de Inteligencia Artificial, utilizar promedios o estimaciones puntuales genera una "falsa precisión". El modelo se expresa en rangos para aislar y reflejar la varianza operativa real, fundamentada en los siguientes factores de incertidumbre técnica:
*   **Volatilidad del Entorno Térmico:** La eficiencia proyectada está intrínsecamente ligada al margen térmico y a los algoritmos de escalado dinámico (DVFS). Por ejemplo, sistemas en refrigeración líquida operan entre 46°C y 54°C, mientras que el aire alcanza límites de *throttling* de 71°C, lo que genera variaciones de hasta un 17% en el rendimiento computacional.
*   **Asimetría Geográfica de Costos:** El multiplicador de ineficiencia varía drásticamente según la región. Un rack de 60 kW puede costar desde $51,116 en zonas de bajo costo hasta $207,934 en zonas de alto costo. Un modelo de rango absorbe esta volatilidad de la "Espiral de Densidad-Costo".
*   **Errores de Telemetría (Detrás del Medidor):** En sistemas enfriados por aire, existe un error de medición donde la potencia de los ventiladores del servidor se cuenta erróneamente como carga de IT. El rango inferior y superior contempla las posibles desviaciones en la lectura del PUE real.

### 2. ¿Cómo se calculan los límites? (Arquitectura Matemática)
Para garantizar la rentabilidad de la infraestructura, el modelo no calcula los rangos al azar, sino que establece un marco estricto de "suelo y techo" (Floor & Ceiling) financiero.

**A. Cálculo de Límites Físicos (Megavatios Varados)**
El límite de MW desperdiciados se calcula aplicando un coeficiente de ineficiencia sobre la capacidad no utilizada, escalado por el PUE de la instalación:
*   **Rango de Ineficiencia por Tecnología:** 12% - 13% para Aire, 8% - 10% para Híbrido, y < 5% para Líquido.
*   *Fórmula base:* `Capacidad Total * (1 - Utilización IT) * Rango de Ineficiencia * PUE`

**B. Límite Financiero Inferior (Punto de Equilibrio Operativo)**
Define el costo mínimo aceptable para mantener la capacidad activa en instalaciones propias. Se asume una extensión del ciclo de vida del hardware de 3 a 6 años para diluir el CAPEX.
*   *Fórmula (Floor Formula):* `(OPEX Energy [$/kWh * 8760 * PUE] + Amortized CAPEX [Total CAPEX / Lifecycle]) / Total kW`.

**C. Límite Financiero Superior (Costo de Oportunidad)**
Define el techo de pérdida tolerable antes de que sea matemáticamente mejor subcontratar el servicio. 
*   *Límite Máximo:* Se utiliza la tasa del mercado de Colocation de $184 por kW al mes como techo absoluto.
*   *Regla de Decisión:* Cualquier ineficiencia operativa que eleve el costo interno de la "Stranded Capacity" por encima de este umbral invalida la justificación económica de operar infraestructura privada. El rango de la calculadora alerta al operador si su costo interno no se mantiene, al menos, un 20% por debajo de este techo.
