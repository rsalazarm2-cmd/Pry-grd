use dioxus::prelude::*;

#[derive(Clone, Copy)]
pub struct UiStore {
    pub active_project: Signal<Option<String>>,
    pub current_layer: Signal<String>,
}

impl UiStore {
    pub fn new() -> Self {
        Self {
            active_project: Signal::new(None),
            current_layer: Signal::new("bronze".to_string()),
        }
    }

    pub fn set_layer(&mut self, layer: &str) {
        *self.current_layer.write() = layer.to_string();
    }
}
