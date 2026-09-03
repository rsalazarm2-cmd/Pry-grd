use dioxus::prelude::*;
use crate::models::DatasetProfileDTO;

#[derive(Clone, Copy)]
pub struct ProfilingStore {
    pub profile: Signal<Option<DatasetProfileDTO>>,
    pub is_loading: Signal<bool>,
    pub error: Signal<Option<String>>,
}

impl ProfilingStore {
    pub fn new() -> Self {
        Self {
            profile: Signal::new(None),
            is_loading: Signal::new(false),
            error: Signal::new(None),
        }
    }

    pub fn fetch_profile(&mut self) {
        let mut profile = self.profile;
        let mut is_loading = self.is_loading;
        let mut error = self.error;

        is_loading.set(true);
        error.set(None);

        spawn(async move {
            let url = "http://localhost:8000/api/bronze/profile";
            match reqwest::get(url).await {
                Ok(resp) => {
                    if resp.status().is_success() {
                        if let Ok(data) = resp.json::<DatasetProfileDTO>().await {
                            profile.set(Some(data));
                        } else {
                            error.set(Some("Error parseando respuesta JSON (DatasetProfileDTO)".to_string()));
                        }
                    } else {
                        error.set(Some(format!("Error del servidor: {}", resp.status())));
                    }
                }
                Err(e) => {
                    error.set(Some(format!("Error de red: {}", e)));
                }
            }
            is_loading.set(false);
        });
    }
}
