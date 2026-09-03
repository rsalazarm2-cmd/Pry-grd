use dioxus::prelude::*;
use crate::models::TabularResultDTO;
use reqwest;

#[derive(Clone, Copy)]
pub struct SilverRecordsStore {
    pub records: Signal<Option<TabularResultDTO>>,
    pub is_loading: Signal<bool>,
    pub error: Signal<Option<String>>,
}

impl SilverRecordsStore {
    pub fn new() -> Self {
        Self {
            records: Signal::new(None),
            is_loading: Signal::new(false),
            error: Signal::new(None),
        }
    }

    pub fn fetch_records(&mut self) {
        let mut records = self.records;
        let mut is_loading = self.is_loading;
        let mut error = self.error;

        is_loading.set(true);
        error.set(None);
        records.set(None);

        spawn(async move {
            let url = "http://localhost:8000/api/silver/records?limit=1000";
            
            match reqwest::get(url).await {
                Ok(res) => {
                    if res.status().is_success() {
                        match res.json::<TabularResultDTO>().await {
                            Ok(data) => records.set(Some(data)),
                            Err(e) => error.set(Some(format!("Error parseando JSON: {}", e))),
                        }
                    } else {
                        let text = res.text().await.unwrap_or_default();
                        error.set(Some(format!("Error del servidor: {}", text)));
                    }
                }
                Err(e) => {
                    error.set(Some(format!("Error de conexión: {}", e)));
                }
            }
            
            is_loading.set(false);
        });
    }
}
