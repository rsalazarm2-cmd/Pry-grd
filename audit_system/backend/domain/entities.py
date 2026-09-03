from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

class AsientoContableSilverDTO(BaseModel):
    """
    DTO estricto que representa un asiento contable de Oracle EBS en la Capa Plata.
    Incorpora los nombres de dominio de auditoría financiera en español.
    """
    FOLIO_ASIENTO: str = Field(..., description="Identificador único del asiento contable")
    LINEA_ASIENTO: int = Field(..., description="Número secuencial de la línea dentro del folio")
    LIBRO_CONTABLE: str = Field(..., description="Nombre del libro o Ledger en Oracle EBS")
    PERIODO_CONTABLE: str = Field(..., description="Periodo contable (ej. ENE-2025)")
    FECHA_CONTABILIZACION: str = Field(..., description="Fecha efectiva de contabilización")
    FECHA_REGISTRO_CONTABLE: str = Field(..., description="Fecha de creación en el sistema")
    USUARIO_REGISTRADOR: str = Field(..., description="Usuario Maker que creó el asiento")
    USUARIO_APROBADOR: str = Field(..., description="Usuario Checker que aprobó el asiento")
    CUENTA_CONTABLE: str = Field(..., description="Segmento de cuenta contable")
    DESCRIPCION_CUENTA: Optional[str] = Field(None, description="Descripción de la cuenta")
    CARGO_MONEDA_FUNCIONAL: Decimal = Field(default=Decimal("0.00"), description="Monto en el Debe")
    ABONO_MONEDA_FUNCIONAL: Decimal = Field(default=Decimal("0.00"), description="Monto en el Haber")
    TOTAL_CARGOS_CABECERA: Decimal = Field(default=Decimal("0.00"), description="Total declarado en cabecera")
    CONCEPTO_ASIENTO: Optional[str] = Field(None, description="Glosa o explicación del asiento")
    ORIGEN_ASIENTO: str = Field(default="MANUAL", description="Modulo de origen (Manual, AP, AR, GL)")

class AlertaDescuadreDTO(BaseModel):
    """DTO para asientos que violan el principio de partida doble o descuadre de cabecera."""
    FOLIO_ASIENTO: str
    LIBRO_CONTABLE: str
    PERIODO_CONTABLE: str
    TOTAL_CARGOS_CALCULADO: Decimal
    TOTAL_ABONOS_CALCULADO: Decimal
    TOTAL_CARGOS_CABECERA: Decimal
    DIFERENCIA_DESCUADRE: Decimal
    TIPO_ALERTA: str = Field(default="DESCUADRE_PARTIDA_DOBLE")

class SegregacionFuncionesDTO(BaseModel):
    """DTO para violaciones de SoD (Maker == Checker)."""
    FOLIO_ASIENTO: str
    USUARIO_REGISTRADOR: str
    USUARIO_APROBADOR: str
    FECHA_REGISTRO: str
    MONTO_TOTAL_ASIENTO: Decimal
    NIVEL_RIESGO: str = Field(default="ALTO_RIESGO_SOD")

class InformeIntegridadAuditoriaDTO(BaseModel):
    """Resumen consolidado de la auditoría forense."""
    total_asientos_analizados: int
    total_descuadres_detectados: int
    total_violaciones_sod: int
    monto_total_descuadrado: Decimal
    alertas_descuadre: List[AlertaDescuadreDTO]
    alertas_sod: List[SegregacionFuncionesDTO]
