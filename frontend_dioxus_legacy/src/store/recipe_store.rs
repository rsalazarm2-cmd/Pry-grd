use dioxus::prelude::*;

#[derive(Clone, Debug, PartialEq)]
pub struct TransformationRule {
    pub rule_type: String,
    pub column: String,
    pub target: Option<String>,
}

#[derive(Clone, Copy)]
pub struct RecipeStore {
    pub rules: Signal<Vec<TransformationRule>>,
}

impl RecipeStore {
    pub fn new() -> Self {
        Self {
            rules: Signal::new(Vec::new()),
        }
    }

    pub fn add_rule(&mut self, rule: TransformationRule) {
        self.rules.write().push(rule);
    }
}
