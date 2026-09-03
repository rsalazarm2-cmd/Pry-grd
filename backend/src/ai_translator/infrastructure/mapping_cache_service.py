"""Servicio de Caché Persistente para Sugerencias Semánticas de Mapeo (IA).

Garantiza respuestas en ~1 ms leyendo `.mapping_cache.json`
indexado por la firma SHA-256 del Parquet Bronce.
"""
import json
import logging
from pathlib import Path
from src.shared.domain.journal_entry import BronzeToSilverRulesDTO
from src.bronze.domain.chain_of_custody import compute_file_sha256

logger = logging.getLogger(__name__)


class MappingCacheService:
    """Gestiona el almacenamiento en caché del mapeo semántico sugerido por la IA."""

    @staticmethod
    def get_cache_path(parquet_path: Path, lang: str = "es") -> Path:
        return parquet_path.parent / f".mapping_cache_{lang.lower()}.json"

    @classmethod
    def load_cached_rules(cls, parquet_path: Path, lang: str = "es") -> BronzeToSilverRulesDTO | None:
        """Carga las reglas sugeridas desde el JSON si la firma SHA-256 coincide."""
        cache_file = cls.get_cache_path(parquet_path, lang)
        if not (cache_file.exists() and parquet_path.exists()):
            return None

        try:
            current_hash = compute_file_sha256(parquet_path)
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("file_hash") != current_hash:
                logger.info(f"⚡ SHA-256 del Parquet cambió. Recalculando mapeo IA ({lang})...")
                return None

            rules_dict = data.get("rules")
            if not rules_dict:
                return None

            return BronzeToSilverRulesDTO(**rules_dict)
        except Exception as e:
            logger.warning(f"No se pudo cargar la caché de mapeo IA: {e}")
            return None

    @classmethod
    def save_rules_cache(cls, parquet_path: Path, rules: BronzeToSilverRulesDTO, lang: str = "es") -> None:
        """Guarda las reglas sugeridas en JSON inmutable junto con la firma SHA-256."""
        cache_file = cls.get_cache_path(parquet_path, lang)
        try:
            file_hash = compute_file_sha256(parquet_path)
            payload = {
                "file_hash": file_hash,
                "rules": rules.model_dump()
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Mapeo IA cacheado exitosamente en: {cache_file}")
        except Exception as e:
            logger.error(f"Error guardando caché de mapeo IA: {e}")
