# Resumen Ejecutivo Publicable: Estimación de Capacidad Varada (Stranded Capacity) y Eficiencia Financiera en Data Centers de IA

> **Orientado a:** CFOs, COOs, Directores de Infraestructura y Comités de Inversión  
> **Área:** Data Center Infrastructure & AI Financial Optimization  
> **Fecha:** Agosto 2026  

---

## 1. El Problema: El Ineficiente Costo Oculto de la IA

La expansión acelerada de los modelos de Inteligencia Artificial (LLMs) ha transformado la arquitectura física de los centros de datos. En clústeres de alta densidad (ej. NVIDIA H100/B200), la densidad de potencia por rack ha superado los **40–60 kW**, trasladando la restricción operativa del espacio físico al **arbitraje de potencia eléctrica**.

Existe un desperdicio financiero y técnico estructural denominado **Capacidad Varada (*Stranded Capacity*)**: potencia eléctrica pagada, aprovisionada y reservada en contratos de energía y $CAPEX$ de soporte que **jamás se convierte en trabajo computacional útil**.

### Causas Fundamentales:
* **Dimensionamiento Defensivo por Potencia Pico (Max-Power Provisioning):** Inmoviliza capital asumiendo consumos máximos teóricos continuos.
* **Desacople Térmico en Enfriamiento por Aire:** Provoca *throttling* dinámico (DVFS) a ~71°C, degradando hasta un **17%** del rendimiento computacional.
* **Falta de Telemetría Unificada:** Brecha entre los orquestadores de software (Slurm/Kubernetes) y la capa física de soporte (PDUs/Chillers).

---

## 2. Los Resultados: Hallazgos Clave del Modelo

A través de un motor determinístico de límites (**Floor & Ceiling**) y una simulación estocástica de Monte Carlo ($N=10,000$ iteraciones) validada con fuentes públicas de la industria (Microsoft GFS, Uptime Institute, Supermicro, EIA, Nlyte), se cuantifican los siguientes resultados para un centro de datos de **20 MW al 75% de utilización**:

| Tecnología de Enfriamiento | PUE Realizado | Potencia Varada (MW) | Pérdida Financiera Anual (Floor) | Pérdida Financiera Anual (Ceiling) | Estimación Central (Mid Expected) | Monte Carlo Median (P50) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Aire Tradicional (`air-cooled`)** | **1.58** | **2.50 MW** | $5.13 M USD | $5.52 M USD | **$5.32 M USD** | **$5.31 M USD** |
| **Híbrido (`hybrid`)** | **1.25** | **1.80 MW** | $3.88 M USD | $3.97 M USD | **$3.93 M USD** | **$3.92 M USD** |
| **Líquido Direct-to-Chip (`liquid-cooled`)** | **1.08** | **0.70 MW** | $1.76 M USD | $1.55 M USD | **$1.65 M USD** | **$1.64 M USD** |

> **Conclusión Financiera Principal:** Migrar de enfriamiento tradicional por aire a **Refrigeración Líquida Direct-to-Chip** en un facility de 20 MW reduce el desperdicio financiero anual en un **68.9%**, generando un ahorro neto directo de más de **$3.67 Millones de USD al año**.

---

## 3. Sensibilidad y Factores de Impacto (Tornado Chart)

El análisis de sensibilidad identifica la **Tarifa Eléctrica ($C_{elec}$)** y la **Tecnología de Enfriamiento (PUE)** como los dos factores con mayor elasticidad sobre la pérdida anual:

1. **Tarifa Eléctrica ($\pm 45\%$ Impacto):** Una variación del $+50\%$ en la tarifa por kWh eleva la pérdida en $+45\%$. En mercados de alta tarifa ($0.25 USD/kWh), operar con aire tradicional representa una fuga de hasta **$8.90 M USD/año**.
2. **Tecnología de Cooling ($\pm 28\%$ Impacto):** La adopción de refrigeración líquida elimina los ventiladores parasitarios del chasis, ahorrando un **16%** adicional de energía a nivel de procesador.
3. **Utilización IT ($\pm 15\%$ Impacto):** Operar por debajo del 50% de utilización gatilla una penalización progresiva por ineficiencia fija de soporte.

---

## 4. Recomendaciones de Inversión y Próximos Pasos (ROI)

1. **Implementación de Software DCIM & Telemetría IA:**
   * Con una inversión estimada de **$75,000 USD por MW** ($1.5M USD para un facility de 20 MW), la optimización dinámica mediante software y sensores térmicos permite recuperar el **80% del valor varado**.
   * **Tiempo Estimado de Recuperación (ROI):** **4.2 meses** en sistemas de aire tradicional y **5.5 meses** en instalaciones híbridas.

2. **Regla de Decisión "Build vs. Buy":**
   * Cualquier facility de aire tradicional cuya pérdida Floor supere el **80% de la tarifa de Colocation ($184/kW/mes)** debe priorizar inmediatamente la conversión tecnológica a refrigeración líquida o la relocalización regional.

---
*Para acceder a las demostraciones interactivas, código en Python y documentación matemática auditable completa, consulte los entregables del repositorio.*
