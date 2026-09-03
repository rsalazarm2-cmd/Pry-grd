# 🚀 11. MANUAL DE DESPLIEGUE Y EJECUCIÓN LOCAL
### Guía de Instalación, Configuración de Entorno `uv` y Ejecución de Servidores
**Proyecto de Maestría en Analítica de Datos | Stack: Python 3.14, `uv`, Node.js, Vite, DuckDB**

---

## 📌 1. PRERREQUISITOS DEL SISTEMA

Para ejecutar la plataforma en un PC de escritorio local se requiere:
- **Python 3.12+ (Recomendado Python 3.14)**
- **Package Manager `uv`** (Astral)
- **Node.js 18+ & npm 9+**
- **Sistema Operativo:** Linux (Ubuntu/Debian/Fedora), macOS o Windows WSL2.

---

## 🛠️ 2. INSTALACIÓN DE DEPENDENCIAS Y ENTORNOS

### 1. Clonar el Repositorio y Verificar Entorno:
```bash
cd /home/rsalazar/Python/Pry_Grd
```

### 2. Configurar Backend (Python + `uv` + Django Ninja):
```bash
cd backend
# Sincronizar y crear virtualenv con uv
uv sync
# Verificar que Django y DuckDB están instalados
uv run python -c "import django, duckdb; print('Django:', django.__version__, '| DuckDB:', duckdb.__version__)"
```

### 3. Configurar Frontend (Vue 3 + TypeScript + Vite):
```bash
cd ../frontend
# Instalar paquetes Node.js
npm install
```

---

## ⚡ 3. COMANDOS DE EJECUCIÓN EN PARALELO

### Iniciar Servidor Backend (Django REST Ninja - Puerto 8000):
```bash
cd backend
uv run python manage.py runserver 0.0.0.0:8000
```

### Iniciar Servidor Frontend (Vite Dev Server - Puerto 5173):
```bash
cd frontend
npm run dev
```

El servidor Vite redirige automáticamente todas las peticiones con prefijo `/api/*` hacia `http://localhost:8000/api/*` mediante la configuración de proxy en `vite.config.ts`.
