import logging
import time
from pathlib import Path
import duckdb

from src.shared.domain.journal_entry import BronzeIngestionResultDTO
from src.bronze.domain.chain_of_custody import (
    compute_file_sha256, create_manifest, save_manifest
)

logger = logging.getLogger(__name__)

def _safe_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")

class BronzeIngestionService:
    """Servicio con la responsabilidad única de gestionar la ingesta de CSVs a Parquet Bronce."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def save_bronze(self, source_csv_path: str, target_parquet_path: str) -> BronzeIngestionResultDTO:
        start_time = time.time()
        source_path = Path(source_csv_path).resolve()
        target_path = Path(target_parquet_path).resolve()

        if not source_path.exists():
            raise FileNotFoundError(f"El archivo fuente CSV no existe en: {source_path}")

        target_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_parquet = target_path.parent / ".ingestion_manifest.parquet"

        file_hash = compute_file_sha256(source_path)

        duplicate_result = self._check_duplicate(manifest_parquet, target_path, file_hash, source_path, start_time)
        if duplicate_result:
            return duplicate_result

        is_incremental = False
        previous_rows = 0

        if not target_path.exists():
            self._first_ingestion(source_path, target_path)
        elif self._schemas_match(source_path, target_path):
            previous_rows = self._incremental_append(source_path, target_path)
            is_incremental = True
        else:
            self._schema_overwrite(source_path, target_path)

        safe_target = _safe_path(target_path)
        row_count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_target}')").fetchone()[0]
        new_rows_count = row_count - previous_rows
        col_count = len(self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_target}')").fetchall())
        
        self._update_manifest(manifest_parquet, file_hash, source_path.name, new_rows_count)

        # Generar y guardar manifiesto JSON inmutable de cadena de custodia
        manifest_obj = create_manifest(source_path, row_count, col_count)
        json_manifest_path = target_path.parent / "ingestion_manifest.json"
        save_manifest(manifest_obj, json_manifest_path)

        file_size = target_path.stat().st_size
        elapsed_time = round(time.time() - start_time, 4)

        msg = (
            f"✅ Ingesta incremental completada (Añadidos {new_rows_count} registros a {previous_rows} existentes)."
            if is_incremental
            else f"✅ Ingesta completada ({row_count} registros procesados con firma SHA-256)."
        )

        return BronzeIngestionResultDTO(
            status="success",
            source_csv_path=str(source_path),
            target_parquet_path=str(target_path),
            rows_ingested=row_count,
            columns_count=col_count,
            file_size_bytes=file_size,
            execution_time_seconds=elapsed_time,
            is_incremental=is_incremental,
            previous_rows=previous_rows,
            file_hash=file_hash,
            message=msg,
        )

    def _check_duplicate(
        self, manifest_path: Path, target_path: Path, file_hash: str, source_path: Path, start_time: float
    ) -> BronzeIngestionResultDTO | None:
        if not (manifest_path.exists() and target_path.exists()):
            return None

        safe_manifest = _safe_path(manifest_path)
        safe_target = _safe_path(target_path)

        dup_count = self.conn.execute(
            f"SELECT COUNT(*) FROM read_parquet('{safe_manifest}') WHERE file_hash = ?", [file_hash]
        ).fetchone()[0]

        if dup_count == 0:
            return None

        row_count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_target}')").fetchone()[0]
        col_count = len(self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_target}')").fetchall())
        file_size = target_path.stat().st_size

        return BronzeIngestionResultDTO(
            status="duplicate",
            source_csv_path=str(source_path),
            target_parquet_path=str(target_path),
            rows_ingested=row_count,
            columns_count=col_count,
            file_size_bytes=file_size,
            execution_time_seconds=round(time.time() - start_time, 4),
            file_hash=file_hash,
            message="⚠️ El archivo subido es un duplicado exacto ya registrado en el manifest de auditoría SHA-256. Operación omitida.",
        )

    def _schemas_match(self, source_path: Path, target_path: Path) -> bool:
        safe_target = _safe_path(target_path)
        safe_source = _safe_path(source_path)
        existing_cols = [r[0] for r in self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_target}')").fetchall()]
        new_cols = [r[0] for r in self.conn.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{safe_source}', all_varchar=True)").fetchall()]
        return existing_cols == new_cols

    def _first_ingestion(self, source_path: Path, target_path: Path) -> None:
        safe_source = _safe_path(source_path)
        safe_target = _safe_path(target_path)
        self.conn.execute(f"""
            COPY (
                SELECT * FROM read_csv_auto('{safe_source}', all_varchar=True)
            ) TO '{safe_target}' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
        """)

    def _incremental_append(self, source_path: Path, target_path: Path) -> int:
        safe_target = _safe_path(target_path)
        safe_source = _safe_path(source_path)
        existing_rows = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_target}')").fetchone()[0]
        temp_parquet = target_path.parent / "bronze_tmp.parquet"
        safe_temp = _safe_path(temp_parquet)

        self.conn.execute(f"""
            COPY (
                SELECT * FROM read_parquet('{safe_target}')
                UNION ALL
                SELECT * FROM read_csv_auto('{safe_source}', all_varchar=True)
            ) TO '{safe_temp}' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
        """)

        if temp_parquet.exists():
            temp_parquet.replace(target_path)

        return existing_rows

    def _schema_overwrite(self, source_path: Path, target_path: Path) -> None:
        safe_source = _safe_path(source_path)
        safe_target = _safe_path(target_path)
        self.conn.execute(f"""
            COPY (
                SELECT * FROM read_csv_auto('{safe_source}', all_varchar=True)
            ) TO '{safe_target}' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
        """)

    def _update_manifest(self, manifest_path: Path, file_hash: str, file_name: str, rows_count: int) -> None:
        safe_manifest = _safe_path(manifest_path)
        union_clause = f"UNION ALL SELECT * FROM read_parquet('{safe_manifest}')" if manifest_path.exists() else ""
        self.conn.execute(f"""
            COPY (
                SELECT
                    '{file_hash}' AS file_hash,
                    '{file_name}' AS file_name,
                    CURRENT_TIMESTAMP AS ingested_at,
                    {rows_count} AS rows_count
                {union_clause}
            ) TO '{safe_manifest}' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
        """)
