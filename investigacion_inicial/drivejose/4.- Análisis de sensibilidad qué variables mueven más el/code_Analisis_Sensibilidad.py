import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def mostrar_analisis_sensibilidad():
    st.markdown("### Análisis de Sensibilidad: Variables Críticas")
    st.write("El siguiente gráfico de Tornado ilustra el impacto porcentual de cada variable en el costo total de la capacidad varada, comparando escenarios favorables (ahorro) vs desfavorables (costo).")
    
    # Definición de variables y su impacto
    variables = [
        'Tarifa Eléctrica (Nlyte / Geografía)', 
        'PUE (Tecnología de Enfriamiento)', 
        'Tasa de Utilización IT (Microsoft GFS)', 
        'Rendimiento Térmico (Supermicro / DVFS)'
    ]

    impacto_favorable = np.array([-45, -28, -15, -10]) 
    impacto_desfavorable = np.array([45, 28, 15, 10])

    y_pos = np.arange(len(variables))

    # Crear la figura
    fig, ax = plt.subplots(figsize=(10, 6))

    # Dibujar barras
    ax.barh(y_pos, impacto_favorable, align='center', color='#3182ce', label='Escenario Favorable (Ahorro)')
    ax.barh(y_pos, impacto_desfavorable, align='center', color='#e53e3e', label='Escenario Desfavorable (Costo)')

    # Formato
    ax.set_yticks(y_pos)
    ax.set_yticklabels(variables, fontsize=11, weight='medium')
    ax.invert_yaxis()  # Mayor impacto arriba
    ax.set_xlabel('Variación en el Costo Total de Stranded Capacity (%)', fontsize=12, weight='bold')
    ax.legend(loc='lower right')
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    # Etiquetas de datos
    for i, v in enumerate(impacto_favorable):
        ax.text(v - 2, i, f"{v}%", va='center', ha='right', fontsize=10, color='#2d3748')
    for i, v in enumerate(impacto_desfavorable):
        ax.text(v + 2, i, f"+{v}%", va='center', ha='left', fontsize=10, color='#2d3748')

    # Ajustar márgenes
    plt.tight_layout()

    # Mostrar en Streamlit
    st.pyplot(fig)

    # Resumen Ejecutivo debajo del gráfico
    with st.expander("Ver Resumen Ejecutivo (Justificación)"):
        st.markdown("""
        * **Tarifa Eléctrica:** El costo operativo puede cuadruplicarse dependiendo de la geografía, pasando de regiones de bajo costo a alto costo.
        * **Tecnología de Enfriamiento:** Pasar a refrigeración líquida elimina los ventiladores IT, reduciendo el consumo a nivel nodo hasta en un 16%.
        * **Utilización IT:** Una sobre-provisión no detectada puede inmovilizar hasta un 13% del CAPEX en hardware sin uso.
        * **Rendimiento Térmico:** El estrangulamiento térmico (*throttling*) degrada el rendimiento computacional obligando a consumir más energía para la misma carga.
        """)

# Para mandar a llamar la función en tu app, simplemente usa:
# mostrar_analisis_sensibilidad()