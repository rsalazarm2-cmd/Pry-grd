import logging
from pathlib import Path
from uuid import uuid4
import duckdb

logger = logging.getLogger(__name__)

def execute_atomic_parquet_copy(conn: duckdb.DuckDBPyConnection, select_sql: str, target_path: Path) -> None:
    """
    Ejecuta una escritura atómica de Parquet utilizando el patrón (temp_file -> replace).
    Si ocurre cualquier falla durante la generación SQL o escritura en disco, 
    el archivo temporal se elimina y el target_path original permanece 100% intacto y sin corrupción.
    """
    target_path = Path(target_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Crear un archivo temporal único en la misma carpeta para garantizar rename atómico a nivel de POSIX/OS
    temp_filename = f".atomic_{uuid4().hex}.tmp.parquet"
    temp_path = target_path.parent / temp_filename

    safe_temp_str = str(temp_path).replace("'", "''")

    copy_sql = f"""
        COPY (
            {select_sql}
        ) TO '{safe_temp_str}' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
    """

    try:
        conn.execute(copy_sql)
        # Reemplazo atómico a nivel de sistema operativo
        temp_path.replace(target_path)
        logger.info(f"✅ Escritura atómica exitosa en Parquet: {target_path.name}")
    except Exception as e:
        logger.error(f"❌ Error durante escritura atómica Parquet: {e}", exc_info=True)
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise e
