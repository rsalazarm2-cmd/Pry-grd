# 🛡️ Sistema de Auditoría Forense Contable ERP — Arquitectura Medallón (Bronce ➔ Plata ➔ Oro)

Plataforma Enterprise de Auditoría Forense, Análisis Exploratorio de Datos (EDA) y Detección de Riesgos/Fraudes en Asientos Contables ERP (Oracle EBS / SAP), basada en una **Arquitectura Medallón de 3 Capas**, **DuckDB Nativo**, **Motor NLP de Matching Difuso y Profiling Empírico de 3 Capas** y un **Canvas Studio de Modelado Visual por Nodos (Vue 3 + TypeScript)**.

---

> [!IMPORTANT]
> ## 📖 MANUAL DE INSTALACIÓN Y DESPLIEGUE RÁPIDO PASO A PASO
> Guía completa para instalar prerrequisitos y desplegar el proyecto Backend (Python/DuckDB) y Frontend (Vue 3/Vite) en cualquier equipo.

### 📦 Paso 1: Instalación Obligatoria del Gestor `uv` (Backend Python)
Este proyecto exige **`uv`** (Astral Python Package Manager) para gestionar el entorno virtual `.venv` y dependencias en menos de 1 segundo.

- **Linux / macOS (Terminal):**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell):**
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Instalación alternativa con pip:**
  ```bash
  pip install uv
  ```

---

### 💻 Paso 2: Despliegue del Backend (API REST Django + DuckDB C++)

1. Entra a la carpeta del backend:
   ```bash
   cd backend
   ```
2. Instala y sincroniza automáticamente las dependencias exactas (`pyproject.toml`):
   ```bash
   uv sync
   ```
3. Ejecuta el servidor en el puerto 8000:
   - **Linux / macOS:** `.venv/bin/python manage.py runserver 8000`
   - **Windows:** `.venv\Scripts\python manage.py runserver 8000`

---

### 🎨 Paso 3: Despliegue del Frontend (Vue 3 + TypeScript + Vite)

1. En una nueva terminal, entra a la carpeta frontend:
   ```bash
   cd frontend
   ```
2. Instala las dependencias de Node.js:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo:
   ```bash
   npm run dev
   ```
4. Abre `http://localhost:5173/` en tu navegador.

---

### 🧪 Paso 4: Ejecución de Pruebas Automatizadas (QA Pytest)

```bash
# Desde la raíz del proyecto
backend/.venv/bin/pytest qa_environment/ -v
```

---

## 🏛️ Stack Tecnológico Estricto & Arquitectura Hexagonal

### ⚙️ Backend (Python + DuckDB + Pydantic)
* **Motor Analítico In-Memory:** API Nativa de **DuckDB** para procesamiento OLAP vectorizado en C++ sobre archivos **Apache Parquet**.
* **Enrutamiento HTTP Slim:** **Django** (utilizado *únicamente* como enrutador HTTP delgado; **PROHIBIDO el uso de Django ORM** para datos analíticos).
* **DTOs & Tipado Estricto:** **Pydantic V2** para validación atómica y contratos de dominio immutables (Cero `dict` o `Any`).
* **Motor Infeccioso NLP de 3 Capas (`FuzzyForensicNLPClassifier`):**
  1. *Inspección Empírica en DuckDB:* Profiling de Ratios de Unicidad (`COUNT DISTINCT / TOTAL`) y Nulos en $<15\text{ ms}$.
  2. *Matching Semántico Difuso:* Clasificación por similitud de tokens (SequenceMatcher) sin campos quemados.
  3. *Garantía Surrogate Kimball:* Generación de llaves relacionales `FOLIO_ASIENTO_ID` mediante `DENSE_RANK() OVER (...)` para evitar productos cartesianos.
* **Gestor de Paquetes:** `uv` para gestión ultra-rápida de dependencias en Python 3.14.

### 🎨 Frontend (Vue 3 + TypeScript Strict + Vite)
* **Framework SPA:** **Vue 3** con Composition API (`<script setup lang="ts">`) y **TypeScript en Strict Mode**.
* **Gestión de Estado:** **Pinia** para reactividad centralizada del pipeline Medallón.
* **Studio Blueprint Canvas (`VisualNodeGraphCanvas.vue`):** Lienzo interactivo visual de modelado por nodos conectores con hilos SVG (Draw.io style), renombrado inline de vistas, selector de tipos de Join (`LEFT`, `INNER`, `RIGHT`, `FULL`) y estacionamiento de campos (Parking Lot Drawer).
* **Herramientas de Build:** **Vite** para HMR instantáneo y empaquetado optimizado.

---

## 📁 Estructura del Proyecto

```text
Pry_Grd/
├── backend/                  # API REST Hexagonal (Django + DuckDB + Pydantic + NLP)
│   ├── src/
│   │   ├── ai_translator/    # Motor NLP de 3 Capas (Fuzzy NLP + DuckDB Profiler)
│   │   ├── audit/            # Analizadores Forenses (Benford, Segregación SoD, Vector)
│   │   ├── data_ingestion/   # Capa Bronce (Catálogo e Ingestión Parquet)
│   │   └── shared/           # Entidades de Dominio (JournalEntryDTO)
│   └── pyproject.toml        # Configuración estricta con uv
├── frontend/                 # Cliente SPA (Vue 3 + TypeScript + Vite + Pinia)
│   ├── src/
│   │   ├── components/
│   │   │   ├── canvas/       # Node Studio Canvas (VisualNodeGraphCanvas, NodeCard)
│   │   │   └── forms/        # Formularios de Transformación Plata/Oro
│   │   ├── views/            # Espacios de Trabajo (Bronze, Silver, Gold Workspaces)
│   │   └── stores/           # Store Central Pinia
│   └── package.json
├── qa_environment/           # Suite de Pruebas Automatizadas Pytest (50+ Tests)
├── Documentation/            # Guías de Dominio Financiero y Reportes de Auditoría
└── README.md                 # Documentación Principal del Sistema
```

---

## ⚡ Ejecución del Sistema

### 1. Backend (Python + DuckDB)
```bash
cd backend
uv sync
.venv/bin/python manage.py runserver 8000
```

### 2. Frontend (Vue 3 + Vite)
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Pruebas Automatizadas (QA Suite)
El sistema cuenta con una suite de pruebas End-to-End en Pytest con **100% de éxito**:
```bash
backend/.venv/bin/pytest qa_environment/ -v
```

---

## 📜 Reglas de Diseño de Código (Golden Rules)
1. **Regla de las 200 Líneas (CRÍTICO):** NINGÚN archivo de código (Python o TypeScript) excede las 200 líneas.
2. **Principio de Responsabilidad Única (SRP):** Funciones atómicas, retorno temprano (Early Returns) y cero anidamientos profundos.
3. **Tipado Estricto & Google Docstrings:** Sin `Any` ni `dict` genéricos.
