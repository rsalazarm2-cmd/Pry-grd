"""Servicio de Persistencia de Reglas de Mapeo (.column_mapping_rules.json).

Permite guardar, cargar y auto-generar las reglas personalizadas del auditor por proyecto.
En cargas incrementales o archivos con la misma estructura, devuelve las reglas
en ~1 ms omitiendo la llamada al modelo NLP.
"""
import json
import logging
from pathlib import Path
import duckdb
from src.shared.domain.journal_entry import BronzeToSilverRulesDTO, ColumnCleaningRuleDTO

logger = logging.getLogger(__name__)


class MappingRulesPersistenceService:
    """Gestiona la lectura, auto-generación y escritura inmutable de reglas de mapeo contables."""

    @staticmethod
    def get_rules_path(bronze_parquet_path: Path) -> Path:
        return bronze_parquet_path.parent / ".column_mapping_rules.json"

    @classmethod
    def load_saved_rules(cls, bronze_parquet_path: Path) -> BronzeToSilverRulesDTO:
        """Carga las reglas guardadas o auto-genera reglas por defecto basadas en el Parquet Bronce."""
        rules_file = cls.get_rules_path(bronze_parquet_path)
        if not rules_file.exists():
            return cls.generate_default_rules(bronze_parquet_path)

        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info(f"⚡ Reglas de mapeo encontradas en memoria local: {rules_file}")
            return BronzeToSilverRulesDTO(**data)
        except Exception as e:
            logger.warning(f"No se pudieron cargar las reglas guardadas, usando por defecto: {e}")
            return cls.generate_default_rules(bronze_parquet_path)

    @classmethod
    def generate_default_rules(cls, bronze_parquet_path: Path) -> BronzeToSilverRulesDTO:
        """Genera reglas 1-a-1 automáticamente a partir del esquema de read_parquet."""
        rules_dict = {}
        if not bronze_parquet_path.exists():
            return BronzeToSilverRulesDTO()

        try:
            conn = duckdb.connect(database=":memory:")
            safe_p = str(bronze_parquet_path.resolve()).replace("'", "''")
            schema = conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_p}')").fetchall()
            conn.close()
            for row in schema:
                col_name = row[0]
                col_type = str(row[1]).upper()
                target_t = "DOUBLE" if any(k in col_type for k in ["DOUBLE", "DECIMAL", "FLOAT", "INT", "HUGEINT"]) else "VARCHAR"
                rules_dict[col_name] = ColumnCleaningRuleDTO(
                    include_in_silver=True,
                    new_column_name=col_name,
                    target_data_type=target_t,
                    null_imputation="DEFAULT",
                    has_commas=True,
                    has_dots=True,
                    has_nulls=True,
                )

        except Exception as e:
            logger.warning(f"Error generando reglas por defecto: {e}")

        return BronzeToSilverRulesDTO(column_rules=rules_dict)

    @classmethod
    def save_rules(cls, bronze_parquet_path: Path, rules: BronzeToSilverRulesDTO) -> None:
        """Guarda las reglas personalizadas del auditor en .column_mapping_rules.json."""
        rules_file = cls.get_rules_path(bronze_parquet_path)
        try:
            payload = rules.model_dump()
            with open(rules_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Reglas de mapeo del auditor guardadas en: {rules_file}")
        except Exception as e:
            logger.error(f"Error guardando reglas de mapeo: {e}")
