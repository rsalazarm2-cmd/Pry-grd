import logging
from typing import Dict, Any

from ninja import Router, Query
from ninja.errors import HttpError

from src.ai_translator.infrastructure.marian_mt_translator import MarianMTTranslator
from src.ai_translator.application.translate_columns_use_case import TranslateColumnsUseCase

logger = logging.getLogger(__name__)

router = Router()

_translator_instance = None
def get_translator():
    global _translator_instance
    if _translator_instance is None:
        logger.info("Cargando modelo MarianMT de HuggingFace en memoria...")
        _translator_instance = MarianMTTranslator()
    return _translator_instance

@router.get("/suggest-mapping", tags=["AI Integration"])
def suggest_mapping(
    request,
    source_columns: str = Query(..., description="Columnas CSV separadas por coma"),
    target_lang: str = Query("es", description="Idioma objetivo: es o en")
):
    """
    Usa el traductor NLP local para sugerir el mapeo de las columnas enviadas en Español o Inglés.
    """
    cols = [c.strip() for c in source_columns.split(",") if c.strip()]
    if not cols:
        return {}
    
    try:
        translator = get_translator()
        use_case = TranslateColumnsUseCase(translator)
        result = use_case.execute(cols, target_lang=target_lang)
        return result.dict()
    except Exception as e:
        logger.error(f"Error sugiriendo mapeo: {e}", exc_info=True)
        return {"error": str(e)}
