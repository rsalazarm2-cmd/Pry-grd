use dioxus::prelude::*;

mod store;
mod models;
mod js_interop;
mod components;
mod api;
mod workspaces;

use store::{UiStore, RecipeStore, ProfilingStore, BronzeRecordsStore, ConfigOptionsStore};
use workspaces::bronze_workspace::BronzeWorkspace;
use workspaces::silver_workspace::SilverWorkspace;

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    use_context_provider(|| UiStore::new());
    use_context_provider(|| RecipeStore::new());
    use_context_provider(|| ProfilingStore::new());
    use_context_provider(|| BronzeRecordsStore::new());
    use_context_provider(|| ConfigOptionsStore::new());

    let mut ui = use_context::<UiStore>();
    
    let mut prof_store = use_context::<ProfilingStore>();
    let mut records_store = use_context::<BronzeRecordsStore>();
    let mut config_store = use_context::<ConfigOptionsStore>();
    
    // Al cargar la app, vamos a hacer fetch del profiling y de los records
    use_effect(move || {
        prof_store.fetch_profile();
        spawn(async move {
            config_store.fetch_options().await;
        });
        if (ui.current_layer)() == "bronze" {
            records_store.fetch_records(None, None, None);
        }
    });
    
    rsx! {
        link { rel: "stylesheet", href: "variables.css" }
        link { rel: "stylesheet", href: "layout.css" }
        link { rel: "stylesheet", href: "components.css" }
        link { rel: "stylesheet", href: "tables.css" }
        
        div { class: "app-container",
            // Header Global
            div { class: "app-header",
                div { class: "brand",
                    div { class: "brand-icon", "🛡️" }
                    div {
                        h1 { class: "brand-title", "Auditoría Forense" }
                        div { class: "brand-subtitle", "Medallion Architecture Wasm" }
                    }
                }
            }
            
            // Navegación (Tabs)
            div { class: "tabs-nav",
                button {
                    class: if (ui.current_layer)() == "bronze" { "tab-btn active" } else { "tab-btn" },
                    onclick: move |_| ui.set_layer("bronze"),
                    "Capa Bronce"
                }
                button {
                    class: if (ui.current_layer)() == "silver" { "tab-btn active" } else { "tab-btn" },
                    onclick: move |_| ui.set_layer("silver"),
                    "Capa Plata"
                }
                button {
                    class: if (ui.current_layer)() == "gold" { "tab-btn active" } else { "tab-btn" },
                    onclick: move |_| ui.set_layer("gold"),
                    "Capa Oro"
                }
            }
            
            // Renderizado condicional del Workspace según el State
            if (ui.current_layer)() == "bronze" {
                BronzeWorkspace {}
            } else if (ui.current_layer)() == "silver" {
                SilverWorkspace {}
            } else if (ui.current_layer)() == "gold" {
                div { class: "glass-card", "Workspace Oro (En Construcción)..." }
            }
        }
    }
}
