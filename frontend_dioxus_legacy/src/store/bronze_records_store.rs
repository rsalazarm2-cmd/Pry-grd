use dioxus::prelude::*;
use crate::models::TabularResultDTO;

#[derive(Clone, Copy)]
pub struct BronzeRecordsStore {
    pub records: Signal<Option<TabularResultDTO>>,
    pub is_loading: Signal<bool>,
    pub error: Signal<Option<String>>,
}

impl BronzeRecordsStore {
    pub fn new() -> Self {
        Self {
            records: Signal::new(None),
            is_loading: Signal::new(false),
            error: Signal::new(None),
        }
    }

    pub fn fetch_records(&mut self, column_name: Option<String>, search_term: Option<String>, filters_json: Option<String>) {
        let mut records = self.records;
        let mut is_loading = self.is_loading;
        let mut error = self.error;

        is_loading.set(true);
        error.set(None);

        spawn(async move {
            let mut url = "http://localhost:8000/api/bronze/records?limit=1000".to_string();
            
            if let Some(col) = column_name {
                url.push_str(&format!("&column_name={}", urlencoding::encode(&col)));
            }
            if let Some(term) = search_term {
                url.push_str(&format!("&search={}", urlencoding::encode(&term)));
            }
            if let Some(filters) = filters_json {
                url.push_str(&format!("&filters_json={}", urlencoding::encode(&filters)));
            }
            
            match reqwest::get(&url).await {
                Ok(resp) => {
                    if resp.status().is_success() {
                        if let Ok(data) = resp.json::<TabularResultDTO>().await {
                            records.set(Some(data));
                        } else {
                            error.set(Some("Error parseando respuesta JSON (TabularResultDTO)".to_string()));
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
