use dioxus::prelude::*;
use crate::models::BronzeToSilverRulesDTO;
use crate::components::mapping_table_row::MappingTableRow;

#[derive(PartialEq, Props, Clone)]
pub struct MappingTableProps {
    pub columns: Vec<String>,
    pub rules: Signal<BronzeToSilverRulesDTO>,
}

#[component]
pub fn MappingTable(props: MappingTableProps) -> Element {
    let mut search_query = use_signal(String::new);
    let mut rules = props.rules;
    
    let config_store = use_context::<crate::store::ConfigOptionsStore>();
    
    let data_types = (config_store.options)()
        .map(|o| o.available_data_types.clone())
        .unwrap_or_default();

    let filtered_columns = props.columns.iter().filter(|col| {
        let q = search_query().to_lowercase();
        if q.is_empty() {
            return true;
        }
        let col_lower = col.to_lowercase();
        let current_rule = rules.read().column_rules.get(*col).cloned().unwrap_or_default();
        let alias_lower = current_rule.new_column_name.unwrap_or_default().to_lowercase();
        
        col_lower.contains(&q) || alias_lower.contains(&q)
    }).cloned().collect::<Vec<_>>();

    rsx! {
        div { style: "padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem;",
            
            // Título de la tabla y buscador
            div { style: "display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding-bottom: 1rem;",
                div { style: "display: flex; align-items: center; gap: 0.75rem;",
                    div { style: "padding: 0.5rem; border-radius: 8px; background-color: rgba(99, 102, 241, 0.15); color: var(--accent-indigo); font-size: 1.25rem;",
                        "📋"
                    }
                    div {
                        h3 { style: "font-size: 1.1rem; font-weight: 700; margin: 0; color: var(--text-main);", "Semantic Mapping Tool" }
                        p { style: "font-size: 0.82rem; color: var(--text-muted); margin: 0;", "Define las reglas de negocio, tipado y saneamiento por cada columna." }
                    }
                }
                
                div { style: "display: flex; align-items: center; gap: 1rem;",
                    div { style: "display: flex; gap: 0.5rem;",
                        button {
                            class: "btn-secondary",
                            style: "background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.4); color: var(--accent-emerald); font-size: 0.75rem; padding: 0.4rem 0.8rem;",
                            onclick: move |_| {
                                spawn(async move {
                                    let url = "http://localhost:8000/api/bronze/suggest-mapping";
                                    if let Ok(resp) = reqwest::get(url).await {
                                        if let Ok(suggested_rules) = resp.json::<crate::models::BronzeToSilverRulesDTO>().await {
                                            let mut w = rules.write();
                                            for (col, rule) in suggested_rules.column_rules {
                                                w.column_rules.entry(col).or_default().new_column_name = rule.new_column_name;
                                            }
                                        }
                                    }
                                });
                            },
                            "🌐 Traducir Todo a Español"
                        }
                        button {
                            class: "btn-secondary",
                            style: "background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); color: var(--accent-rose); font-size: 0.75rem; padding: 0.4rem 0.8rem;",
                            onclick: move |_| {
                                let mut w = rules.write();
                                for (_col, rule) in w.column_rules.iter_mut() {
                                    rule.new_column_name = None;
                                }
                            },
                            "↩️ Usar Nombres Originales"
                        }
                        button {
                            class: "btn-secondary",
                            style: "background-color: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.4); color: var(--accent-amber); font-size: 0.75rem; padding: 0.4rem 0.8rem;",
                            onclick: move |_| {
                                spawn(async move {
                                    let url = "http://localhost:8000/api/bronze/suggest-mapping";
                                    if let Ok(resp) = reqwest::get(url).await {
                                        if let Ok(suggested_rules) = resp.json::<crate::models::BronzeToSilverRulesDTO>().await {
                                            let mut w = rules.write();
                                            for (col, rule) in suggested_rules.column_rules {
                                                w.column_rules.insert(col, rule);
                                            }
                                        }
                                    }
                                });
                            },
                            "✨ Regenerar Mapeo (Forzar IA)"
                        }
                    }
                    div { style: "position: relative; width: 300px;",
                        input {
                            r#type: "text",
                            placeholder: "🔍 Filtrar columnas...",
                            value: "{search_query}",
                            oninput: move |evt| search_query.set(evt.value()),
                            style: "width: 100%; padding: 0.5rem 1rem; border-radius: 8px; background-color: var(--bg-input); border: 1px solid var(--border-glass); color: var(--text-main); font-size: 0.85rem;"
                        }
                    }
                }
            }

            // Contenedor de la Tabla
            div { style: "overflow-x: auto;",
                table { class: "minimalist-table",
                    thead {
                        tr {
                            th { style: "width: 5%; text-align: center;", "INCLUIR" }
                            th { "COLUMNA ORIGINAL" }
                            th { "ALIAS PLATA (Opcional)" }
                            th { "TIPO DATO PLATA" }
                            th { style: "text-align: center;", "ENUM" }
                            th { "TRATAMIENTO DE NULOS" }
                            th { "REGLAS ESPECÍFICAS" }
                        }
                    }
                    tbody {
                        for col in filtered_columns.iter() {
                            MappingTableRow {
                                col: col.clone(),
                                rules: rules,
                                data_types: data_types.clone(),
                            }
                        }
                    }
                }
            }
        }
    }
}
