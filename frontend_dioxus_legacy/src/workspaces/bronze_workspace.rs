use dioxus::prelude::*;
use crate::components::raw_data_table::RawDataTable;
use crate::models::{AsientoContable, BronzeToSilverRulesDTO, SilverTransformationResultDTO};
use crate::api::procesar_plata;
use crate::components::config_header::ConfigHeader;
use crate::components::mapping_table::MappingTable;
use crate::components::profiling_diagnostic::ProfilingDiagnostic;

use crate::store::BronzeRecordsStore;

/// Workspace de la Capa Bronce (Data Lake)
#[component]
pub fn BronzeWorkspace() -> Element {
    let records_store = use_context::<BronzeRecordsStore>();

    let prof_store = use_context::<crate::store::ProfilingStore>();
    
    // Obtener columnas reales desde el backend (Profiling)
    let columns = (prof_store.profile)()
        .as_ref()
        .map(|p| p.columns.iter().map(|c| c.column_name.clone()).collect::<Vec<_>>())
        .unwrap_or_default();

    // Estado para la transformación de Bronce a Plata
    let mut rules = use_signal(BronzeToSilverRulesDTO::default);
    let mut is_processing = use_signal(|| false);
    let mut is_suggesting = use_signal(|| true); // Inicia en true porque lo corremos al inicio
    let mut result = use_signal(|| None::<SilverTransformationResultDTO>);
    let mut error_msg = use_signal(|| None::<String>);
    let mut show_config = use_signal(|| false);

    // 🚀 Auto-ejecutar el mapeo semántico (IA) en segundo plano al cargar el Workspace
    use_effect(move || {
        // Solo lo corremos una vez si está vacío
        if rules.read().column_rules.is_empty() {
            spawn(async move {
                is_suggesting.set(true);
                let url = "http://localhost:8000/api/bronze/suggest-mapping";
                if let Ok(resp) = reqwest::get(url).await {
                    if let Ok(suggested_rules) = resp.json::<BronzeToSilverRulesDTO>().await {
                        rules.set(suggested_rules);
                    }
                }
                is_suggesting.set(false);
            });
        }
    });

    let handle_process = move |_| {
        is_processing.set(true);
        error_msg.set(None);
        result.set(None);
        
        let current_rules = rules().clone();
        
        // Spawn async task para llamar al backend
        spawn(async move {
            let project_id = "default_project";
            match procesar_plata(project_id, current_rules).await {
                Ok(res) => result.set(Some(res)),
                Err(e) => error_msg.set(Some(e)),
            }
            is_processing.set(false);
        });
    };

    rsx! {
        div { class: "app-container", style: "display: flex; flex-direction: column; gap: 1.5rem;",
            
            // Header del Workspace Bronce
            div { style: "display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;",
                h2 { style: "font-size: 1.5rem; font-weight: 700; color: var(--text-main); margin: 0;", "Capa Bronce: Data Lake" }
                
                div { style: "display: flex; align-items: center; gap: 0.75rem;",
                    button {
                        class: "btn-primary",
                        style: "background: linear-gradient(135deg, #a855f7, #6366f1); font-size: 0.95rem; padding: 0.5rem 1.25rem;",
                        onclick: move |_| {
                            show_config.set(!show_config());
                        },
                        if show_config() { "🔽 Ocultar Configuración" } else { "⚙️ Configurar Limpieza y Tipado" }
                    }
                }
            }

            // Alerta de Error
            if let Some(err) = error_msg() {
                div { style: "padding: 1rem; background-color: rgba(239, 68, 68, 0.1); border: 1px solid var(--accent-rose); border-radius: 8px; color: var(--accent-rose); font-weight: 600;",
                    "❌ Error: {err}"
                }
            }

            // 📊 Panel de Análisis (Solo si es exitoso)
            if let Some(res) = result() {
                div { class: "glass-card", style: "padding: 1.5rem; border: 1px solid var(--accent-emerald); background-color: rgba(16, 185, 129, 0.05); margin-bottom: 1rem;",
                    h3 { style: "font-size: 1.2rem; font-weight: 700; margin: 0 0 1rem 0; color: var(--accent-emerald); display: flex; align-items: center; gap: 0.5rem;",
                        "✅ Capa Plata Generada Exitosamente"
                    }
                    div { style: "display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;",
                        div { style: "padding: 1rem; border-radius: 12px; background-color: var(--bg-card); border: 1px solid var(--border-glass); display: flex; flex-direction: column; align-items: center; justify-content: center;",
                            span { style: "font-size: 1.8rem; font-weight: 800; color: var(--accent-indigo);", "{res.silver_row_count}" }
                            span { style: "font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;", "Filas Procesadas" }
                        }
                        div { style: "padding: 1rem; border-radius: 12px; background-color: var(--bg-card); border: 1px solid var(--border-glass); display: flex; flex-direction: column; align-items: center; justify-content: center;",
                            span { style: "font-size: 1.8rem; font-weight: 800; color: var(--accent-emerald);", "{res.nulls_removed}" }
                            span { style: "font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;", "Nulos Limpiados" }
                        }
                        div { style: "padding: 1rem; border-radius: 12px; background-color: var(--bg-card); border: 1px solid var(--border-glass); display: flex; flex-direction: column; align-items: center; justify-content: center;",
                            span { style: "font-size: 1.8rem; font-weight: 800; color: var(--accent-amber);", "{res.traps_detected}" }
                            span { style: "font-size: 0.8rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;", "Trampas Forenses" }
                        }
                    }
                }
            }

            // 📈 Panel de Diagnóstico Exploratorio
            ProfilingDiagnostic {}

            // ⚙️ Panel de Configuración de Transformación
            if show_config() {
                div { class: "glass-card", style: "padding: 0; overflow: hidden; display: flex; flex-direction: column;",
                    // 1. Cabecera de Configuración
                    ConfigHeader { rules: rules }
                    
                    // 2. Tabla de Mapeo Semántico
                    div { style: "padding: 0 1.5rem 1.5rem 1.5rem;",
                        MappingTable { columns: columns.clone(), rules: rules }

                        // Botón para procesar
                        div { style: "display: flex; justify-content: flex-end; margin-top: 1.5rem;",
                            button {
                                class: "btn-primary",
                                style: "background: linear-gradient(135deg, #10b981, #059669); font-size: 1.1rem; padding: 0.75rem 2rem;",
                                disabled: is_processing(),
                                onclick: handle_process,
                                if is_processing() {
                                    "⏳ Procesando en Backend..."
                                } else {
                                    "🚀 Ejecutar Pipeline Bronce -> Plata"
                                }
                            }
                        }
                    }
                }
            }
            
            // Tabla Bronce Pura
            div { class: "glass-card",
                div { style: "margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;",
                    div { style: "font-size: 1rem; font-weight: 600; color: var(--text-main);", "Datos sin procesar (Raw Data)" }
                    if let Some(r) = (records_store.records)() {
                        div { style: "font-size: 0.875rem; color: var(--text-muted);", "Mostrando {r.total_returned} asientos extraídos." }
                    }
                }
                
                if (records_store.is_loading)() {
                    div { style: "display: flex; justify-content: center; align-items: center; min-height: 400px; width: 100%;",
                        span { style: "color: var(--accent-cyan); font-weight: 600;", "Cargando Dataset de DuckDB..." }
                    }
                } else if let Some(err) = (records_store.error)() {
                    div { style: "padding: 1.5rem; border-color: var(--accent-rose);",
                        span { style: "color: var(--accent-rose); font-weight: 600;", "Error del Backend: {err}" }
                    }
                } else if let Some(r) = (records_store.records)() {
                    RawDataTable {
                        data: r,
                        container_height: 400.0,
                        row_height: 48.0,
                    }
                }
            }
        }
    }
}
