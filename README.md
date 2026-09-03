# Pry_Grd - Datamart Financiero ERP (Arquitectura Medallón)

Plataforma de procesamiento y analítica financiera contable para datos ERP a gran escala (Oracle EBS) basada en la **Arquitectura Medallón (Bronze ➔ Silver ➔ Gold)** con **Clean Architecture / Domain-Driven Design (DDD)**.

---

## 🏛️ Documentación de Arquitectura

Para consultar la especificación técnica completa, diagramas Mermaid, flujo de datos, estructura de subdominios y patrones de diseño, revisa el documento oficial:

📄 **[ARCHITECTURE.md](./ARCHITECTURE.md)** (o en la carpeta [`Documentation/`](./Documentation/))

---

## 🚀 Estructura del Proyecto

- **`backend/`**: Servidor API REST en Python 3.12+ (Django Ninja) que integra el motor analítico in-memory **DuckDB** y persistencia columnar comprimida en **Apache Parquet**. Aplica Clean DDD por subdominios (`project`, `bronze`, `silver`, `gold`, `ai_translator`, `shared`, etc.).
- **`frontend/`**: Cliente de ultra alto rendimiento desarrollado en **Rust** con **Dioxus 0.7** compilado a **WebAssembly (WASM)**, utilizando Signals para gestión de estado y tabla virtualizada para +100k registros a 60 FPS.
- **`frontend_react_legacy/`**: Versión previa del cliente SPA en React 18 / TypeScript / Vite / Zustand.
- **`audit_system/`**: Módulo independiente de auditoría forense contable (Partida Doble, Reglas Maker/Checker SoD, Informe de Integridad).
- **`qa_environment/`**: Suite de pruebas automáticas e integración End-to-End con Pytest.
- **`Documentation/`**: Guías técnicas, especificaciones de modelado dimensional y reportes de auditoría.

---

## ⚡ Ejecución Rápida

### Backend (Django Ninja + DuckDB)
```bash
cd backend
uv sync
python manage.py runserver 8000
```

### Frontend (Rust / Dioxus WASM)
```bash
cd frontend
dx serve
```

