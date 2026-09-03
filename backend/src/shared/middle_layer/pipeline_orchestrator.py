import uuid
import logging
from typing import Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
from src.shared.middle_layer.sse_broadcaster import sse_broadcaster
from src.shared.middle_layer.cache_manager import cache_manager

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """
    Orquestador Asíncrono de Pipelines para la Capa Media:
    Ejecuta transformaciones pesadas E2E en segundo plano con ThreadPoolExecutor,
    notificando avances vía SSE y gestionando el estado global de trabajos.
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="PipelineWorker")
            cls._instance.jobs: Dict[str, Dict[str, Any]] = {}
        return cls._instance

    def submit_job(self, task_fn: Callable[..., Any], *args, **kwargs) -> str:
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        self.jobs[job_id] = {
            "job_id": job_id,
            "status": "PENDING",
            "progress": 0,
            "detail": "Trabajo encolado",
            "result": None,
            "error": None
        }

        self.executor.submit(self._run_job, job_id, task_fn, *args, **kwargs)
        logger.info(f"[Orchestrator] Trabajo {job_id} enviado a ThreadPoolExecutor.")
        return job_id

    def _run_job(self, job_id: str, task_fn: Callable[..., Any], *args, **kwargs) -> None:
        try:
            self._update_progress(job_id, "PROCESSING", 10, "Iniciando pipeline de datos...")
            
            # Hook de callback para actualizar progreso durante la ejecución
            def progress_callback(percentage: int, message: str):
                self._update_progress(job_id, "PROCESSING", percentage, message)

            result = task_fn(progress_callback=progress_callback, *args, **kwargs)
            
            # Invalida la caché ya que la data de Bronze/Silver/Gold cambió
            cache_manager.invalidate_namespace("medallion")

            self.jobs[job_id]["result"] = result
            self._update_progress(job_id, "COMPLETED", 100, "Pipeline completado con éxito.", data=result if isinstance(result, dict) else None)
            logger.info(f"[Orchestrator] Trabajo {job_id} completado con éxito.")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[Orchestrator] Error en trabajo {job_id}: {error_msg}", exc_info=True)
            self.jobs[job_id]["error"] = error_msg
            self._update_progress(job_id, "FAILED", 100, f"Error: {error_msg}")

    def _update_progress(self, job_id: str, status: str, progress: int, detail: str, data: dict = None) -> None:
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            self.jobs[job_id]["progress"] = progress
            self.jobs[job_id]["detail"] = detail
        
        sse_broadcaster.publish_event(job_id, status, progress, detail, data)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

pipeline_orchestrator = PipelineOrchestrator()
