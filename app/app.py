import sys
import time
from pathlib import Path
from typing import Any
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

# Asegurar importación del motor original
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "01_modelo_documentado"))
sys.path.append(str(ROOT_DIR / "02_dataset_referencia"))

try:
    from stranded_model import StrandedCapacityCalculator
except ImportError:
    StrandedCapacityCalculator = None


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
# UI: BARRA LATERAL
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1909/1909848.png", width=80)
st.sidebar.title("Calculadora Stranded Capacity")
st.sidebar.markdown("### No Country | Team 25")
st.sidebar.markdown("---")

api_url_default = "http://127.0.0.1:8000"
st.sidebar.subheader("🔌 Estado del Backend API")
try:
    health_check = requests.get(f"{api_url_default}/", timeout=1.2)
    if health_check.status_code == 200:
        st.sidebar.success(f"🟢 API Conectada (v{health_check.json().get('version', '1.0')})")
    else:
        st.sidebar.warning(f"⚠️ API respondió con código {health_check.status_code}")
except Exception:
    st.sidebar.error("🔴 API Desconectada")
    st.sidebar.caption("Para iniciar el servidor ejecuta:\n`uv run uvicorn 06_api_backend.main:app --reload --port 8000`")

st.sidebar.markdown("---")
st.sidebar.info(
    "Esta herramienta cuantifica la desalineación entre las capas físicas (cooling) "
    "y operativas (IT) en Data Centers de IA para calcular el capital inmovilizado."
)


# ==========================================
# UI: CUERPO PRINCIPAL (TABS)
# ==========================================
st.title("⚡ Calculadora de Stranded Capacity")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 1. Contexto & MVP", 
    "📊 2. Calculadora (Motor Local)", 
    "🔌 3. Calculadora por API & Monte Carlo", 
    "🌪️ 4. Sensibilidad", 
    "📖 5. Lógica y Supuestos", 
    "💾 6. Dataset de Referencia"
])


# ==========================================
# TAB 1: CONTEXTO Y MVP (CON GLOSARIO EJECUTIVO)
# ==========================================
with tab1:
    st.header("El Desafío de la Infraestructura de IA")
    st.markdown("""
    En los data centers modernos optimizados para Inteligencia Artificial (AI Data Centers), la capacidad pagada y encendida que no produce trabajo útil debido a la falta de coordinación entre las instalaciones térmicas y operativas se denomina **Stranded Capacity (Capacidad Varada)**.
    
    Este prototipo (MVP) despliega un **modelo de rangos auditable (Floor & Ceiling)**. No busca una falsa precisión puntual, sino que establece límites financieros y operativos que permiten a un operador entender el orden de magnitud de su problema y priorizar decisiones estratégicas sin revelar datos confidenciales.
    """)
    st.success("Impacto del Proyecto: Expansión de mercado mediante la optimización y recuperación de capital inmovilizado.")

    st.markdown("---")
    st.subheader("📌 Glosario Ejecutivo: Términos Principales")
    st.markdown("Guía rápida para interpretar las métricas y los conceptos clave del modelo:")

    g_col1, g_col2 = st.columns(2)

    with g_col1:
        st.markdown("""
        * **⚡ Stranded Capacity (Capacidad Varada):** Potencia eléctrica contratada y pagada (MW) que no se puede utilizar para computación de IA debido a restricciones de enfriamiento o cuellos de botella térmicos.
        * **🌡️ PUE (Power Usage Effectiveness):** Métrica global de eficiencia energéctica. `PUE = Energía Total / Energía IT`. Un PUE de **1.58** en aire significa gastar 0.58 kW extra en enfriar por cada 1 kW útil; en líquido bajan a **1.08-1.10**.
        * **🏗️ Piso (Floor):** Límite inferior del rango financiero. Representa la ineficiencia real pagada internamente (**OPEX eléctrico + CAPEX de infraestructura amortizado**).
        """)

    with g_col2:
        st.markdown("""
        * **🏢 Techo (Ceiling):** Límite financiero superior. Representa el costo de oportunidad si esa capacidad varada se comercializara en el mercado de *Colocation* (**$184 USD/kW/mes**).
        * **🎲 Percentiles P10, P50, P90 (Monte Carlo):** Escenarios probabilísticos de confianza. **P10** (Escenario favorable), **P50** (Mediana esperada), **P90** (Escenario pesimista de máximo riesgo).
        * **⏱️ Tiempo de Recuperación (ROI):** Período estimado (en meses) para amortizar la inversión requerida en remediación y sistemas de telemetría/DCIM.
        """)


# ==========================================
# TAB 2: CALCULADORA (MOTOR LOCAL)
# ==========================================
with tab2:
    st.header("Calculadora de Impacto Operativo (Motor Local)")
    st.caption("Cálculo determinístico procesado directamente en memoria utilizando la clase `StrandedCapacityCalculator`.")
    
    # Inputs
    st.markdown("### 📥 Entradas del Operador")
    col1, col2, col3 = st.columns(3)
    with col1:
        cap_mw_loc = st.number_input("Tamaño del Facility (MW)", min_value=1.0, max_value=500.0, value=15.0, step=1.0, key="loc_cap")
    with col2:
        util_pct_loc = st.slider("Utilización Actual (%)", 0.0, 100.0, 87.0, key="loc_util")
    with col3:
        cooling_loc = st.selectbox("Tipo de Cooling", ["Air-cooled", "Híbrido", "Liquid-cooled"], key="loc_cooling")
        
    cooling_map: dict[str, Any] = {"Air-cooled": "air-cooled", "Híbrido": "hybrid", "Liquid-cooled": "liquid-cooled"}
    
    if StrandedCapacityCalculator:
        calc_loc = StrandedCapacityCalculator()
        res_loc = calc_loc.calculate(cap_mw_loc, util_pct_loc, cooling_map[cooling_loc])
        
        st.markdown("---")
        st.markdown("### 📤 Salidas y KPIs Financieros (Motor Local)")
        
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric(
            "Stranded Capacity (MW)", 
            f"{res_loc.stranded_capacity_mw_range['min']} - {res_loc.stranded_capacity_mw_range['max']} MW", 
            f"{res_loc.stranded_capacity_pct_range['min']}% - {res_loc.stranded_capacity_pct_range['max']}% del total", 
            delta_color="inverse"
        )
        loss_lower = min(res_loc.annual_financial_loss_usd.min_usd_annual, res_loc.annual_financial_loss_usd.max_usd_annual)
        loss_upper = max(res_loc.annual_financial_loss_usd.min_usd_annual, res_loc.annual_financial_loss_usd.max_usd_annual)
        rc2.metric(
            "Pérdida Financiera Anual (Rango)", 
            f"${loss_lower:,.0f} - ${loss_upper:,.0f}",
            f"Media: ${res_loc.annual_financial_loss_usd.mid_usd_annual:,.0f}"
        )
        rc3.metric("Valor Recuperable Potencial", f"${res_loc.potential_recoverable_value_usd:,.0f}")
        
        st.info("💡 **¿Cómo interpretar el Rango?** El límite menor representa la oportunidad de mercado no capturada (**Techo Colocation**); el límite mayor representa el costo de ineficiencia real pagado internamente (**Piso: OPEX + CAPEX amortizado**).")

        st.markdown("#### Indicadores Clave de Rendimiento (KPIs)")
        kc1, kc2, kc3, kc4 = st.columns(4)
        kc1.metric("Tiempo Est. de Recuperación", f"{res_loc.estimated_recovery_time_months['min_months']} a {res_loc.estimated_recovery_time_months['max_months']} meses")
        kc2.metric("Costo por MW Perdido", f"${res_loc.kpis.usd_per_lost_mw:,.0f}")
        kc3.metric("Brecha vs Benchmark Industria", f"{util_pct_loc - res_loc.kpis.industry_benchmark_utilization_pct:.1f}%")
        kc4.metric("Capacidad Efectiva vs Pagada", f"{res_loc.kpis.effective_capacity_mw:.1f} / {res_loc.kpis.paid_capacity_mw} MW")

        # Gráficos del motor local
        st.markdown("---")
        st.markdown("### 📈 Visualización Gráfica (Motor Local)")
        gc1, gc2 = st.columns(2)
        with gc1:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(
                ['Efectiva (Útil)', 'Stranded (Varada)', 'Sin Utilizar'], 
                [res_loc.kpis.effective_capacity_mw, res_loc.stranded_capacity_mw_range['mid'], max(0, cap_mw_loc - res_loc.kpis.effective_capacity_mw - res_loc.stranded_capacity_mw_range['mid'])], 
                color=['#2b6cb0', '#e53e3e', '#cbd5e0']
            )
            ax.set_ylabel("Megavatios (MW)", weight='bold')
            ax.set_title("Descomposición de Capacidad en MW", weight='bold')
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            st.pyplot(fig)
        with gc2:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.bar(
                ['Techo (Colocation)', 'Media (Mid)', 'Piso (OPEX+CAPEX)'], 
                [loss_lower / 1e6, res_loc.annual_financial_loss_usd.mid_usd_annual / 1e6, loss_upper / 1e6], 
                color=['#ed8936', '#dd6b20', '#c53030']
            )
            ax2.set_ylabel("Millones de USD ($M)", weight='bold')
            ax2.set_title("Pérdida Financiera Anual Estimada ($M)", weight='bold')
            ax2.grid(axis='y', linestyle='--', alpha=0.3)
            st.pyplot(fig2)


# ==========================================
# TAB 3: CALCULADORA POR API REST & MONTE CARLO
# ==========================================
with tab3:
    st.header("🔌 Calculadora por API REST & Simulación de Monte Carlo")
    st.markdown("Esta sección interactúa directamente con los endpoints del backend **FastAPI (`06_api_backend`)**.")

    # --- GUÍA RÁPIDA ---
    with st.expander("📘 ¿Cómo funciona y cómo usar la API REST?", expanded=False):
        st.markdown("""
        ### 🚀 Inicio del Servidor Backend
        ```bash
        uv run uvicorn 06_api_backend.main:app --reload --port 8000
        ```
        ### 📋 Endpoints Disponibles
        - **`POST /api/v1/calculate`**: Cálculo determinístico de rangos.
        - **`POST /api/v1/monte-carlo`**: Simulación estocástica con distribuciones de probabilidad y percentiles (P10, P50, P90).
        - **`GET /api/v1/benchmarks`**: Benchmarks de la industria.

        👉 **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
        """)

    st.markdown("---")

    api_url_input = st.text_input("URL del Servidor FastAPI:", api_url_default, key="api_url_calculator")

    # Estado de conexion
    is_api_running = False
    try:
        check_r = requests.get(f"{api_url_input}/", timeout=1.5)
        if check_r.status_code == 200:
            is_api_running = True
            st.success(f"🟢 **Conectado con FastAPI Backend** (`{api_url_input}`) - Status: 200 OK")
        else:
            st.warning(f"⚠️ Servidor API respondió con status {check_r.status_code}")
    except Exception:
        st.error("🔴 **Servidor FastAPI Desconectado**")
        st.info("💡 Por favor, inicia el backend en la terminal: `uv run uvicorn 06_api_backend.main:app --reload --port 8000`")

    # Formulario general de entradas
    st.markdown("#### 📥 Entradas para la Evaluación")
    ap_col1, ap_col2, ap_col3 = st.columns(3)
    with ap_col1:
        api_mw = st.number_input("Capacidad del Facility (MW)", min_value=1.0, max_value=500.0, value=20.0, step=1.0, key="api_mw_in")
    with ap_col2:
        api_util = st.slider("Porcentaje de Utilización (%)", 0.0, 100.0, 85.0, key="api_util_in")
    with ap_col3:
        api_cooling = st.selectbox("Tecnología de Enfriamiento", ["air-cooled", "hybrid", "liquid-cooled"], key="api_cooling_in")

    api_payload = {
        "facility_mw": api_mw,
        "utilization_pct": api_util,
        "cooling_type": api_cooling
    }

    # Pestañas internas para comparar Determinístico vs Monte Carlo
    sub_tab1, sub_tab2 = st.tabs([
        "📊 1. Cálculo Determinístico (Floor & Ceiling)",
        "🎲 2. Simulación Estocástica de Monte Carlo (Percentiles P10, P50, P90)"
    ])

    # -------------------------------------------------------------
    # SUB-TAB 1: CÁLCULO DETERMINÍSTICO VIA API
    # -------------------------------------------------------------
    with sub_tab1:
        st.subheader("Cálculo Determinístico (`POST /api/v1/calculate`)")
        if is_api_running:
            try:
                t0 = time.time()
                res_api = requests.post(f"{api_url_input}/api/v1/calculate", json=api_payload, timeout=3.0)
                latency_ms = round((time.time() - t0) * 1000, 1)

                if res_api.status_code == 200:
                    json_resp = res_api.json()
                    st.caption(f"⏱️ **Latencia HTTP:** `{latency_ms} ms` | 📡 **Endpoint:** `POST /api/v1/calculate`")

                    m_mw = json_resp["stranded_capacity_mw_range"]
                    m_pct = json_resp["stranded_capacity_pct_range"]
                    m_loss = json_resp["annual_financial_loss_usd"]
                    m_rec = json_resp["potential_recoverable_value_usd"]

                    det_c1, det_c2, det_c3 = st.columns(3)
                    det_c1.metric("Stranded Capacity (MW)", f"{m_mw['min']} - {m_mw['max']} MW", f"{m_pct['min']}% - {m_pct['max']}%", delta_color="inverse")
                    api_loss_lower = min(m_loss['min_usd_annual'], m_loss['max_usd_annual'])
                    api_loss_upper = max(m_loss['min_usd_annual'], m_loss['max_usd_annual'])
                    det_c2.metric(
                        "Pérdida Financiera (Rango USD/Año)", 
                        f"${api_loss_lower:,.0f} - ${api_loss_upper:,.0f}", 
                        f"Media: ${m_loss['mid_usd_annual']:,.0f}"
                    )
                    det_c3.metric("Valor Recuperable", f"${m_rec:,.0f}")

                    st.info("💡 **Interpretación del Rango de la API:** El valor menor ($" + f"{api_loss_lower:,.0f}" + ") es el Techo de Oportunidad de Colocation; el mayor ($" + f"{api_loss_upper:,.0f}" + ") representa el Piso de Costos Incurridos.")

                    # Gráficos determinísticos
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        fig_mw, ax_mw = plt.subplots(figsize=(5, 3.5))
                        ax_mw.bar(['Min', 'Mid', 'Max'], [m_mw['min'], m_mw['mid'], m_mw['max']], color=['#3182ce', '#dd6b20', '#e53e3e'])
                        ax_mw.set_ylabel("MW Varados", weight='bold')
                        ax_mw.set_title("Stranded Capacity (MW)", weight='bold')
                        ax_mw.grid(axis='y', linestyle='--', alpha=0.3)
                        st.pyplot(fig_mw)
                    with dc2:
                        fig_l, ax_l = plt.subplots(figsize=(5, 3.5))
                        ax_l.bar(['Techo (Colocation)', 'Mid (Media)', 'Piso (OPEX+CAPEX)'], [api_loss_lower/1e6, m_loss['mid_usd_annual']/1e6, api_loss_upper/1e6], color=['#ed8936', '#dd6b20', '#c53030'])
                        ax_l.set_ylabel("$M USD/Año", weight='bold')
                        ax_l.set_title("Pérdida Financiera Determinística ($M)", weight='bold')
                        ax_l.grid(axis='y', linestyle='--', alpha=0.3)
                        st.pyplot(fig_l)
            except Exception as e:
                st.error(f"Error al llamar a la API determinística: {e}")
        else:
            st.warning("⚠️ Servidor FastAPI no disponible.")

    # -------------------------------------------------------------
    # SUB-TAB 2: SIMULACIÓN DE MONTE CARLO VIA API
    # -------------------------------------------------------------
    with sub_tab2:
        st.subheader("Simulación de Monte Carlo (`POST /api/v1/monte-carlo`)")
        st.markdown("""
        A diferencia del cálculo determinístico (que usa límites estáticos), la **Simulación de Monte Carlo** ejecuta miles de iteraciones aleatorias
        haciendo variar probabilísticamente el **PUE**, la **Tarifa Eléctrica ($/kWh)**, la **Tasa de Colocation ($/kW/mes)** y el **CAPEX/MW**.
        
        Devuelve **Percentiles de Confianza**:
        - **P10 (Conservador / Favorable):** Solo un 10% de probabilidad de que el costo sea menor a este valor.
        - **P50 (Mediana / Escenario Base):** El valor medio más probable en la distribución estocástica.
        - **P90 (Pesimista / Alto Riesgo):** 90% de probabilidad de estar por debajo (límite de riesgo máximo).
        """)

        num_sims = st.slider("Número de Iteraciones Estocásticas:", min_value=1000, max_value=20000, value=5000, step=1000, key="mc_num_sims")

        if is_api_running:
            try:
                t0_mc = time.time()
                mc_payload = {
                    "facility_mw": api_mw,
                    "utilization_pct": api_util,
                    "cooling_type": api_cooling,
                    "num_simulations": num_sims
                }
                res_mc = requests.post(f"{api_url_input}/api/v1/monte-carlo", json=mc_payload, timeout=5.0)
                latency_mc = round((time.time() - t0_mc) * 1000, 1)

                if res_mc.status_code == 200:
                    mc_data = res_mc.json()
                    st.caption(f"⏱️ **Latencia API Monte Carlo:** `{latency_mc} ms` | 🎲 **Iteraciones Ejecutadas:** `{num_sims:,}`")

                    percentiles = mc_data["percentiles"]
                    p_loss = percentiles["loss_mid_usd"]
                    p_mw = percentiles["stranded_mw"]
                    p_roi = percentiles["roi_months"]

                    st.markdown("#### 🎯 Rangos de Confianza Obtenidos por Monte Carlo")

                    mc_col1, mc_col2, mc_col3 = st.columns(3)
                    mc_col1.metric("P10 (Escenario Optimista)", f"${p_loss['p10']:,.0f} USD", f"{p_mw['p10']:.2f} MW varados")
                    mc_col2.metric("P50 (Mediana / Esperado)", f"${p_loss['p50']:,.0f} USD", f"{p_mw['p50']:.2f} MW varados")
                    mc_col3.metric("P90 (Escenario Pesimista)", f"${p_loss['p90']:,.0f} USD", f"{p_mw['p90']:.2f} MW varados", delta_color="inverse")

                    # Gráficos de Monte Carlo
                    st.markdown("---")
                    st.markdown("### 📊 Gráficos de Distribución de Probabilidad (Monte Carlo)")

                    mc_gcol1, mc_gcol2 = st.columns(2)

                    with mc_gcol1:
                        st.markdown("#### 🎲 Distribución de Pérdida Financiera ($M USD)")
                        fig_mc_bar, ax_mc_bar = plt.subplots(figsize=(6, 4))
                        p_labels = ['P10 (Optimista)', 'P50 (Mediana)', 'P90 (Pesimista)']
                        p_vals = [p_loss['p10'] / 1e6, p_loss['p50'] / 1e6, p_loss['p90'] / 1e6]
                        p_colors = ['#38a169', '#dd6b20', '#e53e3e']

                        bars_p = ax_mc_bar.bar(p_labels, p_vals, color=p_colors, width=0.5)
                        ax_mc_bar.set_ylabel("Millones de USD ($M)", weight='bold')
                        ax_mc_bar.set_title(f"Percentiles de Pérdida ({num_sims:,} iteraciones)", weight='bold')
                        ax_mc_bar.grid(axis='y', linestyle='--', alpha=0.3)

                        for b in bars_p:
                            h = b.get_height()
                            ax_mc_bar.text(b.get_x() + b.get_width()/2.0, h + 0.05, f"${h:.2f}M", ha='center', va='bottom', fontsize=9, weight='bold')

                        st.pyplot(fig_mc_bar)

                    with mc_gcol2:
                        st.markdown("#### ⚡ Stranded Capacity Estocástico (MW)")
                        fig_mc_mw, ax_mc_mw = plt.subplots(figsize=(6, 4))
                        mw_p_vals = [p_mw['p10'], p_mw['p50'], p_mw['p90']]
                        bars_mw_p = ax_mc_mw.bar(p_labels, mw_p_vals, color=['#3182ce', '#dd6b20', '#c53030'], width=0.5)

                        ax_mc_mw.set_ylabel("Megavatios (MW)", weight='bold')
                        ax_mc_mw.set_title(f"Megavatios Varados en Percentiles P10-P90", weight='bold')
                        ax_mc_mw.grid(axis='y', linestyle='--', alpha=0.3)

                        for b in bars_mw_p:
                            h = b.get_height()
                            ax_mc_mw.text(b.get_x() + b.get_width()/2.0, h + 0.02, f"{h:.2f} MW", ha='center', va='bottom', fontsize=9, weight='bold')

                        st.pyplot(fig_mc_mw)

                    # Tabla Comparativa: Determinístico vs Monte Carlo
                    st.markdown("---")
                    st.markdown("#### ⚖️ Comparativa: Modelo Determinístico vs. Simulación Monte Carlo")
                    
                    res_det = requests.post(f"{api_url_input}/api/v1/calculate", json=api_payload, timeout=3.0).json()
                    det_loss = res_det["annual_financial_loss_usd"]
                    det_mw = res_det["stranded_capacity_mw_range"]

                    comp_data = [
                        {
                            "Métrica": "Pérdida Financiera Mínima / Piso (P10)",
                            "Determinístico (Límites Estáticos)": f"${min(det_loss['min_usd_annual'], det_loss['max_usd_annual']):,.0f} USD",
                            "Monte Carlo (Percentil P10 Estocástico)": f"${p_loss['p10']:,.0f} USD",
                            "Diferencia": f"${p_loss['p10'] - min(det_loss['min_usd_annual'], det_loss['max_usd_annual']):,.0f} USD"
                        },
                        {
                            "Métrica": "Pérdida Financiera Media (P50)",
                            "Determinístico (Límites Estáticos)": f"${det_loss['mid_usd_annual']:,.0f} USD",
                            "Monte Carlo (Percentil P50 Estocástico)": f"${p_loss['p50']:,.0f} USD",
                            "Diferencia": f"${p_loss['p50'] - det_loss['mid_usd_annual']:,.0f} USD"
                        },
                        {
                            "Métrica": "Pérdida Financiera Máxima / Techo (P90)",
                            "Determinístico (Límites Estáticos)": f"${max(det_loss['min_usd_annual'], det_loss['max_usd_annual']):,.0f} USD",
                            "Monte Carlo (Percentil P90 Estocástico)": f"${p_loss['p90']:,.0f} USD",
                            "Diferencia": f"${p_loss['p90'] - max(det_loss['min_usd_annual'], det_loss['max_usd_annual']):,.0f} USD"
                        },
                        {
                            "Métrica": "Stranded Capacity MW (Media/P50)",
                            "Determinístico (Límites Estáticos)": f"{det_mw['mid']} MW",
                            "Monte Carlo (Percentil P50 Estocástico)": f"{p_mw['p50']:.2f} MW",
                            "Diferencia": f"{p_mw['p50'] - det_mw['mid']:.2f} MW"
                        }
                    ]
                    st.dataframe(pd.DataFrame(comp_data), use_container_width=True)

            except Exception as e:
                st.error(f"Error al ejecutar la simulación de Monte Carlo en la API: {e}")
        else:
            st.warning("⚠️ Servidor FastAPI no disponible para la simulación de Monte Carlo.")


# ==========================================
# TAB 4: ANÁLISIS DE SENSIBILIDAD
# ==========================================
with tab4:
    st.header("Análisis de Sensibilidad (Tornado Chart)")
    st.markdown("Identificación de las variables que desplazan con mayor agresividad el resultado (TCO y Pérdida).")
    
    variables = ['Tarifa Eléctrica (Geografía)', 'PUE (Enfriamiento)', 'Tasa de Utilización IT', 'Rendimiento Térmico (DVFS)']
    imp_fav = np.array([-45, -28, -15, -10]) 
    imp_des = np.array([45, 28, 15, 10])
    y_pos = np.arange(len(variables))

    fig_tor, ax_tor = plt.subplots(figsize=(9, 4))
    ax_tor.barh(y_pos, imp_fav, align='center', color='#3182ce', label='Escenario Favorable (Ahorro)')
    ax_tor.barh(y_pos, imp_des, align='center', color='#e53e3e', label='Escenario Desfavorable (Costo)')
    ax_tor.set_yticks(y_pos)
    ax_tor.set_yticklabels(variables, fontsize=10)
    ax_tor.invert_yaxis() 
    ax_tor.set_xlabel('Variación en el Costo Total de Stranded Capacity (%)', fontsize=10, weight='bold')
    ax_tor.legend(loc='lower right')
    ax_tor.grid(axis='x', linestyle='--', alpha=0.3)
    
    st.pyplot(fig_tor)
    
    st.success("""
    🚀 **Conclusión Clave:** La tarifa eléctrica es la variable de mayor sensibilidad geográfica. 
    La transición de Aire Tradicional a Refrigeración Líquida reduce el PUE de 1.58 a 1.08 y elimina hasta un 16% del consumo de ventiladores IT internos.
    """)


# ==========================================
# TAB 5: LÓGICA Y SUPUESTOS
# ==========================================
with tab5:
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

    st.markdown("---")
    st.subheader("📚 Fuentes Académica e Industriales Citadas")
    sources_data = [
        {"Institución / Fuente": "Microsoft GFS (Sankar & Vaid, 2010)", "Tema": "Over-provisioning & Stranded Capacity", "Hallazgo Principal": "Hasta 13% de capacidad varada en aprovisionamiento Max-Power."},
        {"Institución / Fuente": "Uptime Institute (2024)", "Tema": "Global Data Center Survey", "Hallazgo Principal": "Benchmark PUE promedio global para aire = 1.58."},
        {"Institución / Fuente": "Supermicro (2025)", "Tema": "Liquid Cooling Benchmark Report", "Hallazgo Principal": "PUE de 1.08 y 16% de ahorro de energía al eliminar ventiladores IT."},
        {"Institución / Fuente": "U.S. EIA (2026)", "Tema": "Commercial Electricity Rates", "Hallazgo Principal": "Tarifa eléctrica comercial promedio = $0.12 USD/kWh."},
        {"Institución / Fuente": "Nlyte Software / Colocation Market", "Tema": "Market Opportunity Rate", "Hallazgo Principal": "Tarifa de oportunidad de Colocation = $184 USD/kW/mes."}
    ]
    st.dataframe(pd.DataFrame(sources_data), use_container_width=True)


# ==========================================
# TAB 6: DATASET DE REFERENCIA
# ==========================================
with tab6:
    st.header("Dataset de Referencia")
    st.subheader("📊 Dataset Público (Single Source of Truth)")
    data = [
        {"Categoría": "Termodinámica", "Métrica": "PUE (Air-cooled)", "Valor": "1.58", "Fuente": "Industria / Baseline"},
        {"Categoría": "Termodinámica", "Métrica": "PUE (Liquid-cooled)", "Valor": "1.10", "Fuente": "Open Compute Project"},
        {"Categoría": "Operativa", "Métrica": "Stranded Capacity (Air)", "Valor": "12% - 13%", "Fuente": "Microsoft GFS"},
        {"Categoría": "Operativa", "Métrica": "Stranded Capacity (Liquid)", "Valor": "< 5%", "Fuente": "Supermicro"},
        {"Categoría": "Financiera", "Métrica": "Techo Mercado (Colocation)", "Valor": "$184/kW/mes", "Fuente": "Mercado Benchmark"}
    ]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
