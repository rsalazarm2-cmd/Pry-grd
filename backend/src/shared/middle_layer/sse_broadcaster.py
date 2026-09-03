import json
import queue
import logging
from typing import Dict, Generator, List

logger = logging.getLogger(__name__)

class SSEBroadcaster:
    """
    Gestor de Eventos Server-Sent Events (SSE) para la Capa Media:
    Emite actualizaciones de progreso en vivo desde Worker Threads hacia el cliente React.
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.subscribers: Dict[str, List[queue.Queue]] = {}
        return cls._instance

    def subscribe(self, job_id: str) -> queue.Queue:
        q = queue.Queue(maxsize=50)
        if job_id not in self.subscribers:
            self.subscribers[job_id] = []
        self.subscribers[job_id].append(q)
        logger.info(f"[SSE] Nuevo cliente suscrito a job_id: {job_id}")
        return q

    def unsubscribe(self, job_id: str, q: queue.Queue) -> None:
        if job_id in self.subscribers:
            if q in self.subscribers[job_id]:
                self.subscribers[job_id].remove(q)
            if not self.subscribers[job_id]:
                del self.subscribers[job_id]
        logger.info(f"[SSE] Cliente desuscrito de job_id: {job_id}")

    def publish_event(self, job_id: str, status: str, progress: int, detail: str = "", data: dict = None) -> None:
        payload = {
            "job_id": job_id,
            "status": status,
            "progress": progress,
            "detail": detail,
            "data": data or {}
        }
        if job_id in self.subscribers:
            for q in list(self.subscribers[job_id]):
                try:
                    q.put_nowait(payload)
                except queue.Full:
                    pass

    def stream_events(self, job_id: str) -> Generator[str, None, None]:
        q = self.subscribe(job_id)
        try:
            # Evento inicial de conexión
            yield f"data: {json.dumps({'type': 'CONNECTED', 'job_id': job_id})}\n\n"
            while True:
                try:
                    item = q.get(timeout=30)
                    yield f"data: {json.dumps(item)}\n\n"
                    if item.get("status") in ["COMPLETED", "FAILED"]:
                        break
                except queue.Empty:
                    # Keep-alive heartbeat cada 30s
                    yield ": keep-alive\n\n"
        finally:
            self.unsubscribe(job_id, q)

sse_broadcaster = SSEBroadcaster()
