import logging
from pathlib import Path
import duckdb

from src.shared.domain.journal_entry import (
    BronzeIngestionResultDTO,
    DatasetProfileDTO,
    TabularResultDTO,
)
from src.shared.infrastructure.query_builder import QueryBuilder
from src.bronze.infrastructure.bronze_ingestion_service import BronzeIngestionService
from src.bronze.infrastructure.profile_cache_service import ProfileCacheService
from src.bronze.infrastructure.bronze_profiler import (
    safe_path,
    profile_column,
    get_nlp_classifier,
)

logger = logging.getLogger(__name__)

class BronzeDuckDBService:
    """
    Fachada / Facade para la Capa Bronce. 
    Aplica SRP delegando a servicios especializados (Ingesta, Profiling, Caché, Consultas).
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn
        self.ingestion_service = BronzeIngestionService(conn)

    def save_bronze(self, source_csv_path: str, target_parquet_path: str) -> BronzeIngestionResultDTO:
        return self.ingestion_service.save_bronze(source_csv_path, target_parquet_path)

    def get_bronze_profile(self, bronze_parquet_path: str) -> DatasetProfileDTO:
        target_path = Path(bronze_parquet_path).resolve()
        if not target_path.exists():
            return DatasetProfileDTO(
                file_path=str(target_path),
                total_rows=0,
                total_columns=0,
                file_size_bytes=0,
                columns=[],
                domain_summary={},
            )

        cached_profile = ProfileCacheService.load_cached_profile(target_path)
        if cached_profile:
            return cached_profile

        safe_target = safe_path(target_path)
        file_size = target_path.stat().st_size
        total_rows = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_target}')").fetchone()[0]
        schema_info = self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_target}')").fetchall()

        classifier = get_nlp_classifier()
        column_profiles = [
            profile_column(self.conn, target_path, col_tuple[0], col_tuple[1], total_rows)
            for col_tuple in schema_info
        ]

        domain_counts: dict[str, int] = {}
        for col_profile in column_profiles:
            domain_cat = col_profile.domain_category
            domain_counts[domain_cat] = domain_counts.get(domain_cat, 0) + 1

        profile = DatasetProfileDTO(
            file_path=str(target_path),
            total_rows=total_rows,
            total_columns=len(schema_info),
            file_size_bytes=file_size,
            columns=column_profiles,
            domain_summary=domain_counts,
        )

        ProfileCacheService.save_profile_cache(target_path, profile)
        return profile

    def query_bronze_records(
        self,
        bronze_parquet_path: str,
        limit: int = 50,
        search_term: str = None,
        column_name: str = None,
        filters_json: str = None,
    ) -> TabularResultDTO:
        target_path = Path(bronze_parquet_path).resolve()
        if not target_path.exists():
            return TabularResultDTO(total_count=0, returned_count=0, columns=[], rows=[])

        safe_target = safe_path(target_path)
        total_count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_target}')").fetchone()[0]
        schema_info = self.conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{safe_target}')").fetchall()
        columns = [c[0] for c in schema_info]

        where_sql, params = QueryBuilder.build_where(columns, search_term, column_name, filters_json)

        query = f"SELECT * FROM read_parquet('{safe_target}') {where_sql} LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(query, params)
        col_names = [desc[0] for desc in cursor.description]
        raw_rows = cursor.fetchall()
        rows = [dict(zip(col_names, r)) for r in raw_rows]

        return TabularResultDTO(
            total_count=total_count,
            returned_count=len(rows),
            columns=col_names,
            rows=rows,
        )
