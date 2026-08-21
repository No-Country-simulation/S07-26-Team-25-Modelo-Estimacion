# ⚡ Calculadora de Stranded Capacity (Modelo de Estimación)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/) 

## 📌 ¿Qué hace esta aplicación?

Esta aplicación es una **Calculadora Interactiva y Dashboard** para estimar el **Stranded Capacity (Capacidad Varada)** y su impacto financiero en centros de datos de alta densidad optimizados para Inteligencia Artificial (AI Data Centers).

### 🎯 Funcionalidades Principales
- **Cálculo de Rangos (Floor, Mid, Ceiling):** Permite ingresar la potencia del Data Center (MW), el porcentaje de utilización actual (%) y el tipo de refrigeración (*Air-cooled*, *Liquid-cooled* o *Hybrid*).
- **Métricas e Impacto Financiero:** Muestra el $CAPEX$ desperdiciado, pérdidas anuales estimadas en USD, valor potencial recuperable y tiempo estimado de ROI (retorno de inversión) en meses.
- **Análisis de Sensibilidad (Tornado Chart):** Identifica visualmente qué variables operativas impactan más en el costo total de la ineficiencia.
- **Simulación de Monte Carlo:** Presenta distribuciones estocásticas (P10, P50, P90) para un análisis de riesgo cuantitativo auditable.
- **Arquitectura Limpia:** Separación estricta entre el motor de cálculo matemático backend y la interfaz gráfica frontend desarrollada en **Streamlit**.

---

## 🚀 Cómo Ejecutar la Aplicación

### 1. Clonar o acceder al repositorio
Abre tu terminal y ubícate en la carpeta raíz del proyecto:
```bash
git clone https://github.com/No-Country-simulation/S07-26-Team-25-Modelo-Estimacion.git
cd S07-26-Team-25-Modelo-Estimacion
```

---

### 2. Opción Recomendada (Usando `uv`)

Si tienes instalado el administrador de paquetes **`uv`**, ejecuta:

1. **Instalar dependencias y sincronizar entorno:**
   ```bash
   uv sync
   ```

2. **Iniciar la aplicación en Streamlit:**
   ```bash
   uv run streamlit run app/app.py
   ```

---

### 3. Opción Tradicional (Con Entorno Virtual Activo)

Si prefieres activar el entorno virtual manualmente:

* **En Git Bash:**
  ```bash
  source .venv/Scripts/activate
  streamlit run app/app.py
  ```

* **En PowerShell (Windows):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  streamlit run app/app.py
  ```

* **En Command Prompt (CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  streamlit run app/app.py
  ```

---

## 🌐 Acceso a la Interfaz

Una vez iniciado el servidor de Streamlit, se abrirá automáticamente una pestaña en tu navegador web en la siguiente dirección local:

👉 **[http://localhost:8501](http://localhost:8501)**

---

## 🧪 Verificación y Pruebas Unitarias

Para comprobar el correcto funcionamiento del motor de cálculo matemático:

```bash
uv run python test_stranded_model.py
```
