import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Calculadora Stranded Capacity", layout="wide")

st.title("⚡ Calculadora de Stranded Capacity en Data Centers")

st.sidebar.header("📥 Inputs del Operador")
facility_mw = st.sidebar.number_input("Tamaño del Facility (MW)", min_value=0.1, value=10.0)
utilization_pct = st.sidebar.slider("Utilización actual (%)", 0.0, 100.0, 60.0)
cooling_type = st.sidebar.selectbox("Tipo de Cooling", ["air-cooled", "liquid-cooled", "hybrid"])

# ==========================================
# CONEXIÓN A LA API (FastAPI)
# ==========================================
API_URL = "http://127.0.0.1:8000/api/v1/calculate"

if st.sidebar.button("Calcular con la API"):
    payload = {
        "facility_mw": facility_mw,
        "utilization_pct": utilization_pct,
        "cooling_type": cooling_type
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status() 
        data = response.json()
        
        # 1. EXTRACCIÓN COMPLETA DEL JSON
        mw_mid = data["stranded_capacity_mw_range"]["mid"]
        pct_mid = data["stranded_capacity_pct_range"]["mid"]
        
        loss_min = data["annual_financial_loss_usd"]["min_usd_annual"]
        loss_mid = data["annual_financial_loss_usd"]["mid_usd_annual"]
        loss_max = data["annual_financial_loss_usd"]["max_usd_annual"]
        
        recoverable = data["potential_recoverable_value_usd"]
        
        # Aquí extraemos los datos que faltaban mostrar
        recovery_months = data["estimated_recovery_time_months"]["mid_months"]
        kpis = data["kpis"]
        assumptions = data["assumptions_summary"]
        
        # ==========================================
        # VISUALIZACIÓN DE RESULTADOS
        # ==========================================
        st.markdown("### 📊 Resultados de la Estimación")
        
        # Fila 1: Métricas Principales (Tarjetas superiores)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("⚠️ Stranded Capacity (Media)", f"{mw_mid} MW", f"{pct_mid}% del facility")
            
        with col2:
            st.metric("💸 Pérdida Media Anual", f"${loss_mid:,.0f} USD", f"Rango: ${loss_min:,.0f} - ${loss_max:,.0f}")
            
        with col3:
            st.metric("🚀 Valor Recuperable", f"${recoverable:,.0f} USD")
            
        st.markdown("---")
        
        # Fila 2: Tabla de KPIs y Criterios Técnicos (Donde está el tiempo)
        col4, col5 = st.columns(2)
        
        with col4:
            st.subheader("📈 Análisis de Capacidad y KPIs")
            kpi_table = {
                "Métrica KPI": [
                    "Capacidad Pagada Total",
                    "Capacidad Efectiva Real (TI)",
                    "Costo Anual Promedio por MW Perdido",
                    "Utilización Actual vs Benchmark"
                ],
                "Valor": [
                    f"{kpis['paid_capacity_mw']} MW",
                    f"{kpis['effective_capacity_mw']} MW",
                    f"${kpis['usd_per_lost_mw']:,.2f} USD/MW",
                    f"{kpis['current_utilization_pct']}% vs Benchmark: {kpis['industry_benchmark_utilization_pct']}%"
                ]
            }
            st.table(pd.DataFrame(kpi_table))
            
        with col5:
            st.subheader("📋 Criterios Técnicos y Tiempos")
            st.write(f"**Arquitectura base:** `{assumptions['cooling_type']}`")
            st.write(f"* **PUE de Referencia:** {assumptions['pue_reference']}")
            st.write(f"* **CCF Típico:** {assumptions['ccf_typical']}")
            
            # --- LÍNEA NUEVA PARA MOSTRAR LA FÓRMULA ---
            st.write(f"* **Cálculo Financiero Base:** {assumptions.get('financial_floor_formula', 'N/A')}")
            
            # Aquí se imprime el tiempo de recuperación extraído de la API
            st.success(f"⏱️ **Tiempo estimado de recuperación (ROI):** ~{recovery_months} meses")
            
    except requests.exceptions.ConnectionError:
        st.error("🚨 Error de conexión: Asegúrate de que el servidor de FastAPI esté corriendo en la otra terminal.")