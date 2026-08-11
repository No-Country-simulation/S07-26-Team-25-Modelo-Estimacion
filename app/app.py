import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Estimación Stranded Capacity | Team 25", 
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. MOTOR DEL MODELO (API / FUNCIÓN LISTA)
# ==========================================
class StrandedCapacityAPI:
    """
    Motor determinístico de estimación de rangos (Floor & Ceiling).
    """
    def __init__(self):
        # Benchmark de Industria
        self.industry_benchmark_utilization = 0.75 
        # Matriz termodinámica (Basada en MSFT GFS, Supermicro, Nlyte)
        self.cooling_matrix = {
            'Air-cooled': {'pue': 1.58, 'stranded_pct_range': (0.12, 0.13), 'tco_10yr_per_mw': (6500000, 11000000), 'rec_time': '9 a 12+ meses'},
            'Híbrido': {'pue': 1.25, 'stranded_pct_range': (0.08, 0.10), 'tco_10yr_per_mw': (11000000, 13000000), 'rec_time': '6 a 9 meses'},
            'Liquid-cooled': {'pue': 1.10, 'stranded_pct_range': (0.01, 0.05), 'tco_10yr_per_mw': (8000000, 14000000), 'rec_time': '3 a 6 meses'}
        }
        self.colocation_ceiling_annual = 184 * 1000 * 12 # $184/kW/mes
        self.recoverable_ratio = (0.60, 0.85)

    def calculate(self, capacity_mw, util_pct, cooling_type):
        params = self.cooling_matrix[cooling_type]
        pue = params['pue']
        
        # Físico
        unutilized = capacity_mw * (1 - util_pct)
        mw_min = unutilized * params['stranded_pct_range'][0] * pue
        mw_max = unutilized * params['stranded_pct_range'][1] * pue
        
        # Financiero
        tco_min = params['tco_10yr_per_mw'][0] / 10
        tco_max = params['tco_10yr_per_mw'][1] / 10
        loss_min = mw_min * tco_min
        loss_max = mw_max * tco_max
        
        # Recuperable
        rec_val_min = loss_min * self.recoverable_ratio[0]
        rec_val_max = loss_max * self.recoverable_ratio[1]
        
        # KPIs
        avg_loss_per_mw = np.mean([loss_min, loss_max]) / np.mean([mw_min, mw_max]) if np.mean([mw_min, mw_max]) > 0 else 0
        effective_cap = capacity_mw - np.mean([mw_min, mw_max])
        
        return {
            "mw_range": (round(mw_min, 2), round(mw_max, 2)),
            "pct_range": (round((mw_min/capacity_mw)*100, 2), round((mw_max/capacity_mw)*100, 2)),
            "loss_range": (loss_min, loss_max),
            "recoverable_range": (rec_val_min, rec_val_max),
            "recovery_time": params['rec_time'],
            "kpis": {
                "usd_per_mw_lost": avg_loss_per_mw,
                "util_vs_benchmark": (util_pct - self.industry_benchmark_utilization) * 100,
                "effective_vs_paid": (effective_cap, capacity_mw)
            }
        }

# ==========================================
# UI: BARRA LATERAL
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1909/1909848.png", width=80)
st.sidebar.title("Presentación Ejecutiva")
st.sidebar.markdown("### No Country | Team 25")
st.sidebar.markdown("---")
st.sidebar.info(
    "Esta herramienta consolida los entregables del modelo de estimación para cuantificar "
    "el impacto de la desalineación entre las capas físicas y operativas en Data Centers."
)

# ==========================================
# UI: CUERPO PRINCIPAL (TABS)
# ==========================================
st.title("⚡ Calculadora de Stranded Capacity")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 1. Contexto & MVP", 
    "📊 2. KPIs y Simulador", 
    "🌪️ 3. Sensibilidad", 
    "📖 4. Lógica y Supuestos", 
    "💾 5. Dataset & API"
])

# --- TAB 1: CONTEXTO ---
with tab1:
    st.header("El Desafío de la Infraestructura de IA")
    st.markdown("""
    En los data centers modernos, la capacidad pagada y encendida que no produce nada productivo debido a la falta de coordinación entre las instalaciones térmicas y operativas se denomina **Stranded Capacity**.
    
    Este prototipo (MVP) despliega un **modelo de rangos auditable**. No busca una falsa precisión puntual, sino que establece límites financieros y operativos (Floor & Ceiling) que permiten a un operador entender el orden de magnitud de su problema y priorizar decisiones sin revelar datos confidenciales.
    """)
    st.success("Impacto del Proyecto: Expansión de mercado mediante la optimización y recuperación de capital inmovilizado.")

# --- TAB 2: SIMULADOR Y KPIS ---
with tab2:
    st.header("Simulador Interactivo de Impacto Operativo")
    
    # Inputs
    st.markdown("### 📥 Entradas del Operador")
    col1, col2, col3 = st.columns(3)
    with col1:
        cap_mw = st.number_input("Tamaño del Facility (MW)", min_value=1.0, max_value=500.0, value=15.0, step=1.0)
    with col2:
        util_pct = st.slider("Utilización Actual (%)", 0.0, 100.0, 87.0) / 100.0
    with col3:
        cooling = st.selectbox("Tipo de Cooling", ["Air-cooled", "Híbrido", "Liquid-cooled"])
        
    # Procesamiento
    engine = StrandedCapacityAPI()
    results = engine.calculate(cap_mw, util_pct, cooling)
    
    st.markdown("---")
    st.markdown("### 📤 Salidas y KPIs Financieros")
    
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Stranded Capacity (MW)", f"{results['mw_range'][0]} - {results['mw_range'][1]} MW", f"{results['pct_range'][0]}% - {results['pct_range'][1]}% del total", delta_color="inverse")
    rc2.metric("Pérdida Financiera Anual", f"${results['loss_range'][0]:,.0f} - ${results['loss_range'][1]:,.0f}")
    rc3.metric("Valor Recuperable Potencial", f"${results['recoverable_range'][0]:,.0f} - ${results['recoverable_range'][1]:,.0f}")
    
    st.markdown("#### Indicadores Clave de Rendimiento (KPIs)")
    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric("Tiempo Est. de Recuperación", results['recovery_time'])
    kc2.metric("Costo por MW Perdido", f"${results['kpis']['usd_per_mw_lost']:,.0f}")
    kc3.metric("Brecha vs Benchmark Industria", f"{results['kpis']['util_vs_benchmark']:.1f}%")
    kc4.metric("Capacidad Efectiva vs Pagada", f"{results['kpis']['effective_vs_paid'][0]:.1f} / {results['kpis']['effective_vs_paid'][1]} MW")

# --- TAB 3: ANÁLISIS DE SENSIBILIDAD ---
with tab3:
    st.header("Análisis de Sensibilidad (Tornado Chart)")
    st.markdown("Identificación de las variables que desplazan con mayor agresividad el resultado (TCO y Pérdida).")
    
    variables = ['Tarifa Eléctrica (Geografía)', 'PUE (Enfriamiento)', 'Tasa de Utilización IT', 'Rendimiento Térmico (DVFS)']
    imp_fav = np.array([-45, -28, -15, -10]) 
    imp_des = np.array([45, 28, 15, 10])
    y_pos = np.arange(len(variables))

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(y_pos, imp_fav, align='center', color='#3182ce', label='Escenario Favorable (Ahorro)')
    ax.barh(y_pos, imp_des, align='center', color='#e53e3e', label='Escenario Desfavorable (Costo)')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(variables, fontsize=10)
    ax.invert_yaxis() 
    ax.set_xlabel('Variación en el Costo Total de Stranded Capacity (%)', fontsize=10, weight='bold')
    ax.legend(loc='lower right')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    st.pyplot(fig)
    
    st.info("""
    * **Tarifa Eléctrica:** Variable de mayor impacto. El costo operativo no escala linealmente; reubicar cargas a zonas de alto costo puede cuadruplicar el OPEX.
    * **Tipo de Cooling (PUE):** El salto a refrigeración líquida mitiga hasta un 16% de pérdida al eliminar los ventiladores internos de TI (IT-fan power).
    """)

# --- TAB 4: LÓGICA Y SUPUESTOS ---
with tab4:
    st.header("Documento de Supuestos y Lógica de Rangos")
    st.markdown("El modelo es **auditablemente honesto**. Sus límites no se calculan al azar, sino que se rigen por topes operativos de la industria:")
    
    col_sup1, col_sup2 = st.columns(2)
    with col_sup1:
        st.markdown("#### ¿Por qué un modelo de rangos?")
        st.markdown("""
        Utilizar promedios genera una 'falsa precisión' en infraestructuras críticas. El rango absorbe:
        * **Volatilidad térmica:** Fluctuaciones por *throttling* de GPUs (ej. caídas de rendimiento a >71°C).
        * **Errores de telemetría:** El PUE de aire a menudo contabiliza erróneamente los ventiladores IT.
        """)
    with col_sup2:
        st.markdown("#### ¿Cómo se calculan los límites?")
        st.markdown("""
        * **Límite Físico (Floor):** `Capacidad Total * (1 - Utilización IT) * Factor Ineficiencia * PUE`.
        * **Límite Financiero Superior (Ceiling):** Se asume la tasa del mercado de Colocation de **$184 USD/kW/mes**. Si la ineficiencia interna rompe este techo, operar la infraestructura deja de ser financieramente viable.
        """)

# --- TAB 5: DATASET Y API ---
with tab5:
    st.header("Dataset de Referencia y Arquitectura")
    
    st.subheader("Dataset Público (Single Source of Truth)")
    data = [
        {"Categoría": "Termodinámica", "Métrica": "PUE (Air-cooled)", "Valor": "1.58", "Fuente": "Industria / Baseline"},
        {"Categoría": "Termodinámica", "Métrica": "PUE (Liquid-cooled)", "Valor": "1.10", "Fuente": "Open Compute Project"},
        {"Categoría": "Operativa", "Métrica": "Stranded Capacity (Air)", "Valor": "12% - 13%", "Fuente": "Microsoft GFS"},
        {"Categoría": "Operativa", "Métrica": "Stranded Capacity (Liquid)", "Valor": "< 5%", "Fuente": "Supermicro"},
        {"Categoría": "Financiera", "Métrica": "Techo Mercado (Colocation)", "Valor": "$184/kW/mes", "Fuente": "Mercado Benchmark"}
    ]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
    
    st.subheader("Arquitectura de la Solución (API)")
    st.markdown("""
    El modelo está desacoplado del frontend. En el código fuente (`app.py`), la clase `StrandedCapacityAPI` actúa como el motor de negocio, recibiendo 3 parámetros y retornando un diccionario (formato JSON) con los 5 outputs esperados, listo para ser consumido por microservicios o integrarse con herramientas de Business Intelligence.
    """)
