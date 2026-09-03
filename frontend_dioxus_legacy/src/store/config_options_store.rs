use dioxus::prelude::*;
use crate::models::SystemConfigOptionsDTO;

#[derive(Clone, Copy)]
pub struct ConfigOptionsStore {
    pub options: Signal<Option<SystemConfigOptionsDTO>>,
    pub is_loading: Signal<bool>,
    pub error: Signal<Option<String>>,
}

impl ConfigOptionsStore {
    pub fn new() -> Self {
        Self {
            options: Signal::new(None),
            is_loading: Signal::new(false),
            error: Signal::new(None),
        }
    }

    pub async fn fetch_options(&mut self) {
        self.is_loading.set(true);
        self.error.set(None);

        let url = "http://localhost:8000/api/bronze/config-options";
        match reqwest::get(url).await {
            Ok(resp) => {
                if resp.status().is_success() {
                    if let Ok(data) = resp.json::<SystemConfigOptionsDTO>().await {
                        self.options.set(Some(data));
                    } else {
                        self.error.set(Some("Error al decodificar las opciones del diccionario de datos.".to_string()));
                    }
                } else {
                    self.error.set(Some(format!("Error del servidor: {}", resp.status())));
                }
            }
            Err(e) => {
                self.error.set(Some(format!("Error de conexión: {}", e)));
            }
        }
        self.is_loading.set(false);
    }
}
