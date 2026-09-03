import re
from typing import List, Optional
from src.silver.domain.atomicity import AtomicitySuggestionDTO, SegmentDefinitionDTO


ERP_KNOWN_PATTERNS = {
    "CODE_COMBINATION": [
        "COMPANIA",
        "SUCURSAL",
        "CENTRO_COSTO",
        "CUENTA_NATIVA",
        "SUBCUENTA",
        "INTERCO",
        "AUXILIAR",
    ],
    "JOURNAL_ENTRY_LINE_DESCRIPTION": [
        "MODULO_ERP",
        "ID_COMPROBANTE",
        "USUARIO_ANALISTA",
        "DESCRIPCION_DETALLADA",
    ],
    "JE_DESCRIPTION": [
        "TIPO_ASIENTO",
        "NRO_COMPROBANTE",
        "DETALLE_TRANSACCION",
    ],
    "JE_BATCH_NAME": [
        "MODULO_LOTE",
        "NRO_PLANILLA",
        "USUARIO_CREADOR",
        "NARRATIVA_LOTE",
    ],
}


class AtomicityAnalyzer:
    """Servicio de Dominio puro para detectar atomización de columnas y sanitizar encabezados SQL."""

    @staticmethod
    def sanitize_header_name(column_name: str) -> str:
        """Limpia nombres de columna ruidosos provenientes de exportaciones SQL de ERP."""
        col = column_name.strip()
        if "TO_CHAR" in col.upper():
            return "FECHA_HORA_ULTIMA_ACTUALIZACION"
        
        # Eliminar comillas y paréntesis sobrantes
        col = re.sub(r"['\"\(\)]", "", col)
        col = re.sub(r"__+", "_", col)
        return col.upper().strip()

    @classmethod
    def analyze_column(cls, column_name: str, raw_samples: List[str]) -> Optional[AtomicitySuggestionDTO]:
        clean_samples = [s for s in raw_samples if s and str(s).strip() and str(s) != "NULL"]
        if not clean_samples:
            return None

        col_upper = column_name.upper()
        clean_header = cls.sanitize_header_name(column_name)

        # 1. Comprobar patrones de ERP conocidos primero
        for pattern_key, suggested_names in ERP_KNOWN_PATTERNS.items():
            if pattern_key in col_upper or col_upper.startswith(pattern_key) or ("DESCRIP" in col_upper and "DESCRIPTION" in pattern_key):
                # Determinar delimitador principal (punto '.' para CODE_COMBINATION, ' - ' o '-' para descripciones)
                delimiter = "." if "COMBINATION" in col_upper else "-"
                first_sample = clean_samples[0]
                
                parts = [p.strip() for p in first_sample.split(delimiter) if p.strip()]
                if len(parts) >= 2:
                    segments: List[SegmentDefinitionDTO] = []
                    for idx, part in enumerate(parts, start=1):
                        alias = suggested_names[idx - 1] if idx <= len(suggested_names) else f"SEGMENTO_{idx}"
                        segments.append(SegmentDefinitionDTO(index=idx, suggested_alias=alias, sample_value=part))

                    return AtomicitySuggestionDTO(
                        column_name=column_name,
                        suggested_clean_header=clean_header if clean_header != col_upper else None,
                        delimiter=delimiter,
                        confidence_score=0.95,
                        detected_segments_count=len(segments),
                        suggested_segments=segments,
                        sample_raw_values=clean_samples[:3],
                    )

        # 2. Análisis heurístico para columnas compuestas genéricas
        candidate_delimiters = [".", "-", "/", " "]
        best_delimiter = None
        best_count = 0
        best_confidence = 0.0

        for delim in candidate_delimiters:
            counts = [len(s.split(delim)) for s in clean_samples if len(s.split(delim)) > 1]
            if len(counts) >= len(clean_samples) * 0.7:
                avg_count = sum(counts) // len(counts)
                if avg_count >= 2:
                    best_delimiter = delim
                    best_count = avg_count
                    best_confidence = round(len(counts) / len(clean_samples), 2)
                    break

        if best_delimiter and best_count >= 2:
            first_sample = clean_samples[0]
            parts = [p.strip() for p in first_sample.split(best_delimiter)]
            segments = [
                SegmentDefinitionDTO(index=idx, suggested_alias=f"{column_name}_SEG_{idx}", sample_value=part)
                for idx, part in enumerate(parts, start=1)
            ]

            return AtomicitySuggestionDTO(
                column_name=column_name,
                suggested_clean_header=clean_header if clean_header != col_upper else None,
                delimiter=best_delimiter,
                confidence_score=best_confidence,
                detected_segments_count=len(segments),
                suggested_segments=segments,
                sample_raw_values=clean_samples[:3],
            )

        return None
