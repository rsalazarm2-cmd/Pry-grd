from typing import List
from audit_system.backend.domain.interfaces import IAuditRepository
from audit_system.backend.domain.entities import (
    AlertaDescuadreDTO,
    SegregacionFuncionesDTO,
    InformeIntegridadAuditoriaDTO,
)

class ValidarIntegridadAsientosUseCase:
    """
    Caso de Uso Principal de Auditoría Forense:
    Inyecta la interfaz del repositorio (Clean Architecture) para validar
    las afirmaciones de integridad financiera sobre los asientos contables.
    """

    def __init__(self, repository: IAuditRepository):
        self.repository = repository

    def ejecutar_validacion_descuadres(
        self, parquet_path: str, limite: int = 100
    ) -> List[AlertaDescuadreDTO]:
        return self.repository.consultar_descuadres_partida_doble(parquet_path, limite)

    def ejecutar_validacion_sod(
        self, parquet_path: str, limite: int = 100
    ) -> List[SegregacionFuncionesDTO]:
        return self.repository.consultar_violaciones_segregacion_funciones(
            parquet_path, limite
        )

    def generar_informe_auditoria(
        self, parquet_path: str
    ) -> InformeIntegridadAuditoriaDTO:
        return self.repository.generar_informe_integridad_completo(parquet_path)
