"""Servicio de Caché Persistente para el Perfil Estadístico de la Capa Bronce.

Garantiza respuestas en ~1 ms leyendo un archivo manifest `.profile_cache.json`
indexado por la firma SHA-256 del archivo Parquet.
"""
import json
import logging
from pathlib import Path
from src.shared.domain.journal_entry import DatasetProfileDTO, ColumnProfileDTO, TopFrequencyItem
from src.bronze.domain.chain_of_custody import compute_file_sha256

logger = logging.getLogger(__name__)


class ProfileCacheService:
    """Gestiona la lectura y escritura inmutable del perfil estadístico cacheado."""

    @staticmethod
    def get_cache_path(parquet_path: Path) -> Path:
        return parquet_path.parent / ".profile_cache.json"

    @classmethod
    def load_cached_profile(cls, parquet_path: Path) -> DatasetProfileDTO | None:
        """Carga el perfil estadístico desde el caché JSON si la firma SHA-256 coincide."""
        cache_file = cls.get_cache_path(parquet_path)
        if not (cache_file.exists() and parquet_path.exists()):
            return None

        try:
            current_hash = compute_file_sha256(parquet_path)
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("file_hash") != current_hash:
                logger.info("⚡ El hash SHA-256 del Parquet cambió. Recalculando perfil...")
                return None

            profile_data = data.get("profile")
            if not profile_data:
                return None

            return DatasetProfileDTO(**profile_data)
        except Exception as e:
            logger.warning(f"No se pudo cargar el perfil cacheado: {e}")
            return None

    @classmethod
    def save_profile_cache(cls, parquet_path: Path, profile: DatasetProfileDTO) -> None:
        """Guarda el perfil estadístico en JSON inmutable junto con la firma SHA-256."""
        cache_file = cls.get_cache_path(parquet_path)
        try:
            file_hash = compute_file_sha256(parquet_path)
            payload = {
                "file_hash": file_hash,
                "profile": profile.model_dump()
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Perfil de auditoría cacheado exitosamente en: {cache_file}")
        except Exception as e:
            logger.error(f"Error guardando caché de perfil: {e}")
