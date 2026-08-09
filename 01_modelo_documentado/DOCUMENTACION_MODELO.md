# Documentación del Modelo de Estimación de Stranded Capacity
> **Entregable 1** | Modelo documentado en Python con supuestos explícitos y fuentes citadas.

---

## 1. Introducción y Definición Teórica

En los centros de datos modernos de alta densidad orientados a Inteligencia Artificial (AI Data Centers), el factor limitante para la expansión de la infraestructura no es la disponibilidad de espacio físico, sino el **arbitraje de potencia eléctrica pagada**.

La **Capacidad Varada (Stranded Capacity)** es una ineficiencia estructural caracterizada por la brecha entre la potencia eléctrica en Megavatios (MW) contratada y amortizada ($CAPEX$ de soporte) y la utilización real consumida por la infraestructura de cómputo en producción. 

### ¿Por qué se produce la Capacidad Varada?
1. **Aprovisionamiento por Carga Pico ("Max-Power Provisioning")**: Tradicionalmente, la potencia eléctrica y de enfriamiento se dimensiona asumiendo que el 100% de los servidores operarán a su máximo consumo térmico de manera simultánea.
2. **Desacople entre capas físicas y operativas**: Los sistemas de infraestructura (chillers, UPS, PDUs) no se comunican dinámicamente con los orquestadores de carga de trabajo (Kubernetes, Slurm, vSphere).
3. **Restricciones térmicas y Cooling Capacity Factor (CCF)**: En arquitecturas basadas exclusivamente en aire, el sobrecalentamiento local imposibilita encender racks adicionales aunque la subestación eléctrica disponga de capacidad nominal.

---

## 2. Matriz de Supuestos Explícitos y Fuentes Citadas

El modelo clasifica los parámetros de ineficiencia y costos de acuerdo con la tecnología de enfriamiento desplegada en el facility (`air-cooled`, `hybrid`, `liquid-cooled`).

| Parámetro / Métrica | Aire Tradicional (`air-cooled`) | Híbrido (`hybrid`) | Líquido Direct-to-Chip (`liquid-cooled`) | Fuente Citada / Referencia |
|---------------------|--------------------------------|-------------------|------------------------------------------|----------------------------|
| **PUE de Referencia ($PUE_{ref}$)** | **1.58** | **1.25** | **1.08** | Uptime Institute Global Data Center Survey (2024) / Supermicro (2025) |
| **Stranded Capacity Estructural (%)** | **12.0% - 13.0%** (Mid: 12.5%) | **8.0% - 10.0%** (Mid: 9.0%) | **2.0% - 5.0%** (Mid: 3.5%) | Microsoft GFS (Sankar & Vaid 2010) & Supermicro (2025) |
| **Cooling Capacity Factor (CCF)** | **3.9** | **1.8** | **1.2** | Uptime Institute Technical Reports |
| **CAPEX Estimado por MW ($)** | **$11,000,000 USD** | **$13,500,000 USD** | **$17,500,000 USD** | Industry Building & Infrastructure Benchmarks (2025) |
| **Ahorro Energético de Nodo** | Base (0%) | ~8% | **16%** | Supermicro Benchmark Report (2025) |

### Parámetros Financieros Globales
- **Tarifa Eléctrica Comercial Promedio ($C_{elec}$)**: `$0.12 USD/kWh` (Fuente: U.S. Energy Information Administration - EIA, 2026).
- **Tarifa de Oportunidad Colocation ($R_{colo}$)**: `$184.00 USD/kW/mes` = `$2,208 USD/kW/año` (Fuente: Nlyte Software & Data Center Colocation Index, 2025/2026).
- **Periodo de Amortización ($T_{life}$)**: `4.5 años` (Promedio de ciclo de vida del hardware y soporte energizante: 3 a 6 años).
- **Benchmark Objetivo de Utilización ($U_{bench}$)**: `85.0%` (Estándar de la industria para evitar estrangulamiento).
- **Costo de Remediación ($C_{remed}$)**: `$75,000 USD por MW` (Implementación de software DCIM, telemetría y sensores térmicos).
- **Factor de Capacidad Recuperable**: `80.0%` (Se asume que mediante optimización de potencia dinámica se puede rescatar el 80% del valor varado).

---

## 3. Desarrollo de Ecuaciones y Metodología de Rangos (Floor & Ceiling)

### A. Estimación de Megavatios Varados ($MW_{stranded}$)
Dada la capacidad contratada del facility $MW_{facility}$ y la utilización actual $U\%$:

$$MW_{stranded, min} = MW_{facility} \times \left( \frac{\%_{stranded, min}}{100} \right)$$
$$MW_{stranded, max} = MW_{facility} \times \left( \frac{\%_{stranded, max}}{100} \right)$$

Si la utilización del facility cae por debajo del 50%, se aplica una penalización por bajo uso:
$$\text{Penalty} = (50.0 - U) \times 0.2$$
$$\%_{stranded, mid} = \min(\%_{stranded, max}, \%_{base\_mid} + \text{Penalty})$$

$$kW_{stranded, mid} = MW_{stranded, mid} \times 1,000$$

---

### B. Pérdida Financiera Anual ($USD$) - Metodología Floor & Ceiling

Para evitar la falsa precisión de un único valor en dólares, el modelo calcula un límite inferior (Floor) y un límite superior (Ceiling):

#### 1. Límite Inferior (Floor - Incurred Inefficiency Cost)
Calcula el costo contable directo que paga el operador por mantener esa capacidad ociosa (OPEX de energía consumida por el factor PUE + amortización anualizada del CAPEX asignado a esa potencia):

$$\text{OPEX}_{energía} = kW_{stranded, mid} \times 8760 \text{ hrs/año} \times PUE_{ref} \times C_{elec}$$

$$\text{CAPEX}_{amortizado} = \frac{kW_{stranded, mid} \times (\text{CAPEX}_{per\_MW} / 1000)}{T_{life}}$$

$$\text{Loss}_{min} = \text{OPEX}_{energía} + \text{CAPEX}_{amortizado}$$

#### 2. Límite Superior (Ceiling - Colocation Opportunity Cost)
Calcula el costo de oportunidad del mercado: lo que el operador deja de ingresar si hubiera alquilado esa capacidad ociosa en el mercado de Colocation a la tarifa promedio de $\$184 \text{ USD/kW/mes}$:

$$\text{Loss}_{max} = kW_{stranded, mid} \times R_{colo} \times 12 \text{ meses}$$

#### 3. Estimación Media (Mid)
$$\text{Loss}_{mid} = \frac{\text{Loss}_{min} + \text{Loss}_{max}}{2}$$

---

### C. Valor Recuperable y Tiempo de Retorno de Inversión (ROI)

- **Valor Recuperable Potencial ($USD$)**:
$$\text{Valor Recuperable} = \text{Loss}_{mid} \times 0.80$$

- **Tiempo Estimado de Recuperación (Meses)**:
$$\text{Costo Total Remediación} = MW_{facility} \times \$75,000 \text{ USD/MW}$$

$$\text{Meses ROI}_{mid} = \left( \frac{\text{Costo Total Remediación}}{\text{Valor Recuperable}} \right) \times 12 \text{ meses}$$

---

## 4. Bibliografía y Fuentes Citadas

1. **Sankar, S., & Vaid, K. (2010)**. *Trace-Driven Analysis of Data Center Power & Provisioning*. Microsoft Global Foundation Services (GFS).  
   *Aporte*: Establece el techo empírico del 13% de sobre-provisión de capacidad por la gestión de cargas pico sin monitoreo en tiempo real.
2. **Supermicro (2025)**. *Green Computing Benchmark & Direct-to-Chip Liquid Cooling Whitepaper*.  
   *Aporte*: Demuestra la reducción de PUE a 1.08 y la eliminación del consumo eléctrico de ventiladores de nodo (hasta 16% de ahorro de energía).
3. **Uptime Institute (2024)**. *Global Data Center Survey Results*.  
   *Aporte*: Proporciona la media de PUE de la industria (1.58) y métricas de utilización promedio.
4. **U.S. Energy Information Administration (EIA) (2026)**. *Electric Power Monthly - Commercial Sector Energy Pricing*.  
   *Aporte*: Justifica la tarifa base de $0.12 USD/kWh para centros de datos en EE.UU.
5. **Nlyte Software & Data Center Market Index (2025/2026)**. *Enterprise Colocation Pricing Report*.  
   *Aporte*: Define la tarifa promedio de arrendamiento de potencia en colocation de alta densidad ($184 USD/kW/mes).
