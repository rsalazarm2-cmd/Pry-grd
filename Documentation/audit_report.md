# 🔍 Auditoría Técnica: Anti-Patrones de Anidación y Postura de Seguridad

---

## Parte 1: Anti-Patrones de Código Anidado

### ✅ Archivos Limpios (Sin Anidación Problemática)

| Archivo | Líneas | Profundidad Máxima | Veredicto |
| :--- | :---: | :---: | :--- |
| [views.py](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/api/views.py) | 17 | 1 | ✅ Perfecto |
| [health_router.py](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/api/routers/health_router.py) | 22 | 1 | ✅ Perfecto |
| [project_router.py](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/api/routers/project_router.py) | 62 | 2 | ✅ Aceptable |
| [engine.py](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/infrastructure/duckdb/engine.py) | 12 | 1 | ✅ Perfecto |
| [App.tsx](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/frontend/src/App.tsx) | 284 | 2 | ✅ Bien modularizado |
| [client.ts](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/frontend/src/api/client.ts) | 16 | 1 | ✅ Perfecto |
| [projectApi.ts](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/frontend/src/api/projectApi.ts) | 40 | 2 | ✅ Aceptable |

---

### ⚠️ Hallazgos de Anidación (Backend)

#### 🔴 HALLAZGO 1 — `bronze_service.py` L38-55: Triple anidación `if → if → if`

```python
# L38-55: 3 niveles de profundidad
if manifest_path.exists() and target_path.exists():       # Nivel 1
    dup_count = ...
    if dup_count > 0:                                       # Nivel 2
        row_count = ... if target_path.exists() else 0      # Nivel 3 (ternario anidado)
        col_count = ... if target_path.exists() else 0      # Nivel 3
        file_size = ... if target_path.exists() else 0      # Nivel 3
        return BronzeIngestionResultDTO(...)
```

> [!WARNING]
> **Anti-patrón**: Guard clause invertido + ternarios repetitivos. Las 3 líneas con `if target_path.exists() else 0` son redundantes porque ya sabemos que `target_path.exists()` es `True` (comprobado en L38).

**Solución**: Early return con Guard Clause y eliminar ternarios redundantes.

---

#### 🔴 HALLAZGO 2 — `bronze_service.py` L60-92: Triple anidación `if → if → else`

```python
if target_path.exists():                    # Nivel 1
    if existing_cols == new_cols:            # Nivel 2
        is_incremental = True
        ...
        if temp_parquet.exists():            # Nivel 3
            temp_parquet.replace(target_path)
    else:                                    # Nivel 2
        ...
else:                                        # Nivel 1
    ...
```

> [!WARNING]
> **Anti-patrón**: Lógica de branching compleja con 3 niveles. Mezcla "primera carga", "carga incremental" y "esquema diferente" en un solo método.

**Solución**: Extraer a métodos privados `_first_ingestion()`, `_incremental_append()`, `_schema_overwrite()`.

---

#### 🟡 HALLAZGO 3 — `silver_service.py` L47-108: Doble anidación en bucle de transformación

```python
for col in column_names:                          # Nivel 1
    rule = column_rules.get(col)
    if rule and not rule.include_in_silver:        # Nivel 2
        continue
    ...
    if target_type in ("DOUBLE", ...):             # Nivel 2
        if clean_dots:                             # Nivel 3
            ...
        if clean_commas:                           # Nivel 3
            ...
    else:                                          # Nivel 2
        if global_trim:                            # Nivel 3
            ...
        if clean_chars:                            # Nivel 3
            ...
        if target_type == "CHAR":                  # Nivel 3
            ...
        elif target_type in ("DATE", ...):         # Nivel 3
            ...
    # Imputación
    if imputation == "DEFAULT":                    # Nivel 2
        if target_type in ("DOUBLE", ...):         # Nivel 3
            ...
        elif target_type == "BOOLEAN":             # Nivel 3
            ...
    elif imputation.startswith("ADVANCED"):        # Nivel 2
        if "MEAN" in imputation:                   # Nivel 3
            ...
        elif "MEDIAN" in imputation:               # Nivel 3
            ...
```

> [!WARNING]
> **Anti-patrón**: Este bucle tiene **4 niveles de profundidad** en algunos caminos. Es el bloque más complejo del sistema. Genera SQL Expression dinámicamente con if/elif en cascada.

**Solución**: Extraer a `_build_column_expression(col, rule, globals)` y `_build_imputation_expression(expr, imputation, target_type)`.

---

#### 🟡 HALLAZGO 4 — `medallion_router.py` L42-66: Doble anidación en `resolve_project_paths`

```python
def resolve_project_paths(project_id):
    project = p_repo.get_project(p_id)
    if not project:                        # Nivel 1
        projects = p_repo.list_projects()
        if projects:                       # Nivel 2
            project = projects[0]
        else:                              # Nivel 2
            project = p_repo.create_project(...)
```

> [!NOTE]
> **Severidad moderada**: Fallback en cascada. Es defendible pero podría ser un método `get_or_create_default()` en el repositorio.

---

#### 🟡 HALLAZGO 5 — `medallion_router.py` L89-94 y L111-116: `if → try → except pass` (Código Silencioso)

```python
if saved_recipe:                           # Nivel 1
    try:                                   # Nivel 2
        TransformSilverDataUseCase(...)    # Nivel 3
        GenerateGoldModelsUseCase(...)     # Nivel 3
    except Exception:                      # Nivel 2
        pass                               # ← ANTI-PATRÓN SEVERO
```

> [!CAUTION]
> **Anti-patrón grave**: `except Exception: pass` traga TODOS los errores silenciosamente. Si la receta falla, el usuario nunca lo sabrá. Este patrón se repite 2 veces en el mismo archivo.

**Solución**: Logging + re-raise controlado, o al menos `logging.warning(...)`.

---

#### 🟢 HALLAZGO 6 — Código duplicado: Método `_build_where_clauses` repetido 4 veces

La lógica de `where_clauses` + `search_term` + `filters_json` está **copiada textualmente** en:
- [bronze_service.py L272-290](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/infrastructure/duckdb/bronze_service.py#L272-L290)
- [silver_service.py L167-188](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/infrastructure/duckdb/silver_service.py#L167-L188)
- [gold_service.py L106-124](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/infrastructure/duckdb/gold_service.py#L106-L124)
- [gold_service.py L106-124](file:///run/media/rsalazar/Ronald/Python/Pry%20Grd/backend/src/infrastructure/duckdb/gold_service.py#L106-L124) (reutilizado por `query_gold_account_balances`)

> [!IMPORTANT]
> **Anti-patrón DRY**: 4 copias del mismo bloque. Cualquier corrección de seguridad (por ejemplo, sanitización SQL) debe aplicarse 4 veces manualmente.

**Solución**: Extraer a un mixin o utility `QueryFilterBuilder.build_where_sql(columns, search_term, column_name, filters_json)`.

---

### ⚠️ Hallazgos de Anidación (Frontend)

#### 🟡 HALLAZGO 7 — `CleaningConfigModal.tsx` L71-101: `handleAutoConfig` con 4 niveles de if/else

```tsx
columns.forEach((col) => {                    // Nivel 1
  if (isSingleValueConstant) {                // Nivel 2
    updateColumnRule(...); return;
  }
  if (isMonetary) {                           // Nivel 2
    ...
  } else if (isDate) {                        // Nivel 2
    ...
  } else if (colUpper === 'CURRENCY' || ...) {// Nivel 2
    ...
  } else if (colUpper.includes('HEADER_ID')) {// Nivel 2
    ...
  } else {                                    // Nivel 2
    ...
  }
});
```

> [!NOTE]
> **Severidad moderada**: if/elif en cascada dentro de forEach. Es aceptable para una función de configuración auto-detect pero podría beneficiarse de un mapa de estrategias.

---

#### 🟡 HALLAZGO 8 — `ProjectSelectorModal.tsx` L281-375: JSX con 5 niveles de anidación visual

```tsx
{projects.map((proj) => (         // Nivel 1
  <div>                            // Nivel 2
    <div>                          // Nivel 3
      <div>                        // Nivel 4
        <div>                      // Nivel 5 (badges)
          {isActive && (...)}
          {proj.has_recipe && (...)}
```

> [!NOTE]
> **Severidad baja**: Es JSX, no lógica. Pero podría extraerse un `<ProjectCard>` sub-componente.

---

---

## Parte 2: Auditoría de Seguridad Django

### 🔴 Hallazgos Críticos de Seguridad

#### 🔴 SEC-1: `SECRET_KEY` hardcodeada en texto plano

```python
# config/settings.py L23
SECRET_KEY = "django-insecure-medallion-analytics-secret-key-dev-only"
```

> [!CAUTION]
> **Severidad CRÍTICA**. La `SECRET_KEY` de Django es la raíz de toda la seguridad criptográfica: firmas de sesión, tokens CSRF, cookies firmadas. Si está en el repositorio, cualquier persona con acceso al código puede falsificar sesiones.

**Solución**: Moverla a variable de entorno:
```python
import os
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-key-not-for-production")
```

---

#### 🔴 SEC-2: `DEBUG = True` sin condicional

```python
# config/settings.py L25
DEBUG = True
```

> [!CAUTION]
> **Severidad CRÍTICA en producción**. Con `DEBUG=True`, Django muestra stacktraces completos con variables locales, rutas del filesystem, y configuraciones. Un atacante puede ver la estructura interna completa del sistema.

**Solución**:
```python
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
```

---

#### 🔴 SEC-3: `ALLOWED_HOSTS = ["*"]`

```python
# config/settings.py L27
ALLOWED_HOSTS = ["*"]
```

> [!CAUTION]
> **Severidad ALTA**. Acepta peticiones desde cualquier dominio. Permite ataques de **Host Header Injection** donde un atacante puede manipular el encabezado `Host` para generar links maliciosos en emails de reset de contraseña o redireccionamientos.

**Solución**:
```python
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
```

---

#### 🔴 SEC-4: `CORS_ALLOW_ALL_ORIGINS = True`

```python
# config/settings.py L73
CORS_ALLOW_ALL_ORIGINS = True
```

> [!CAUTION]
> **Severidad ALTA**. Cualquier sitio web del mundo puede hacer peticiones AJAX a tu API y leer las respuestas. Esto permite **Cross-Site Request Forgery** y **Data Exfiltration** desde el navegador de cualquier usuario.

**Solución**:
```python
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Solo en desarrollo
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
```

---

#### 🔴 SEC-5: Falta de Middleware de Seguridad de Django

```python
# config/settings.py L36-38
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]
```

> [!CAUTION]
> **Severidad ALTA**. Faltan **todos** los middlewares de seguridad que Django proporciona:

| Middleware Faltante | Protección que brinda |
| :--- | :--- |
| `SecurityMiddleware` | HTTPS redirect, `X-Content-Type-Options`, `Strict-Transport-Security` (HSTS) |
| `CsrfViewMiddleware` | Protección contra **Cross-Site Request Forgery** |
| `XFrameOptionsMiddleware` | Protección contra **Clickjacking** (iframes maliciosos) |

**Solución**:
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

---

#### 🔴 SEC-6: **SQL Injection** en construcción de queries DuckDB

```python
# bronze_service.py L39
is_dup_query = f"... WHERE file_hash = '{file_hash}'"

# bronze_service.py L275-277
term = search_term.strip().replace("'", "''")
where_clauses.append(f"CAST(\"{column_name}\" AS VARCHAR) ILIKE '%{term}%'")
```

> [!CAUTION]
> **Severidad ALTA**. Todo el SQL se construye con **f-strings** e interpolación directa de valores de usuario. El `replace("'", "''"` manual NO es protección suficiente contra inyección SQL avanzada (Unicode escapes, backslash tricks).
>
> **Esto se repite en**: `bronze_service.py`, `silver_service.py`, `gold_service.py` — todas las funciones de query.

**Solución**: DuckDB soporta **parámetros posicionales** (`?` placeholders):
```python
self.conn.execute("SELECT * FROM t WHERE col ILIKE ?", [f"%{term}%"])
```

---

#### 🟡 SEC-7: Sin validación de tipo MIME ni tamaño en Upload de archivos

```python
# medallion_router.py L70-78
def upload_ingest_bronze(request, file: UploadedFile = File(...)):
    temp_csv_path = settings.PROJECT_ROOT / f"data/raw/temp_{file.name}"
    with open(temp_csv_path, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)
```

> [!WARNING]
> **Problemas**:
> 1. Sin validación de extensión: se acepta `.exe`, `.sh`, `.zip`
> 2. Sin límite de tamaño: un archivo de 10GB bloquea el servidor
> 3. `file.name` se usa directamente en el path: un nombre como `../../etc/passwd` = **Path Traversal**

**Solución**:
```python
ALLOWED_EXTENSIONS = {'.csv', '.txt', '.tsv'}
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

ext = Path(file.name).suffix.lower()
if ext not in ALLOWED_EXTENSIONS:
    raise HttpError(400, "Solo se aceptan archivos CSV")
if file.size > MAX_UPLOAD_SIZE:
    raise HttpError(413, "El archivo excede el límite de 100MB")
# Sanitizar nombre
safe_name = f"temp_{uuid4().hex}{ext}"
```

---

#### 🟡 SEC-8: `except Exception: pass` silencia errores de seguridad

```python
# medallion_router.py L90-94
except Exception:
    pass
```

> [!WARNING]
> Si la receta falla por un **error de inyección SQL**, **permiso de archivo**, o **corrupción de datos**, el error se traga silenciosamente. En un contexto de seguridad, esto puede ocultar ataques activos.

---

#### 🟡 SEC-9: Sin autenticación en ningún endpoint

> [!IMPORTANT]
> **Ningún endpoint** de la API requiere autenticación. Cualquier persona con acceso a la red puede:
> - Listar/crear/eliminar proyectos
> - Subir archivos CSV arbitrarios
> - Ejecutar queries sobre los datos
> - Eliminar datos Medallion
>
> Django Ninja soporta autenticación nativa con `from ninja.security import HttpBearer`.

---

#### 🟢 SEC-10: Frontend no sanitiza respuestas del servidor

```tsx
// medallionApi.ts — Todas las funciones
const res = await fetch(`${API_BASE}/...`);
return res.json(); // Sin verificar res.ok
```

> [!NOTE]
> Si el servidor responde con HTTP 500, el `.json()` puede fallar silenciosamente o parsear HTML como JSON. No se valida `res.ok` en ninguna llamada.

---

## Resumen Ejecutivo

### Anidación de Código

| Severidad | Hallazgos | Archivos Afectados |
| :--- | :---: | :--- |
| 🔴 Crítico | 2 | `bronze_service.py` (triple if) |
| 🟡 Medio | 4 | `silver_service.py`, `medallion_router.py`, `CleaningConfigModal.tsx` |
| 🟢 Bajo (DRY) | 1 | 4 copias de `_build_where_clauses` |
| ✅ Limpio | 7 | `views.py`, `health_router.py`, `project_router.py`, `engine.py`, `App.tsx`, `client.ts`, `projectApi.ts` |

### Seguridad Django

| Severidad | Hallazgos | Impacto |
| :--- | :---: | :--- |
| 🔴 Crítico | 6 | SECRET_KEY, DEBUG, ALLOWED_HOSTS, CORS, Middleware faltante, SQL Injection |
| 🟡 Medio | 3 | Upload sin validación, except:pass silencioso, Sin autenticación |
| 🟢 Bajo | 1 | Frontend no valida res.ok |

> [!CAUTION]
> **Veredicto**: La postura de seguridad actual es **apropiada ÚNICAMENTE para desarrollo local**. Para cualquier despliegue (staging, producción, o demo con datos reales) se requieren los 6 hallazgos críticos corregidos como mínimo.
