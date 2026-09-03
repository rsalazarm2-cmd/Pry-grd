use dioxus::prelude::*;
use crate::store::ProfilingStore;

#[component]
pub fn ProfilingDiagnostic() -> Element {
    let mut is_expanded = use_signal(|| true);
    let store = use_context::<ProfilingStore>();

    if (store.is_loading)() {
        return rsx! {
            div { class: "glass-card", style: "margin-bottom: 1.5rem; padding: 1.5rem; display: flex; justify-content: center; align-items: center; min-height: 200px;",
                span { style: "color: var(--accent-cyan); font-weight: 600;", "Cargando Profiling de DuckDB..." }
            }
        };
    }

    if let Some(err) = (store.error)() {
        return rsx! {
            div { class: "glass-card", style: "margin-bottom: 1.5rem; padding: 1.5rem; border-color: var(--accent-rose);",
                span { style: "color: var(--accent-rose); font-weight: 600;", "Error del Backend: {err}" }
            }
        };
    }

    let profile = (store.profile)();
    if profile.is_none() {
        return rsx! { div {} };
    }
    let p = profile.unwrap();
    let cols = p.columns.clone();

    let total_cols = p.total_columns;
    let constantes = p.constant_columns_count;
    let nulos = p.null_columns_count;
    let perfectas = p.perfect_columns_count;

    let table_rows = cols.into_iter().map(|c| {
        let status_lbl = c.status_label;
        let s_color = c.status_color;
        
        let null_pct = (c.null_percentage * 100.0).round();
        let n_color = if c.null_count > 0 { "amber" } else { "emerald" };
        let min_v = c.min_value.unwrap_or_else(|| "-".to_string());
        let max_v = c.max_value.unwrap_or_else(|| "-".to_string());
        
        rsx! {
            tr { key: "{c.column_name}", style: "border-bottom: 1px solid var(--border-glass);",
                td { style: "padding: 0.75rem 0.85rem; font-size: 0.8rem; font-weight: 600; color: var(--text-main);", "{c.column_name}" }
                td { style: "padding: 0.75rem 0.85rem;", span { style: "padding: 0.2rem 0.5rem; border-radius: 4px; background-color: color-mix(in srgb, var(--accent-indigo) 15%, transparent); color: var(--accent-indigo); font-size: 0.7rem; font-weight: 700;", "{c.data_type}" } }
                td { style: "padding: 0.75rem 0.85rem; font-size: 0.8rem; text-align: right; color: var(--accent-{n_color}); font-weight: 600;", "{c.null_count} ({null_pct}%)" }
                td { style: "padding: 0.75rem 0.85rem; font-size: 0.8rem; text-align: right; color: var(--text-main); font-weight: 600;", "{c.unique_count}" }
                td { style: "padding: 0.75rem 0.85rem; font-size: 0.8rem; text-align: right; color: var(--text-muted);", "{min_v}" }
                td { style: "padding: 0.75rem 0.85rem; font-size: 0.8rem; text-align: right; color: var(--text-muted);", "{max_v}" }
                td { style: "padding: 0.75rem 0.85rem; text-align: center;", span { style: "padding: 0.2rem 0.5rem; border-radius: 4px; background-color: color-mix(in srgb, var(--accent-{s_color}) 15%, transparent); color: var(--accent-{s_color}); font-size: 0.7rem; font-weight: 700;", "{status_lbl}" } }
            }
        }
    });

    rsx! {
        div { class: "glass-card", style: "margin-bottom: 1.5rem; padding: 1.5rem;",
            
            div { style: "display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: if is_expanded() { \"1rem\" } else { \"0\" };",
                div {
                    h3 { style: "font-size: 1.1rem; font-weight: 700; margin: 0 0 0.3rem 0; color: var(--accent-cyan); display: flex; align-items: center; gap: 0.5rem;",
                        "📈 Diagnóstico Exploratorio y Profiling Columnar de Calidad (Capa Bronce)"
                    }
                    p { style: "font-size: 0.85rem; color: var(--text-muted); margin: 0;",
                        "Análisis dinámico consumiendo metadatos directo desde DuckDB (API /api/bronze/profile)."
                    }
                }
                
                div { style: "display: flex; align-items: center; gap: 0.75rem;",
                    button {
                        onclick: move |_| is_expanded.set(!is_expanded()),
                        style: "background: none; border: 1px solid var(--border-glass); border-radius: 8px; color: var(--text-muted); cursor: pointer; padding: 0.4rem 0.6rem; display: flex; align-items: center; gap: 0.3rem; font-size: 0.8rem;",
                        if is_expanded() { "🔼 Plegar" } else { "🔽 Desplegar" }
                    }
                }
            }
            
            if is_expanded() {
                div { style: "display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;",
                    div { style: "padding: 1rem; border-radius: 12px; background-color: var(--bg-card); border: 1px solid var(--border-glass); display: flex; flex-direction: column; gap: 0.2rem;",
                        span { style: "font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;", "TOTAL COLUMNAS" }
                        span { style: "font-size: 1.5rem; font-weight: 800; color: var(--accent-cyan);", "{total_cols}" }
                        span { style: "font-size: 0.75rem; color: var(--text-muted);", "Detectadas en Parquet" }
                    }
                    div { style: "padding: 1rem; border-radius: 12px; background-color: color-mix(in srgb, var(--accent-rose) 5%, transparent); border: 1px solid color-mix(in srgb, var(--accent-rose) 20%, transparent); display: flex; flex-direction: column; gap: 0.2rem;",
                        span { style: "font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;", "CONSTANTES (INÚTILES)" }
                        span { style: "font-size: 1.5rem; font-weight: 800; color: var(--accent-rose);", "{constantes}" }
                        span { style: "font-size: 0.75rem; color: var(--accent-rose);", "Varianza Cero" }
                    }
                    div { style: "padding: 1rem; border-radius: 12px; background-color: color-mix(in srgb, var(--accent-amber) 5%, transparent); border: 1px solid color-mix(in srgb, var(--accent-amber) 20%, transparent); display: flex; flex-direction: column; gap: 0.2rem;",
                        span { style: "font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;", "CON NULOS (>0%)" }
                        span { style: "font-size: 1.5rem; font-weight: 800; color: var(--accent-amber);", "{nulos}" }
                        span { style: "font-size: 0.75rem; color: var(--accent-amber);", "Requieren Imputación" }
                    }
                    div { style: "padding: 1rem; border-radius: 12px; background-color: color-mix(in srgb, var(--accent-emerald) 5%, transparent); border: 1px solid color-mix(in srgb, var(--accent-emerald) 20%, transparent); display: flex; flex-direction: column; gap: 0.2rem;",
                        span { style: "font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;", "PERFECTAS (0 NULOS)" }
                        span { style: "font-size: 1.5rem; font-weight: 800; color: var(--accent-emerald);", "{perfectas}" }
                        span { style: "font-size: 0.75rem; color: var(--accent-emerald);", "Listas para Plata" }
                    }
                }
                
                div { style: "overflow-x: auto; border: 1px solid var(--border-glass); border-radius: 12px; max-height: 400px; background: var(--bg-card);",
                    table { class: "data-table", style: "width: 100%; border-collapse: separate; border-spacing: 0;",
                        thead { style: "position: sticky; top: 0; z-index: 10; background-color: var(--table-header-bg); backdrop-filter: blur(10px);",
                            tr { style: "border-bottom: 2px solid var(--border-glass);",
                                th { style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: left;", "COLUMNA" }
                                th { style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: left;", "TIPO BRONCE" }
                                th { style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: right;", "VALORES NULOS" }
                                th { style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: right;", "VALORES ÚNICOS" }
                                th { style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: right;", "MIN" }
                                th { style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: right;", "MAX" }
                                th { style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: center;", "ESTADO" }
                            }
                        }
                        tbody {
                            {table_rows}
                        }
                    }
                }
            }
        }
    }
}
