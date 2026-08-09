# Documento de Transparencia y Supuestos del Modelo

### 1. Declaración de Honestidad del Modelo
Este modelo de estimación de *Stranded Capacity* ha sido diseñado bajo un enfoque determinístico de Floor & Ceiling (Suelo y Techo). No es una bola de cristal financiera, sino una herramienta de contención de riesgos. Su objetivo no es predecir el centavo exacto que se perderá en 2035, sino establecer los límites matemáticos dentro de los cuales la operación de un Data Center de IA deja de ser financieramente viable frente a la alternativa de Colocation.

### 2. Origen de los Datos (Single Source of Truth)
Todos los cálculos presentados dependen de las siguientes métricas base de la industria, las cuales están codificadas en nuestro dataset público:
*   **Sobre-provisión Estructural (13%):** Asumimos que los picos de carga obligan a mantener hardware ocioso. Este techo del 13% es extraído de las trazas de utilización de *Microsoft GFS*.
*   **Eficiencia Térmica (16% y 71°C):** El ahorro energético del 16% a nivel nodo y el límite térmico de 71°C para *throttling* provienen de las pruebas empíricas publicadas por *Supermicro* en sus arquitecturas de refrigeración líquida vs. aire.
*   **Volatilidad de Tarifa Eléctrica:** El modelo utiliza los extremos geográficos de *Nlyte*, asumiendo que un mismo rack puede costar desde $51,116 USD anuales (escenario óptimo) hasta $207,934 USD (escenario pesimista).
*   **Techo de Mercado (Colocation):** Fijamos el costo de oportunidad estricto en $184/kW/mes.

### 3. Limitaciones Reconocidas (Lo que el modelo excluye explícitamente)
Para mantener la integridad auditable, declaramos que este simulador asume condiciones estáticas en áreas que, en la realidad, son dinámicas:
*   **Exclusión de Inflación y Fluctuación Energética:** El TCO a 10 años asume una tarifa eléctrica promediada y congelada. No modela crisis energéticas geopolíticas ni aumentos dinámicos por inflación anual.
*   **PUE Lineal:** El modelo asume que el PUE (*Power Usage Effectiveness*) se mantiene constante todo el año. En la realidad operativa, el PUE fluctúa según la estación del año (verano vs. invierno), especialmente en configuraciones enfriadas por aire.
*   **Ciclo de Vida de Hardware Homogéneo:** Asumimos una amortización plana de 3 a 6 años. No contempla la depreciación acelerada que podría causar la rápida obsolescencia de las GPUs de nueva generación.

### 4. Justificación del Uso de Rangos
Debido a las limitaciones mencionadas, el modelo tiene prohibido emitir valores absolutos. Todo resultado financiero se entrega con un límite inferior y superior. Presentar un número estático único constituiría una "falsa precisión" y una mala práctica analítica en la planificación de infraestructura crítica.
