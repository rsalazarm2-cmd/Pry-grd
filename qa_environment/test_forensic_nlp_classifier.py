"""Pruebas Unitarias para el Clasificador Semántico NLP Forense (Fase NLP Pro)."""

import pytest
from src.ai_translator.infrastructure.forensic_nlp_classifier import ForensicNLPClassifier


def test_classify_sod_and_temporal_columns():
    """Verifica que columnas SOD y fechas obtengan alto score de relevancia (>=0.70)."""
    classifier = ForensicNLPClassifier()

    sod_col = classifier.classify_column("USUARIO_REGISTRADOR")
    assert sod_col.is_high_relevance is True
    assert sod_col.vector_category == "SOD"
    assert sod_col.relevance_score >= 0.90

    date_col = classifier.classify_column("FECHA_CONTABILIZACION")
    assert date_col.is_high_relevance is True
    assert date_col.vector_category == "TEMPORAL"


def test_classify_technical_exclusion_columns():
    """Verifica que campos técnicos de ERP reciban score bajo y sean candidatos a Lista de Espera."""
    classifier = ForensicNLPClassifier()

    org_col = classifier.classify_column("ORG_ID")
    assert org_col.is_high_relevance is False
    assert org_col.vector_category == "TECHNICAL"

    attr_col = classifier.classify_column("ATTRIBUTE1")
    assert attr_col.is_high_relevance is False
    assert attr_col.relevance_score < 0.50


def test_detect_header_pk_strategy_natural_vs_surrogate():
    """Verifica la detección de Llave Natural ERP vs. Llave Sustituta Determinista (DENSE_RANK)."""
    classifier = ForensicNLPClassifier()

    # Caso 1: Dataset con Llave Natural ERP
    strat, key, desc = classifier.detect_header_pk_strategy(["FOLIO_ASIENTO", "CARGO", "USUARIO_REGISTRADOR"])
    assert strat == "NATURAL_KEY"
    assert key == "FOLIO_ASIENTO"
    assert "Llave Natural ERP" in desc

    # Caso 2: Dataset plano sin llave de cabecera nativa
    strat_s, key_s, desc_s = classifier.detect_header_pk_strategy(["CARGO", "ABONO", "USUARIO_REGISTRADOR", "GLOSA"])
    assert strat_s == "DENSE_RANK_SURROGATE"
    assert "DENSE_RANK()" in key_s
    assert "Estándar Kimball" in desc_s
