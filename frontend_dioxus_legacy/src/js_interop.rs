use wasm_bindgen::prelude::*;
use serde_wasm_bindgen::{from_value, to_value};
use crate::models::AsientoContable;

/// Función expuesta a JavaScript para parsear miles de registros instantáneamente.
/// Usa serde-wasm-bindgen (El Arma Secreta) para deserialización sin pasar por JSON string.
#[wasm_bindgen]
pub fn procesar_asientos_js(val: JsValue) -> Result<usize, JsValue> {
    let asientos: Vec<AsientoContable> = from_value(val)
        .map_err(|e| JsValue::from_str(&format!("Error de deserialización Wasm: {}", e)))?;
    
    // Aquí procesaríamos el array en memoria Wasm (ej. guardarlo en Dioxus Signals).
    // Por ahora retornamos el contador de filas parseadas exitosamente.
    Ok(asientos.len())
}

/// Ejecuta filtrado de auditoría forense masivo usando CPU en Rust
#[wasm_bindgen]
pub fn extraer_descuadrados_js(val: JsValue, umbral: f64) -> Result<JsValue, JsValue> {
    // 1. JS a Rust a máxima velocidad
    let asientos: Vec<AsientoContable> = from_value(val)
        .map_err(|e| JsValue::from_str(&format!("Error leyendo datos JS: {}", e)))?;
        
    // 2. Procesamiento puro en Wasm (sin bloqueos de UI)
    let descuadrados: Vec<AsientoContable> = asientos
        .into_iter()
        .filter(|a| a.diferencia.abs() > umbral)
        .collect();
        
    // 3. Rust a JS a máxima velocidad
    to_value(&descuadrados)
        .map_err(|e| JsValue::from_str(&format!("Error exportando a JS: {}", e)))
}
