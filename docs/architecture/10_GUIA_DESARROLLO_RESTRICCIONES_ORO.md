# 📜 10. GUÍA DE DESARROLLO Y RESTRICCIONES DE ORO
### Estándar de Código, Modularidad y Buenas Prácticas de Ingeniería
**Proyecto de Maestría en Analítica de Datos | Nivel: Enterprise Grade**

---

## 📌 1. REGLAS DE ORO INQUEBRANTABLES

### Rule 1: Límite Estricto de 200 Líneas (CRÍTICO)
- **NINGÚN archivo de código (Python o TypeScript) puede exceder las 200 líneas.**
- Si la lógica crece, refactorizar de inmediato separando en servicios auxiliares, composables o DTOs.

### Rule 2: Principio de Responsabilidad Única (SRP) y Atomicidad
- Cada función debe hacer UNA SOLA COSA. Funciones cortas, atómicas y simples.
- Cero anidamientos profundos. Utilizar **Early Returns (Retorno Temprano)** para aplanar el flujo.

### Rule 3: Prohibición Absoluta de Django ORM para Analítica
- Django se utiliza **únicamente como enrutador HTTP REST Ninja**.
- Todas las consultas y transformaciones analíticas sobre parquets y datasets se ejecutan mediante la **API nativa vectorizada de DuckDB**.

### Rule 4: Tipado Estricto y Cero `Any`
- Tipado estricto en Python (`Type Hints` con Pydantic V2) y TypeScript (`Strict Mode`).
- Cero uso de `Any` o `dict` genéricos para datos de negocio.

### Rule 5: Paquete de Dependencias con `uv`
- Utilizar el gestor ultra-rápido `uv` para Python. Evitar ejecuciones globales con `pip install`.
