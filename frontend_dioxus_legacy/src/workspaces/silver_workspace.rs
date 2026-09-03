use dioxus::prelude::*;
use crate::store::SilverRecordsStore;
use crate::components::raw_data_table::RawDataTable;

#[component]
pub fn SilverWorkspace() -> Element {
    // Inicializar el store global
    use_context_provider(|| SilverRecordsStore::new());
    
    let mut store = use_context::<SilverRecordsStore>();
    
    // Cargar datos automáticamente al montar el componente
    use_effect(move || {
        store.fetch_records();
    });

    rsx! {
        div { class: "app-container", style: "display: flex; flex-direction: column; gap: 1rem;",
            
            // Título principal
            div { style: "display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;",
                h2 { style: "font-size: 1.5rem; font-weight: 700; color: var(--text-main); margin: 0;", "Capa Plata (Silver): Datos Limpios y Listos" }
                
                button {
                    class: "btn-primary",
                    style: "background: linear-gradient(135deg, #f59e0b, #d97706); font-size: 0.95rem; padding: 0.5rem 1.25rem;",
                    "🏆 Procesar Plata -> Generar Capa Oro"
                }
            }

            // Tabla Plata
            div { class: "glass-card",
                div { style: "margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;",
                    div { style: "font-size: 1rem; font-weight: 600; color: var(--text-main);", "Dataset Estandarizado (silver.parquet)" }
                    if let Some(r) = (store.records)() {
                        div { style: "font-size: 0.875rem; color: var(--text-muted);", "Mostrando {r.total_returned} asientos limpios." }
                    }
                }
                
                if (store.is_loading)() {
                    div { style: "display: flex; justify-content: center; align-items: center; min-height: 400px; width: 100%;",
                        span { style: "color: var(--accent-amber); font-weight: 600;", "Cargando Capa Plata (Silver)..." }
                    }
                } else if let Some(err) = (store.error)() {
                    div { style: "padding: 1.5rem; border-color: var(--accent-rose);",
                        span { style: "color: var(--accent-rose); font-weight: 600;", "Error del Backend: {err}" }
                    }
                } else if let Some(r) = (store.records)() {
                    RawDataTable {
                        data: r,
                        container_height: 500.0,
                        row_height: 48.0,
                    }
                } else {
                    div { style: "padding: 1.5rem; text-align: center;",
                        span { style: "color: var(--text-muted); font-style: italic;", "No hay datos disponibles en la capa Plata. Genera la Capa Plata desde Bronce." }
                    }
                }
            }
        }
    }
}
