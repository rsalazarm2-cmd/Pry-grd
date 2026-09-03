import logging
from typing import Callable, Dict, List, Type
from src.shared.domain.events.domain_events import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], None]

class InMemoryEventBus:
    """Bus de eventos en memoria para auditoría y desacoplamiento de efectos secundarios."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InMemoryEventBus, cls).__new__(cls)
            cls._instance._subscribers: Dict[Type[DomainEvent], List[EventHandler]] = {}
        return cls._instance

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        logger.info(f"📢 Publicando evento de dominio: {event_type.__name__}")
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error procesando handler para {event_type.__name__}: {e}", exc_info=True)
