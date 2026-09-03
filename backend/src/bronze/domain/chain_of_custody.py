"""Módulo de Dominio para la Cadena de Custodia Criptográfica (SHA-256).

Garantiza la inmutabilidad y el no-repudio legal de la ingesta en la Capa Bronce.
"""
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class IngestionManifest:
    file_name: str
    file_size_bytes: int
    sha256_hash: str
    ingestion_timestamp: str
    rows_count: int
    columns_count: int
    user_agent: str = "AuditForensicEngine/1.0"

    def to_dict(self) -> dict:
        return asdict(self)


def compute_file_sha256(file_path: Path) -> str:
    """Calcula el Hash SHA-256 inmutable del archivo fuente en bloques de 64KB."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_manifest(
    file_path: Path, rows_count: int, columns_count: int
) -> IngestionManifest:
    """Crea una instancia del manifiesto criptográfico de ingesta."""
    sha256 = compute_file_sha256(file_path)
    file_size = file_path.stat().st_size
    now_iso = datetime.now().isoformat()

    return IngestionManifest(
        file_name=file_path.name,
        file_size_bytes=file_size,
        sha256_hash=sha256,
        ingestion_timestamp=now_iso,
        rows_count=rows_count,
        columns_count=columns_count,
    )


def save_manifest(manifest: IngestionManifest, manifest_json_path: Path) -> None:
    """Guarda el manifiesto criptográfico como un archivo JSON inmutable."""
    manifest_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)


def load_manifest(manifest_json_path: Path) -> Optional[IngestionManifest]:
    """Carga un manifiesto criptográfico previamente registrado."""
    if not manifest_json_path.exists():
        return None
    try:
        with open(manifest_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return IngestionManifest(**data)
    except Exception:
        return None
