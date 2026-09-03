use crate::models::{BronzeToSilverRulesDTO, SilverTransformationResultDTO};

pub async fn procesar_plata(project_id: &str, rules: BronzeToSilverRulesDTO) -> Result<SilverTransformationResultDTO, String> {
    let client = reqwest::Client::new();
    let url = "http://localhost:8000/api/silver/transform".to_string();
    
    let res = client.post(&url)
        .json(&rules)
        .send()
        .await
        .map_err(|e| format!("Error de red al conectar con el backend: {}", e))?;
        
    if res.status().is_success() {
        let result: SilverTransformationResultDTO = res.json()
            .await
            .map_err(|e| format!("Error parseando respuesta JSON del servidor: {}", e))?;
        Ok(result)
    } else {
        let err_text = res.text().await.unwrap_or_default();
        Err(format!("Fallo del Motor de Base de Datos: {}", err_text))
    }
}
