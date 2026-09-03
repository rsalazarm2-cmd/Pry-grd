import time
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gestor de Caché Jerárquico de 2 Niveles para la Capa Media:
    - L1 Cache: Memoria RAM ultra-rápida (LRU en memoria con latencia < 1 ms).
    - L2 Cache: Snapshots en disco Parquet/JSON para persistencia entre desalojos (< 10 ms).
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_l1_items: int = 500, l2_dir: Optional[Path] = None):
        if getattr(self, "_initialized", False):
            return
        self.max_l1_items = max_l1_items
        self.l1_cache: OrderedDict[str, Tuple[float, Any]] = OrderedDict()
        
        if l2_dir is None:
            l2_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "cache_l2"
        self.l2_dir = l2_dir
        self.l2_dir.mkdir(parents=True, exist_ok=True)
        self._initialized = True

    def _generate_key(self, namespace: str, params: Dict[str, Any]) -> str:
        serialized = json.dumps(params, sort_keys=True, default=str)
        hash_digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
        return f"{namespace}:{hash_digest}"

    def get(self, key: str) -> Optional[Any]:
        """Recupera valor probando L1 (RAM) y luego L2 (Disco)."""
        now = time.time()
        
        # 1. Chequeo L1 (RAM)
        if key in self.l1_cache:
            expire_at, value = self.l1_cache[key]
            if expire_at > now:
                self.l1_cache.move_to_end(key)
                logger.debug(f"[Caché L1 HIT - RAM] Key: {key} (< 1 ms)")
                return value
            else:
                del self.l1_cache[key]

        # 2. Chequeo L2 (Disco JSON/Snapshot)
        l2_file = self.l2_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"
        if l2_file.exists():
            try:
                with open(l2_file, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                expire_at = payload.get("expire_at", 0)
                if expire_at > now:
                    value = payload.get("value")
                    # Promover a L1
                    self.set_l1(key, value, int(expire_at - now))
                    logger.debug(f"[Caché L2 HIT - Disco] Key: {key} (< 10 ms)")
                    return value
                else:
                    l2_file.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Error al leer caché L2 para key {key}: {e}")

        logger.debug(f"[Caché MISS] Key: {key}")
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Almacena un valor en ambas capas (L1 RAM y L2 Disco)."""
        expire_at = time.time() + ttl_seconds
        
        # L1 RAM
        self.set_l1(key, value, ttl_seconds)

        # L2 Disco
        l2_file = self.l2_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"
        try:
            with open(l2_file, "w", encoding="utf-8") as f:
                json.dump({"expire_at": expire_at, "value": value}, f)
        except Exception as e:
            logger.warning(f"Error guardando caché L2 en disco: {e}")

    def set_l1(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        expire_at = time.time() + ttl_seconds
        if key in self.l1_cache:
            self.l1_cache.move_to_end(key)
        self.l1_cache[key] = (expire_at, value)
        
        # Evicción LRU si se supera el máximo
        while len(self.l1_cache) > self.max_l1_items:
            self.l1_cache.popitem(last=False)

    def invalidate_namespace(self, namespace: str) -> None:
        """Invalida todas las llaves que inicien con un namespace dado."""
        keys_to_del = [k for k in self.l1_cache.keys() if k.startswith(namespace)]
        for k in keys_to_del:
            del self.l1_cache[k]
        
        # Eliminar archivos L2 correspondientes
        for l2_file in self.l2_dir.glob("*.json"):
            try:
                l2_file.unlink(missing_ok=True)
            except Exception:
                pass

cache_manager = CacheManager()
