import pandas as pd
import numpy as np

# ==========================================
# 1. CONFIGURACIÓN Y LECTURA DE DATOS BASE
# ==========================================
# Semilla para que los resultados sean reproducibles si lo corres varias veces
np.random.seed(42)

# Cantidad de simulaciones a generar
NUM_RECORDS = 5000

print("Cargando benchmarks reales...")
try:
    # Leemos el archivo semilla que guardaste
    df_base = pd.read_csv('benchmarks_reales.csv')
except FileNotFoundError:
    print("Error: No se encontró el archivo 'benchmarks_reales.csv'. Asegúrate de que esté en la misma carpeta.")
    exit()

# ==========================================
# 2. MUESTREO Y GENERACIÓN SINTÉTICA
# ==========================================
print(f"Generando {NUM_RECORDS} registros sintéticos mediante muestreo con reemplazo...")

# Hacemos un "sample" (muestreo aleatorio con reemplazo) de nuestra base real
df_synthetic = df_base.sample(n=NUM_RECORDS, replace=True).reset_index(drop=True)

# Agregamos un ID único para cada data center simulado
df_synthetic.insert(0, 'id_facility', range(1, NUM_RECORDS + 1))

# ==========================================
# 3. INYECCIÓN DE RUIDO ESTADÍSTICO (Variabilidad del Mundo Real)
# ==========================================
print("Aplicando distribuciones de probabilidad (ruido gaussiano)...")

# A. Variación en la Tarifa Eléctrica (Desvío estándar del 10% del valor base)
ruido_tarifa = np.random.normal(0, df_synthetic['Tarifa_Electrica_USD_kWh'] * 0.10)
df_synthetic['tarifa_usd_kwh'] = np.round(df_synthetic['Tarifa_Electrica_USD_kWh'] + ruido_tarifa, 4)

# B. Variación en el PUE (Desvío estándar dependiendo del tipo de cooling)
# El líquido es más estable (menos desvío), el aire es más inestable (más desvío)
desvios_pue = df_synthetic['Tipo_Cooling'].map({
    'air-cooled': 0.12,
    'hybrid': 0.08,
    'liquid-cooled': 0.03
})
ruido_pue = np.random.normal(0, desvios_pue)
df_synthetic['pue_real'] = np.round(df_synthetic['PUE_Reportado'] + ruido_pue, 2)
# Límite físico: El PUE nunca puede ser menor a 1.0 (Leyes de la termodinámica)
df_synthetic['pue_real'] = df_synthetic['pue_real'].clip(lower=1.01)

# C. Variación en el CAPEX (Desvío estándar del 5%)
ruido_capex = np.random.normal(0, df_synthetic['CAPEX_MW_USD'] * 0.05)
df_synthetic['capex_per_mw_usd'] = np.round(df_synthetic['CAPEX_MW_USD'] + ruido_capex, 2)

# D. Generación de nuevas variables: Utilización (%) y Tamaño (MW)
# Asumimos una distribución normal para la utilización (media 65%, desvío 15%)
utilizacion = np.random.normal(65.0, 15.0, NUM_RECORDS)
df_synthetic['utilization_pct'] = np.round(np.clip(utilizacion, 30.0, 100.0), 1)

# Asumimos una distribución log-normal para el tamaño (la mayoría son medianos, pocos gigantes)
# Media aproximada de 15 MW, empujando los límites entre 1 MW y 100 MW
facility_mw = np.random.lognormal(mean=2.5, sigma=0.8, size=NUM_RECORDS)
df_synthetic['facility_mw'] = np.round(np.clip(facility_mw, 1.0, 100.0), 2)

# ==========================================
# 4. LIMPIEZA Y EXPORTACIÓN
# ==========================================
# Seleccionamos y renombramos las columnas finales para dejarlas limpias
columnas_finales = [
    'id_facility', 
    'Region_o_Estado', 
    'Tipo_Cooling', 
    'tarifa_usd_kwh', 
    'pue_real', 
    'capex_per_mw_usd', 
    'utilization_pct', 
    'facility_mw'
]
df_final = df_synthetic[columnas_finales].rename(columns={'Region_o_Estado': 'region', 'Tipo_Cooling': 'cooling_type'})

# Guardamos el dataset final
archivo_salida = 'datacenter_synthetic_benchmarks.csv'
df_final.to_csv(archivo_salida, index=False)

print(f"¡Éxito! Dataset exportado a '{archivo_salida}'.")
print("Muestra de los primeros 3 registros:")
print(df_final.head(3))