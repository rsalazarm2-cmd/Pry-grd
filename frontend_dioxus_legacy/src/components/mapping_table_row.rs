use dioxus::prelude::*;
use crate::models::{BronzeToSilverRulesDTO, ConfigOptionDTO};

#[derive(PartialEq, Props, Clone)]
pub struct MappingTableRowProps {
    pub col: String,
    pub rules: Signal<BronzeToSilverRulesDTO>,
    pub data_types: Vec<ConfigOptionDTO>,
}

#[component]
pub fn MappingTableRow(props: MappingTableRowProps) -> Element {
    let mut rules = props.rules;
    let col = &props.col;
    let current_rule = rules.read().column_rules.get(col).cloned().unwrap_or_default();
    
    let col_clone = col.clone();
    let col_clone2 = col.clone();
    let col_clone3 = col.clone();
    let col_clone_null = col.clone();
    let col_clone4 = col.clone();
    let col_clone5 = col.clone();

    rsx! {
        tr { key: "{col}", style: if !current_rule.include_in_silver { "opacity: 0.4;" } else { "" },
            td { style: "text-align: center;",
                input {
                    r#type: "checkbox",
                    checked: current_rule.include_in_silver,
                    onchange: move |evt| {
                        rules.write().column_rules.entry(col_clone.clone()).or_default().include_in_silver = evt.checked();
                    }
                }
            }
            td { style: "font-weight: 600; color: var(--text-main);", "{col}" }
            td {
                input {
                    r#type: "text",
                    disabled: !current_rule.include_in_silver,
                    value: current_rule.new_column_name.unwrap_or_default(),
                    placeholder: "Ej: JE_CATEGORY",
                    style: "width: 100%; padding: 0.4rem 0.6rem; border-radius: 6px; background-color: var(--bg-input); border: 1px solid var(--border-glass); color: var(--text-main); font-size: 0.85rem;",
                    onchange: move |evt| {
                        let val = evt.value();
                        rules.write().column_rules.entry(col_clone2.clone()).or_default().new_column_name = if val.is_empty() { None } else { Some(val) };
                    }
                }
            }
            td {
                select {
                    disabled: !current_rule.include_in_silver,
                    value: current_rule.target_data_type.unwrap_or_else(|| "VARCHAR".to_string()),
                    style: "width: 100%; padding: 0.4rem; border-radius: 6px; background-color: var(--bg-input-select); border: 1px solid var(--border-glass); color: var(--text-main); font-size: 0.85rem;",
                    onchange: move |evt| {
                        rules.write().column_rules.entry(col_clone3.clone()).or_default().target_data_type = Some(evt.value());
                    },
                    for opt in props.data_types.iter() {
                        option { key: "{opt.id}", value: "{opt.id}", "{opt.label}" }
                    }
                }
            }
            td { style: "text-align: center;",
                label { style: "display: flex; align-items: center; justify-content: center; gap: 0.25rem; font-size: 0.8rem; cursor: pointer; color: var(--text-muted);",
                    input {
                        r#type: "checkbox",
                        disabled: !current_rule.include_in_silver,
                        checked: current_rule.convert_to_category,
                        onchange: move |evt| {
                            rules.write().column_rules.entry(col_clone_null.clone()).or_default().convert_to_category = evt.checked();
                        }
                    }
                    span { "ENUM" }
                }
            }
            td { style: "font-size: 0.8rem; color: var(--text-muted); text-align: center;",
                "Auto (Backend)"
            }
            td {
                div { style: "display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;",
                    if current_rule.has_dots {
                        label { style: "display: flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; cursor: pointer; color: var(--text-muted);",
                            input {
                                r#type: "checkbox",
                                disabled: !current_rule.include_in_silver,
                                checked: current_rule.clean_dots.unwrap_or(false),
                                onchange: move |evt| {
                                    rules.write().column_rules.entry(col_clone4.clone()).or_default().clean_dots = Some(evt.checked());
                                }
                            }
                            "🔴 Puntos"
                        }
                    }
                    if current_rule.has_commas {
                        label { style: "display: flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; cursor: pointer; color: var(--text-muted);",
                            input {
                                r#type: "checkbox",
                                disabled: !current_rule.include_in_silver,
                                checked: current_rule.clean_commas.unwrap_or(false),
                                onchange: move |evt| {
                                    rules.write().column_rules.entry(col_clone5.clone()).or_default().clean_commas = Some(evt.checked());
                                }
                            }
                            "🟡 Comas"
                        }
                    }
                }
            }
        }
    }
}
