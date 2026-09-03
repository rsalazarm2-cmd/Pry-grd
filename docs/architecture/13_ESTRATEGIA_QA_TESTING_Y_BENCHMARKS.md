# 🧪 13. ESTRATEGIA QA, SUITE DE PRUEBAS Y BENCHMARKS
### Pruebas Unitarias, Integración DuckDB y Benchmarks de Rendimiento (< 50 ms)
**Proyecto de Maestría en Analítica de Datos | Framework: Pytest, Vue Test Utils, DuckDB Native**

---

## 📌 1. ESTRATEGIA GLOBAL DE PRUEBAS DE CALIDAD (QA)

El sistema impone una política de cero regresiones para garantizar la estabilidad de los cómputos analíticos y la integridad financiera.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 🧪 Pytest Unit Tests -> Pruebas de DTOs, Transformaciones AST y Compiladores   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 🦆 Integration Tests -> Pruebas de DuckDB Engine, Consultas SQL y Parquet I/O   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ⚡ Benchmarks -> Pruebas de Latencia (< 50 ms por consulta sobre 500k filas)    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 2. COMANDOS DE EJECUCIÓN DE PRUEBAS AUTOMATIZADAS

### Ejecutar Suite Backend completa con `pytest` y `uv`:
```bash
cd backend
uv run pytest -v --tb=short
```

### Ejecutar Pruebas de Integración de QA:
```bash
cd qa_environment
uv run pytest test_pipeline_e2e.py -v
```

### Criterios de Aceptación Obligatorios:
1. **0 Fallos (`0 failures`):** Todos los tests unitarios e integrados deben pasar en verde.
2. **Latencia < 50 ms:** Todas las consultas analíticas sobre Parquets procesados deben responder en menos de 50 milisegundos.
3. **Ningún archivo excede 200 líneas.**
