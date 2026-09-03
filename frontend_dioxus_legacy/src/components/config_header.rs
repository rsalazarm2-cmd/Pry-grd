use dioxus::prelude::*;
use crate::models::BronzeToSilverRulesDTO;

#[derive(PartialEq, Props, Clone)]
pub struct ConfigHeaderProps {
    pub rules: Signal<BronzeToSilverRulesDTO>,
}

#[component]
pub fn ConfigHeader(props: ConfigHeaderProps) -> Element {
    let mut rules = props.rules;

    let config_store = use_context::<crate::store::ConfigOptionsStore>();
    let duplicate_modes = (config_store.options)()
        .map(|o| o.duplicate_action_modes.clone())
        .unwrap_or_default();

    rsx! {
        div { style: "padding: 0; overflow: hidden;",
            
            // Título
            div { style: "padding: 1.2rem 1.5rem; background: var(--bg-modal-header); border-bottom: 1px solid var(--border-glass); display: flex; align-items: center; gap: 1rem;",
                div { style: "padding: 0.5rem; border-radius: 8px; background-color: rgba(245, 158, 11, 0.15); color: var(--accent-amber); font-size: 1.5rem;",
                    "🛡️"
                }
                div {
                    h3 { style: "font-size: 1.1rem; font-weight: 700; margin: 0; color: var(--text-main);", "Configuración de Transformación: Capa Bronce -> Capa Plata" }
                    p { style: "font-size: 0.82rem; color: var(--text-muted); margin: 0;", "Aplica Tipado, Saneamiento de Texto, y Genera silver.parquet" }
                }
            }

            // Switches
            div { style: "padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 1.25rem;",
                
                div { style: "display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; padding: 1rem; background-color: var(--bg-input); border-radius: 12px; border: 1px solid var(--border-glass);",
                    
                    // TRIM
                    label { style: "display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.82rem; color: var(--text-main); font-weight: 600;",
                        input {
                            r#type: "checkbox",
                            checked: rules().global_trim_spaces,
                            onchange: move |evt| rules.write().global_trim_spaces = evt.checked(),
                        }
                        span { "✂️ TRIM Global Espacios" }
                    }

                    // Tildes y Ñ
                    label { style: "display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.82rem; color: var(--text-main); font-weight: 600;",
                        input {
                            r#type: "checkbox",
                            checked: rules().global_clean_accents_and_n,
                            onchange: move |evt| rules.write().global_clean_accents_and_n = evt.checked(),
                        }
                        span { "📝 Normalizar Tildes & Ñ" }
                    }

                    // Caracteres Especiales
                    label { style: "display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.82rem; color: var(--text-main); font-weight: 600;",
                        input {
                            r#type: "checkbox",
                            checked: rules().global_clean_special_chars,
                            onchange: move |evt| rules.write().global_clean_special_chars = evt.checked(),
                        }
                        span { "🪄 Quitar Símbolos () /&%$#!;" }
                    }
                    
                    // Dos Puntos
                    label { style: "display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.82rem; color: var(--text-main); font-weight: 600;",
                        input {
                            r#type: "checkbox",
                            checked: rules().global_clean_colons,
                            onchange: move |evt| rules.write().global_clean_colons = evt.checked(),
                        }
                        span { "🏷️ Quitar Dos Puntos (:)" }
                    }

                    // Puntos
                    label { style: "display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.82rem; color: var(--text-main); font-weight: 600;",
                        input {
                            r#type: "checkbox",
                            checked: rules().global_clean_dots,
                            onchange: move |evt| rules.write().global_clean_dots = evt.checked(),
                        }
                        span { "🔴 Quitar Puntos (.) Global" }
                    }

                    // Comas
                    label { style: "display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.82rem; color: var(--text-main); font-weight: 600;",
                        input {
                            r#type: "checkbox",
                            checked: rules().global_clean_commas,
                            onchange: move |evt| rules.write().global_clean_commas = evt.checked(),
                        }
                        span { "🟡 Quitar Comas (,) Global" }
                    }
                }

                // Control Forense
                div { style: "display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; border-radius: 10px; background-color: rgba(245, 158, 11, 0.08); border: 1px solid var(--accent-amber); flex-wrap: wrap; gap: 0.75rem;",
                    div { style: "display: flex; align-items: center; gap: 0.5rem; color: var(--accent-amber); font-weight: 700; font-size: 0.85rem;",
                        "⚠️ Tratamiento Forense de Duplicados & Datos Trampa:"
                    }
                    select {
                        value: "{rules().duplicate_action_mode}",
                        onchange: move |evt| rules.write().duplicate_action_mode = evt.value(),
                        style: "padding: 0.45rem 0.8rem; border-radius: 6px; background-color: var(--bg-input-select); border: 1px solid var(--accent-amber); color: var(--text-main); font-weight: 600; font-size: 0.82rem;",
                        for opt in duplicate_modes.iter() {
                            option { key: "{opt.id}", value: "{opt.id}", "{opt.label}" }
                        }
                    }
                }
            }
        }
    }
}
