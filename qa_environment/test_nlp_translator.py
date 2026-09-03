import sys
import os

# Agregamos src al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from src.ai_translator.infrastructure.nlp_semantic_translator import NLPSemanticTranslator
from src.ai_translator.application.auto_map_columns_use_case import AutoMapColumnsUseCase
from src.ai_translator.domain.models import TargetSchemaDefinitionDTO

def main():
    print("Iniciando modelo NLP de traducción semántica (esto puede tardar unos segundos la primera vez para descargar el modelo)...")
    translator = NLPSemanticTranslator()
    use_case = AutoMapColumnsUseCase(translator)

    # 1. Columnas crudas extraídas de un CSV típico de ERP en español (con nombres "feos")
    source_columns = [
        "fecha_creacion_trx",
        "monto_debe",
        "monto_haber",
        "desc_operacion",
        "libro_mayor",
        "codigo_cuenta",
        "moneda_origen",
        "usuario_sistema_legacy", # No debería mapearse a nada útil
        "estado_fila"
    ]

    print("\nColumnas de origen:", source_columns)

    # 2. Esquema estándar de la Capa Oro y sus descripciones semánticas
    target_schema = TargetSchemaDefinitionDTO(
        schema_map={
            "CREATION_DATE": "Fecha de creacion o registro de la transaccion",
            "ACCOUNTED_DR": "Monto de debito, cargo o monto debe",
            "ACCOUNTED_CR": "Monto de credito, abono o monto haber",
            "JE_DESCRIPTION": "Descripcion, concepto o glosa de la operacion",
            "LEDGER_NAME": "Libro contable, libro mayor o compania",
            "CODE_COMBINATION": "Codigo de cuenta contable o segmento de cuenta",
            "CURRENCY": "Moneda de origen o divisa"
        }
    )

    print("\nTraduciendo...")
    result = use_case.execute(source_columns, target_schema, threshold=0.4)

    print("\n=== RESULTADO DE MAPEO SEMÁNTICO ===")
    print("Columnas mapeadas exitosamente:")
    for src, tgt in result.suggested_mapping.items():
        score = result.confidence_scores.get(src, 0.0)
        print(f"  {src.ljust(25)} => {tgt.ljust(20)} (Confianza: {score:.2f})")

    print("\nColumnas ignoradas (no relevantes):")
    for unmapped in result.unmapped_columns:
        print(f"  - {unmapped}")

if __name__ == "__main__":
    main()
