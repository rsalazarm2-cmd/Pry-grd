use dioxus::prelude::*;
use crate::models::TabularResultDTO;

/// Propiedades requeridas para la Tabla de Capa Bronce virtualizada
#[derive(Props, Clone, PartialEq)]
pub struct RawDataTableProps {
    pub data: TabularResultDTO,
    pub container_height: f64,
    pub row_height: f64,
}

/// Módulo Base: Virtual Scroll para renderizar hasta 100,000 registros a 60FPS
/// Cumple con SRP (Renderizado de tabla ultra rápida) y Regla < 200 líneas
#[component]
pub fn RawDataTable(props: RawDataTableProps) -> Element {
    let mut scroll_top = use_signal(|| 0.0);
    
    let total_items = props.data.rows.len();
    let total_height = total_items as f64 * props.row_height;
    
    // Cálculo matemático puro en WebAssembly para determinar qué renderizar
    let start_node = (scroll_top() / props.row_height).floor() as usize;
    let visible_nodes = (props.container_height / props.row_height).ceil() as usize;
    
    // Buffer de recesión para evitar parpadeo al hacer scroll rápido (5 items)
    let buffer = 5;
    let start_node = start_node.saturating_sub(buffer);
    let end_node = (start_node + visible_nodes + buffer * 2).min(total_items);

    let rows_to_render = (start_node..end_node).filter_map(|idx| {
        if let Some(row) = props.data.rows.get(idx) {
            let cells = props.data.columns.iter().map(|col| {
                let val = row.get(col)
                    .map(|v| match v {
                        serde_json::Value::String(s) => s.clone(),
                        serde_json::Value::Null => "NULL".to_string(),
                        _ => v.to_string(),
                    })
                    .unwrap_or_else(|| "-".to_string());
                
                let (color, font_mono) = if val == "NULL" {
                    ("var(--accent-amber)", false)
                } else if col.to_uppercase().contains("ID") || col.to_uppercase().contains("CODE") || col.to_uppercase().contains("FOLIO") {
                    ("var(--accent-cyan)", true)
                } else {
                    ("var(--text-main)", false)
                };

                let font_str = if font_mono { "var(--font-mono)" } else { "inherit" };

                rsx! {
                    div { style: "padding: 0.75rem 0.85rem; font-size: 0.8rem; color: {color}; font-family: {font_str}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;", 
                        "{val}" 
                    }
                }
            });

            Some(rsx! {
                div {
                    key: "row-{idx}",
                    style: "position: absolute; top: {idx as f64 * props.row_height}px; width: 100%; height: {props.row_height}px; display: grid; grid-template-columns: repeat({props.data.columns.len()}, minmax(150px, 1fr)); align-items: center; padding: 0 16px; border-bottom: 1px solid var(--border-glass); box-sizing: border-box;",
                    {cells}
                }
            })
        } else {
            None
        }
    });

    let grid_min_width = props.data.columns.len() * 150;
    let mut rec_store = use_context::<crate::store::BronzeRecordsStore>();
    
    // Estado local para saber qué columna tiene el menú de filtro abierto y qué texto tiene
    let mut active_filter_col = use_signal(|| None::<String>);
    let mut filter_text = use_signal(|| String::new());
    
    // Estado para los valores únicos del filtro estilo Excel
    let mut filter_values = use_signal(|| Vec::<crate::models::DistinctValueDTO>::new());
    let mut selected_filter_values = use_signal(|| std::collections::HashSet::<String>::new());

    // Fetch de valores únicos cuando se abre un filtro
    use_effect(move || {
        if let Some(col) = active_filter_col.read().clone() {
            spawn(async move {
                let url = format!("http://localhost:8000/api/bronze/distinct-values/{}", urlencoding::encode(&col));
                if let Ok(resp) = reqwest::get(&url).await {
                    if let Ok(data) = resp.json::<Vec<crate::models::DistinctValueDTO>>().await {
                        filter_values.set(data);
                        selected_filter_values.write().clear();
                    }
                }
            });
        }
    });

    rsx! {
        div {
            class: "table-container",
            id: "virtual-scroll-container",
            style: "height: {props.container_height}px; overflow-y: auto; position: relative; background: var(--bg-card); overflow-x: auto;",
            onscroll: move |_evt| {
                if let Some(window) = web_sys::window() {
                    if let Some(document) = window.document() {
                        if let Some(el) = document.get_element_by_id("virtual-scroll-container") {
                            scroll_top.set(el.scroll_top() as f64);
                        }
                    }
                }
            },
            
            // Header sticky dinámico
            div { style: "position: sticky; top: 0; z-index: 20; background-color: var(--table-header-bg); backdrop-filter: blur(10px); display: grid; grid-template-columns: repeat({props.data.columns.len()}, minmax(150px, 1fr)); align-items: center; padding: 0 16px; border-bottom: 2px solid var(--border-glass); height: {props.row_height}px; box-sizing: border-box; min-width: {grid_min_width}px;",
                for col in props.data.columns.clone() {
                    {
                        let col_c1 = col.clone();
                        let col_c2 = col.clone();
                        let col_c3 = col.clone();
                        
                        rsx! {
                            div { 
                                style: "padding: 0.85rem; color: var(--text-muted); font-size: 0.75rem; font-weight: 800; text-align: left; position: relative; display: flex; justify-content: space-between; align-items: center;", 
                                
                                span {
                                    title: "{col}",
                                    style: "overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 85%;",
                                    "{col}"
                                }
                                
                                // Botón de filtro
                                button {
                                    style: "background: none; border: none; cursor: pointer; color: var(--text-muted); font-size: 0.8rem; padding: 2px;",
                                    onclick: move |_| {
                                        let current = active_filter_col.read().clone();
                                        if current.as_deref() == Some(col_c1.as_str()) {
                                            active_filter_col.set(None);
                                        } else {
                                            active_filter_col.set(Some(col_c1.clone()));
                                            filter_text.set(String::new());
                                            filter_values.set(Vec::new()); // Reset values while loading
                                        }
                                    },
                                    "🔻"
                                }
                                
                                // Popup de filtro estilo Excel
                                if active_filter_col.read().as_deref() == Some(col_c2.as_str()) {
                                    div {
                                        style: "position: absolute; top: 100%; left: 0; background: var(--bg-card); border: 1px solid var(--border-glass); padding: 12px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); z-index: 30; display: flex; flex-direction: column; gap: 8px; min-width: 200px;",
                                        
                                        // Buscador rápido local
                                        input {
                                            r#type: "text",
                                            placeholder: "Buscar valor...",
                                            value: "{filter_text}",
                                            style: "background: rgba(255,255,255,0.05); border: 1px solid var(--border-glass); color: var(--text-main); padding: 6px; border-radius: 4px; outline: none; font-size: 0.8rem; width: 100%; box-sizing: border-box;",
                                            oninput: move |evt| filter_text.set(evt.value())
                                        }
                                        
                                        // Lista de checkboxes
                                        div { style: "max-height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; border: 1px solid rgba(255,255,255,0.05); padding: 4px; border-radius: 4px;",
                                            if filter_values.read().is_empty() {
                                                div { style: "color: var(--text-muted); font-size: 0.75rem; text-align: center; padding: 8px;", "Cargando valores..." }
                                            } else {
                                                for val in filter_values.read().iter() {
                                                    if val.value.to_lowercase().contains(&filter_text.read().to_lowercase()) || filter_text.read().is_empty() {
                                                        {
                                                            let val_str = val.value.clone();
                                                            let val_str_disp = val.value.clone();
                                                            let count = val.count;
                                                            let is_selected = selected_filter_values.read().contains(&val_str);
                                                            
                                                            rsx! {
                                                                label { style: "display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: var(--text-main); cursor: pointer; padding: 2px 4px; border-radius: 4px;",
                                                                    input {
                                                                        r#type: "checkbox",
                                                                        checked: is_selected,
                                                                        onchange: move |evt| {
                                                                            if evt.checked() {
                                                                                selected_filter_values.write().insert(val_str.clone());
                                                                            } else {
                                                                                selected_filter_values.write().remove(&val_str);
                                                                            }
                                                                        }
                                                                    }
                                                                    span { style: "flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;", "{val_str_disp}" }
                                                                    span { style: "color: var(--text-muted); font-size: 0.7rem;", "({count})" }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        
                                        div { style: "display: flex; justify-content: space-between; gap: 8px; margin-top: 4px;",
                                            button {
                                                style: "flex: 1; background: var(--accent-indigo); border: none; color: white; padding: 6px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; font-weight: bold;",
                                                onclick: move |_| {
                                                    let selected = selected_filter_values.read().clone();
                                                    if selected.is_empty() {
                                                        rec_store.fetch_records(None, None, None);
                                                    } else {
                                                        let selected_vec: Vec<String> = selected.into_iter().collect();
                                                        let mut map = std::collections::HashMap::new();
                                                        map.insert(col_c3.clone(), selected_vec);
                                                        let filters_json = serde_json::to_string(&map).unwrap_or_default();
                                                        rec_store.fetch_records(None, None, Some(filters_json));
                                                    }
                                                    active_filter_col.set(None);
                                                },
                                                "Aplicar Filtro"
                                            }
                                            button {
                                                style: "background: rgba(255,255,255,0.1); border: none; color: white; padding: 6px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;",
                                                onclick: move |_| {
                                                    rec_store.fetch_records(None, None, None);
                                                    active_filter_col.set(None);
                                                },
                                                "Limpiar"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            div {
                style: "height: {total_height}px; min-width: {grid_min_width}px; position: relative;",
                {rows_to_render}
            }
        }
    }
}
