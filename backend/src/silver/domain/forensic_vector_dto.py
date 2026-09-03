"""DTOs de Pydantic para el Motor Vectorial Forense de 5 Dimensiones.

Representa los vectores de enriquecimiento analítico generados en la Capa Plata
para auditoría forense de asientos contables.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ForensicVectorTemporalDTO(BaseModel):
    """Vector 1: Indicadores de riesgo por ventana temporal y horario."""

    flag_fin_semana: bool = Field(
        default=False,
        description="Verdadero si el asiento se contabilizó en Sábado o Domingo.",
    )
    flag_horario_nocturno: bool = Field(
        default=False,
        description="Verdadero si se registró fuera del horario laboral (19:00 - 07:00).",
    )
    flag_corte_mes: bool = Field(
        default=False,
        description="Verdadero si la fecha de contabilización es día de cierre de mes.",
    )
    dias_diferencia_creacion_gl: int = Field(
        default=0,
        description="Días de brecha entre FECHA_REGISTRO_CONTABLE y FECHA_CONTABILIZACION.",
    )


class ForensicVectorSODDTO(BaseModel):
    """Vector 2: Segregación de Funciones (SOD) y tiempo de aprobación."""

    flag_mismo_usuario: bool = Field(
        default=False,
        description="Verdadero si USUARIO_REGISTRADOR es igual a USUARIO_APROBADOR.",
    )
    delta_segundos_aprobacion: Optional[float] = Field(
        default=None,
        description="Diferencia en segundos entre la creación y la aprobación.",
    )
    flag_aprobacion_flash: bool = Field(
        default=False,
        description="Verdadero si el asiento se aprobó en menos de 60 segundos.",
    )


class ForensicVectorSemanticoDTO(BaseModel):
    """Vector 3: Análisis Semántico NLP en Glosas."""

    score_entropia_glosa: float = Field(
        default=0.0,
        description="Nivel de impredecibilidad/entropía del texto de la glosa.",
    )
    flag_glosa_sospechosa: bool = Field(
        default=False,
        description="Verdadero si contiene términos evasivos ('ajuste', '.', 'reclasif').",
    )
    longitud_glosa: int = Field(
        default=0,
        description="Cantidad total de caracteres de la glosa limpia.",
    )


class ForensicVectorMatematicoDTO(BaseModel):
    """Vector 4: Indicadores de estructura numérica y Benford."""

    flag_monto_redondo: bool = Field(
        default=False,
        description="Verdadero si el monto termina en múltiples ceros (ej. 100,000.00).",
    )
    primer_digito: int = Field(
        default=0,
        description="Primer dígito significativo de CARGO_MONEDA_FUNCIONAL.",
    )
    flag_desviacion_benford: bool = Field(
        default=False,
        description="Verdadero si el dígito inicial es anómalo según Benford.",
    )


class ForensicVectorAcumuladoDTO(BaseModel):
    """Vector 5: Comportamiento Acumulado y Fraccionamiento (Split Transactions)."""

    monto_acumulado_dia_usuario: float = Field(
        default=0.0,
        description="Suma acumulada de cargos por usuario y fecha en ventana móvil.",
    )
    conteo_asientos_dia_usuario: int = Field(
        default=0,
        description="Número de asientos creados por el mismo usuario en el día.",
    )
    flag_posible_fraccionamiento: bool = Field(
        default=False,
        description="Verdadero si la suma acumulada bordea el límite de aprobación.",
    )


class ForensicVectorRecordDTO(BaseModel):
    """DTO Consolidado de los 5 vectores forenses para un asiento contable."""

    folio_asiento: str = Field(description="Identificador único del asiento contable.")
    vector_temporal: ForensicVectorTemporalDTO
    vector_sod: ForensicVectorSODDTO
    vector_semantico: ForensicVectorSemanticoDTO
    vector_matematico: ForensicVectorMatematicoDTO
    vector_acumulado: ForensicVectorAcumuladoDTO
    score_riesgo_preliminar: float = Field(
        default=0.0,
        description="Puntaje de riesgo preliminar (0.0 a 100.0).",
    )


class ForensicAuditSummaryDTO(BaseModel):
    """Resumen analítico ejecutivo de la evaluación del motor vectorial."""

    total_registros_evaluados: int = 0
    total_alertas_temporales: int = 0
    total_alertas_sod: int = 0
    total_alertas_semanticas: int = 0
    total_alertas_fraccionamiento: int = 0
    total_asientos_alto_riesgo: int = 0
