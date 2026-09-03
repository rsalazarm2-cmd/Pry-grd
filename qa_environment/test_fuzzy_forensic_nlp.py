"""Pruebas Unitarias para el Motor NLP de Matching Difuso (Fuzzy NLP Engine)."""

import pytest
from src.ai_translator.infrastructure.fuzzy_forensic_nlp import FuzzyForensicNLPClassifier


def test_fuzzy_matching_custom_erp_column_names():
    """Verifica que columnas con nombres abreviados de cualquier ERP se clasifiquen correctamente."""
    classifier = FuzzyForensicNLPClassifier()

    # Usuario registrador en ERP personalizado
    usr_res = classifier.classify_column("USR_CREAT_ID")
    assert usr_res.is_high_relevance is True
    assert usr_res.vector_category == "SOD"
    assert usr_res.similarity_confidence >= 0.65

    # Fecha contable abreviada
    date_res = classifier.classify_column("POST_DT_TIME")
    assert date_res.is_high_relevance is True
    assert date_res.vector_category == "TEMPORAL"

    # Monto de cargo abreviado
    amt_res = classifier.classify_column("TRX_AMT_DR")
    assert amt_res.is_high_relevance is True
    assert amt_res.vector_category == "FINANCIAL"


def test_fuzzy_matching_technical_exclusion():
    """Verifica que atributos de sistema ERP reciban clasificación técnica."""
    classifier = FuzzyForensicNLPClassifier()

    tech_res = classifier.classify_column("LAST_UPDATE_LOGIN")
    assert tech_res.is_high_relevance is False
    assert tech_res.vector_category == "TECHNICAL"
