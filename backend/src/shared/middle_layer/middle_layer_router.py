import logging
from typing import Optional, Any, Dict
from pathlib import Path

from django.conf import settings
from django.http import StreamingHttpResponse
from ninja import Router, Query
from pydantic import BaseModel

from src.shared.middle_layer.cache_manager import cache_manager
from src.shared.middle_layer.pipeline_orchestrator import pipeline_orchestrator
from src.shared.middle_layer.sse_broadcaster import sse_broadcaster
from src.shared.application.execute_pipeline_use_case import ExecutePipelineUseCase
from src.shared.domain.journal_entry import BronzeToSilverRulesDTO, SilverToGoldRulesDTO
from src.shared.api.dependencies import resolve_project_paths, get_repository

logger = logging.getLogger(__name__)

router = Router(tags=["Capa Media Aislada"])

class AsyncPipelineRequest(BaseModel):
    bronze_rules: Optional[BronzeToSilverRulesDTO] = None
    silver_rules: Optional[SilverToGoldRulesDTO] = None
    project_id: Optional[str] = None

class JobResponseDTO(BaseModel):
    job_id: str
    status: str
    progress: int
    detail: str
    sse_url: str

@router.get("/records", response=Dict[str, Any])
def get_cached_records(
    request,
    layer: str = Query("bronze", description="Capa Medallion: bronze, silver, gold"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    project_id: Optional[str] = Query(None)
):
    """
    Obtiene registros paginados consultando primero la Caché L1/L2 de Capa Media (< 1 ms).
    """
    cache_key = cache_manager._generate_key(
        namespace="medallion:records",
        params={"layer": layer, "page": page, "page_size": page_size, "project_id": project_id}
    )

    # Chequeo en Caché Jerárquica L1/L2
    cached = cache_manager.get(cache_key)
    if cached:
        return {"source": "CACHE_HIT", "latency": "< 1 ms", **cached}

    # Si es MISS, consultar el repositorio DuckDB
    paths = resolve_project_paths(project_id)
    repo = get_repository()
    
    offset = (page - 1) * page_size
    records = repo.get_records_paginated(layer=layer, offset=offset, limit=page_size)
    total_count = repo.get_records_count(layer=layer)

    response_data = {
        "layer": layer,
        "page": page,
        "page_size": page_size,
        "total_records": total_count,
        "data": records
    }

    # Guardar en Caché L1/L2 con TTL de 5 minutos
    cache_manager.set(cache_key, response_data, ttl_seconds=300)

    return {"source": "ENGINE_DUCKDB", "latency": "Calculado", **response_data}


@router.post("/run-async", response={202: JobResponseDTO})
def run_pipeline_async(request, payload: AsyncPipelineRequest):
    """
    Inicia la ejecución E2E del Pipeline Medallion en segundo plano de manera no bloqueante.
    Retorna un job_id y la URL SSE para escuchar el avance en tiempo real.
    """
    paths = resolve_project_paths(payload.project_id)
    source_csv = Path(paths["project"].storage_path) / "raw" / "datos.csv"
    if not source_csv.exists():
        source_csv = settings.PROJECT_ROOT / "datos.csv"

    repo = get_repository()

    # Función interna que ejecutará el worker thread
    def task_worker(progress_callback=None):
        if progress_callback:
            progress_callback(20, "Iniciando ingesta y limpieza en Bronze...")
        use_case = ExecutePipelineUseCase(repo)
        
        # Ejecutar pipeline
        result = use_case.execute(
            str(source_csv), str(paths["bronze"]), str(paths["silver"]), str(paths["gold_dir"]),
            payload.bronze_rules, payload.silver_rules
        )
        
        if progress_callback:
            progress_callback(80, "Generando capas Silver y Gold...")
        
        return {
            "bronze_records": result.bronze_summary.raw_row_count,
            "silver_records": result.silver_summary.cleaned_row_count,
            "gold_records": result.gold_summary.aggregated_row_count,
        }

    job_id = pipeline_orchestrator.submit_job(task_worker)

    return JobResponseDTO(
        job_id=job_id,
        status="PENDING",
        progress=0,
        detail="Trabajo encolado en Capa Media",
        sse_url=f"/api/middle-layer/events/{job_id}"
    )


@router.get("/events/{job_id}")
def stream_job_events(request, job_id: str):
    """
    Canal de transmisión Server-Sent Events (SSE) en tiempo real para el estado del job.
    """
    response = StreamingHttpResponse(
        sse_broadcaster.stream_events(job_id),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@router.get("/status/{job_id}", response=Dict[str, Any])
def get_job_status(request, job_id: str):
    """
    Consulta REST del estado actual del trabajo.
    """
    status = pipeline_orchestrator.get_job_status(job_id)
    if not status:
        return {"error": "Trabajo no encontrado", "job_id": job_id}
    return status
