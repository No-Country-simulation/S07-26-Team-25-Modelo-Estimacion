# ⚡ FastAPI Backend Service - Stranded Capacity API

> **No Country Project - Entregable 6** | Microservicio REST para la estimación de Capacidad Varada y Simulación de Monte Carlo en Data Centers de IA.

---

## 📌 Descripción
Este módulo implementa el backend de la solución utilizando **FastAPI**. Expone el motor determinístico de estimación de rangos (Floor & Ceiling) y el motor de simulación estocástica de Monte Carlo mediante endpoints REST documentados automáticamente con OpenAPI / Swagger.

---

## 🚀 Cómo Ejecutar la API Localmente

### 1. Con `uv` (Recomendado)
```bash
uv run uvicorn 06_api_backend.main:app --reload --port 8000
```

### 2. Con el entorno `.venv` activado
```bash
uvicorn 06_api_backend.main:app --reload --port 8000
```

El servidor iniciará en: **`http://localhost:8000`**

---

## 📖 Documentación Interactiva (Swagger / ReDoc)

Una vez iniciado el servidor, puedes acceder a la interfaz gráfica interactiva para probar los endpoints directamente:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔌 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Estado del servicio y metadatos de la API |
| `GET` | `/api/v1/benchmarks` | Matriz de benchmarks de enfriamiento y parámetros de la industria |
| `POST` | `/api/v1/calculate` | Cálculo determinístico de Stranded Capacity (MW y Pérdida Financiera USD) |
| `POST` | `/api/v1/monte-carlo` | Simulación estocástica de Monte Carlo (Percentiles P10, P50, P90) |

---

## 📝 Ejemplos de Petición (curl)

### Endpoint de Cálculo Determinístico (`POST /api/v1/calculate`)
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/calculate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "facility_mw": 15.0,
  "utilization_pct": 87.0,
  "cooling_type": "air-cooled"
}'
```

---

## 🧪 Ejecutar Pruebas Unitarias
Para correr la suite de tests de la API:
```bash
uv run python 06_api_backend/test_api.py
```
