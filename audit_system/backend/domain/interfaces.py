from abc import ABC, abstractmethod
from typing import List, Optional
from audit_system.backend.domain.entities import (
    AlertaDescuadreDTO,
    SegregacionFuncionesDTO,
    InformeIntegridadAuditoriaDTO,
)

class IAuditRepository(ABC):
    """
    Interfaz abstracta pura (Contrato ABC) del Repositorio de Auditoría Forense.
    Define las operaciones atómicas para validar afirmaciones de auditoría.
    """

    @abstractmethod
    def consultar_descuadres_partida_doble(
        self, parquet_path: str, limite: int = 100
    ) -> List[AlertaDescuadreDTO]:
        """Consulta asientos donde la suma de cargos no coincide con abonos o con el total de cabecera."""
        pass

    @abstractmethod
    def consultar_violaciones_segregacion_funciones(
        self, parquet_path: str, limite: int = 100
    ) -> List[SegregacionFuncionesDTO]:
        """Consulta asientos donde el usuario registrador coincide con el usuario aprobador (Maker/Checker)."""
        pass

    @abstractmethod
    def generar_informe_integridad_completo(
        self, parquet_path: str
    ) -> InformeIntegridadAuditoriaDTO:
        """Genera un resumen consolidado de auditoría forense sobre la Capa Plata."""
        pass
