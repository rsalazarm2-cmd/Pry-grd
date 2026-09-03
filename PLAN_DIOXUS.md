# 🚀 Plan de Migración a Dioxus (Arquitectura de Máxima Potencia)

> [!IMPORTANT]
> **ACLARACIÓN CRÍTICA SOBRE LA UBICACIÓN DEL PROYECTO**
> **El proyecto NO SE MUEVE.** Tu código fuente, tu carpeta `frontend`, tu carpeta `backend` y absolutamente todo tu trabajo **permanecen y permanecerán** en tu disco actual: `/run/media/rsalazar/Ronald/Python/Pry Grd/`.
> 
> *¿Por qué configuré algo en `/home/rsalazar/`?*
> Los discos externos montados en Linux tienen bloqueada la ejecución de scripts por seguridad (`noexec`). Esto hace que el compilador de Rust (Cargo) falle al compilar librerías. Para solucionarlo sin dañar tu disco, le ordené a Cargo que guarde **únicamente la "basura de compilación" temporal (los archivos `.o` y caché binario)** en `~/.cargo/target_frontend`. Tu código fuente NUNCA saldrá de `/run/media/...`.

---

## Fases Completadas ✅

### Fase 1: Destrucción y Renacimiento (Estructura Base)
- Respaldar la carpeta `frontend` a `frontend_react_legacy`. ✅
- Ejecutar `cargo new frontend` para crear el proyecto Dioxus original aquí mismo. ✅
- Resolver los bloqueos de permisos del disco enviando la compilación (y solo la compilación) al disco nativo. ✅

### Fase 2: El Arsenal de Crates (Librerías Enterprise)
Agregamos la lista exhaustiva al `Cargo.toml` para reemplazar todo NPM:
- **Core UI:** `dioxus`, `dioxus-router`, `dioxus-free-icons`. ✅
- **Comunicaciones:** `reqwest`, `futures`, `wasm-bindgen-futures`. ✅
- **Datos y Serialización:** `serde`, `serde_json`, `serde-wasm-bindgen` (Arma secreta). ✅
- **Big Data (WebAssembly):** `parquet`, `arrow`. ✅
- **Concurrencia y DOM:** `gloo-worker`, `gloo-timers`, `web-sys`. ✅

### Fase 3: Gestión de Estado (Adiós Zustand)
En Dioxus usamos el sistema nativo de **Context Providers** y **Signals** para máxima seguridad de memoria (0 fugas).
- `ui_store.rs`: Reemplazó a `uiSlice.ts`. ✅
- `recipe_store.rs`: Reemplazó a `recipeSlice.ts`. ✅

---

## Fases Pendientes ⏳

### Fase 4: Reconstrucción de Componentes (RSX y Virtualización Propia)
Traduciremos los componentes clave de `.tsx` a `.rs` usando la macro `rsx!`.
- **Módulo Base**: Construiremos el `virtual_scroll.rs`. Implementaremos matemática en Rust puro para dibujar solo las filas visibles, reciclando nodos del DOM. Renderizará 100,000 registros a 60FPS constantes sin crashear el navegador.
- **Módulo Bronce**: `bronze_workspace.rs` y `bronze_table.rs` (Tabla virtualizada).
- **Módulo Plata**: `silver_workspace.rs` y el modal de `calculated_fields_tool.rs`.
- **Módulo Oro**: `gold_workspace.rs` con dashboards y gráficas aceleradas.

### Fase 5: Estilos (CSS Puro)
Los 4 archivos de estilos globales (`components.css`, `layout.css`, `tables.css`, `variables.css`) se trasladarán a la nueva carpeta `assets/` y se vincularán en el componente `App.rs` de Dioxus.

### Fase 6: Servidor de Desarrollo y Prueba de Wasm
Lanzar `dx serve` y cargar un archivo `.parquet` o `.csv` gigante en la Capa Bronce para atestiguar cómo la interfaz se mantiene fluida usando hilos secundarios de WebAssembly.
