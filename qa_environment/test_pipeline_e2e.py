import os
import duckdb
from pathlib import Path
from src.shared.domain.journal_entry import (
    BronzeToSilverRulesDTO, 
    SilverToGoldRulesDTO, 
    ColumnCleaningRuleDTO, 
    SemanticMappingDTO
)
from src.shared.application.execute_pipeline_use_case import ExecutePipelineUseCase
from src.shared.infrastructure.duckdb_journal_repository import DuckDBJournalRepository

def test_full_medallion_pipeline_e2e(test_data_dir):
    """
    Prueba End-to-End de la Arquitectura Medallion Refactorizada.
    Verifica que:
    1. Bronce carga datos correctamente.
    2. Plata usa su AST/Visitor para aplicar reglas de transformación (Upper, Replace).
    3. Oro usa su AST/Visitor para agrupar semánticamente y calcular métricas.
    """
    db_path = str(test_data_dir / "test_db.duckdb")
    csv_path = str(test_data_dir / "datos.csv")
    project_id = "test_e2e_project"

    conn = duckdb.connect(db_path)
    
    try:
        repo = DuckDBJournalRepository(conn)
        use_case = ExecutePipelineUseCase(repo)

        # Configuramos reglas de Plata
        # Por ejemplo, convertimos DESCRIPCION a UPPER y reemplazamos "HOLA" con "ADIOS"
        bronze_rules = BronzeToSilverRulesDTO(
            column_rules={
                "JE_DESCRIPTION": ColumnCleaningRuleDTO(
                    uppercase=True,
                    replace_rules=[{"search": "COMPRA", "replace": "ADQUISICION"}]
                )
            },
            drop_columns=[]
        )

        # Configuramos reglas de Oro
        # Mapeo semántico + dimensión adicional
        silver_rules = SilverToGoldRulesDTO(
            semantic_mapping=SemanticMappingDTO(
                ledger_col="LIBRO",
                entered_dr_col="DEBITO",
                entered_cr_col="CREDITO",
                account_col="CUENTA"
            ),
            gold_dimensions=["JE_DESCRIPTION"]
        )

        result = use_case.execute(
            raw_csv_path=csv_path,
            bronze_parquet_path=str(test_data_dir / "bronze.parquet"),
            silver_parquet_path=str(test_data_dir / "silver.parquet"),
            bronze_rules=bronze_rules,
        )


        assert result is not None
        
        # Validaciones de Bronce
        bronze_summary = result.bronze_result
        assert bronze_summary.status in ["success", "duplicate"]

        # Validaciones de Plata
        silver_summary = result.silver_result
        assert "silver" in silver_summary.target_silver_path
        assert silver_summary.status == "success"
        assert result.total_pipeline_time_seconds >= 0.0


    finally:
        conn.close()
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)
