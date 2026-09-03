# 🏛️ 01. ARQUITECTURA GENERAL MEDALLION Y INGENIERÍA CLEAN HEXAGONAL
### Especificación Técnica de Arquitectura de Datos, Capas Medallion y Patrones de Diseño
**Proyecto de Maestría en Analítica de Datos | Backend: Python 3.14, Django REST Ninja, DuckDB | Frontend: Vue 3, TypeScript**

---

## 📌 1. FILOSOFÍA DE ARQUITECTURA Y PARADIGMAS DE DISEÑO

El sistema está diseñado para procesar volúmenes masivos de asientos contables provenientes de diversos Enterprise Resource Planning (ERP) como **Oracle EBS, SAP S/4HANA, Microsoft Dynamics 365 y AS400**, permitiendo a auditores financieros y analistas de datos ejecutar auditoría forense, validación de integridad y segregación de funciones (SoD).

### 📐 Paradigmas Fundamentales de Arquitectura:

1. **Arquitectura Medallion (Bronce ➔ Plata ➔ Oro):**  
   Descomposición lógica y física del almacenamiento de datos en tres niveles de madurez incremental:
   - **Bronce (Data Lake Crudo):** Ingesta inmutable *as-is*, custodia criptográfica (SHA-256) y diagnóstico exploratorio físico (EDA).
   - **Plata (Standardized Data Store):** Estandarización de esquema a 33 campos canónicos en español, selección/reducción dinámica de columnas, expresiones AST de fechas (deltas $T_{\text{delta}}$, días de semana, redundancia % match), Amount Splitter (+/- ➔ Cargo/Abono), linaje transparente y memoria inmutable.
   - **Oro (Business Data Marts & Advanced Analytics):** Modelos estadísticos rigurosos (Pearson $r$, Spearman $\rho$, Mahalanobis $D^2$, Benford MAD, Entropía $H(X)$, Z-Score temporal) y Command Center SOX con impacto financiero en dólares ($).

2. **Clean Architecture / Hexagonal (Puertos y Adaptadores):**  
   Aislamiento total de las reglas de negocio respecto a la infraestructura:
   - `Domain Layer`: Interfaces abstractas (ABC) y DTOs inmutables de Pydantic V2.
   - `Application Layer`: Casos de uso atómicos que orquestan las operaciones de negocio.
   - `Infrastructure Layer`: Adaptadores concretos de DuckDB nativo, compiladores SQL, persistencia JSON y exportadores Parquet.
   - `API / Controller Layer`: Django REST Ninja como enrutador HTTP delgado (*Thin Controller*).

---

## 📐 2. RESTRICCIONES DE ORO E INVARIANTE ARQUITECTÓNICO

El sistema impone cinco restricciones de oro innegociables para garantizar mantenibilidad, velocidad y calidad de grado de producción:

### 1. Regla de las 200 Líneas por Archivo (CRÍTICO)
Ningún archivo de código (Python o TypeScript) puede superar las 200 líneas bajo ninguna circunstancia. Si una clase o módulo se acerca a este límite, se debe refactorizar obligatoriamente dividiéndolo en servicios auxiliares, composables o DTOs.

### 2. Principio de Responsabilidad Única (SRP) & Atomicidad
Cada función debe realizar UNA SOLA COSA. Se exige el uso de **Early Returns (Retorno Temprano)** para aplanar el código y eliminar anidamientos profundos de `if-else`.

```python
# Ejemplo de Estilo Obligatorio: Early Return Flattening
def execute_pipeline(source_path: Path) -> ResultDTO:
    if not source_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {source_path}")
        
    if source_path.stat().st_size == 0:
        raise ValueError("El archivo está vacío.")
        
    # Flujo principal sin anidamientos
    return process_parquet(source_path)
```

### 3. Prohibición Absoluta de Django ORM para Datos Analíticos
Django se utiliza **exclusivamente como enrutador de peticiones HTTP REST (Ninja API)**. Está estrictamente prohibido utilizar el ORM de Django para modelar, cargar o consultar tablas analíticas. Todas las consultas y transformaciones sobre los Parquets se ejecutan con la **API nativa vectorizada en C++ de DuckDB**.

### 4. Tipado Estricto & Cero `Any`
- Python: Annotations estrictas con `pydantic` V2 y `typing` (`Optional`, `List`, `Dict`, `Literal`).
- TypeScript: `Strict Mode` habilitado en `tsconfig.json`. Cero uso de `any` o objetos genéricos para datos de negocio.

### 5. Gestión de Dependencias con `uv`
Toda la gestión de paquetes en Python se realiza mediante `uv` (Astral), garantizando la instalación reproducible y la resolución ultra-rápida de virtualenvs.

---

## 🏛️ 3. INYECCIÓN DE DEPENDENCIAS Y FLUJO DE DATOS ATÓMICO

```
[ Petición HTTP Frontend ] 
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ API Layer (Django REST Ninja Router)                    │
│ Ex: @router.post("/silver/transform")                   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ Application Layer (Use Case)                            │
│ Ex: TransformSilverDataUseCase(repo: JournalRepository) │
└─────────────────────────────────────────────────────────┘
         │
         ▼ (Inyección mediante ABC Interface)
┌─────────────────────────────────────────────────────────┐
│ Domain Layer (Pydantic V2 DTOs)                         │
│ Ex: BronzeToSilverRulesDTO, TabularResultDTO            │
└─────────────────────────────────────────────────────────┘
         │
         ▼ (Implementación Concreta)
┌─────────────────────────────────────────────────────────┐
│ Infrastructure Layer (DuckDB Engine & Parquet Storage)  │
│ Ex: SilverDuckDBService -> DuckDB C++ Vectorized Engine │
└─────────────────────────────────────────────────────────┘
```

Esta separación garantiza que las reglas de negocio de auditoría forense puedan probarse mediante tests unitarios en milisegundos sin levantar servidores web ni bases de datos relacionales pesadas.
