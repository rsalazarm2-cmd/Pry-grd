import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

from src.ai_translator.domain.translator_port import SemanticTranslatorPort
from src.ai_translator.domain.models import SemanticMappingSuggestionDTO, TargetSchemaDefinitionDTO
from src.ai_translator.domain.domain_classifier import (
    BUSINESS_DOMAINS, expand_erp_acronyms,
    ENGLISH_TO_SPANISH_MAP, SPANISH_TO_ENGLISH_MAP
)

class NLPSemanticTranslator(SemanticTranslatorPort):
    """
    Motor NLP Neuronal Multilingüe Bidireccional (Inglés ↔ Español).
    Combina Embeddings L2 con Matriz L1 de Mapeo ERP Estándar y Cache L1 de dominios.
    """
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.domain_names = list(BUSINESS_DOMAINS.keys())
        domain_texts = [f"{k}: {desc}" for k, desc in BUSINESS_DOMAINS.items()]
        self.domain_embeddings = self.model.encode(domain_texts, convert_to_numpy=True)
        domain_norms = np.linalg.norm(self.domain_embeddings, axis=1, keepdims=True)
        self.domain_embeddings_norm = self.domain_embeddings / np.where(domain_norms == 0, 1, domain_norms)
        self._domain_cache: Dict[str, str] = {}

    def classify_domain(self, column_name: str) -> str:
        key = column_name.upper().strip()
        if key in self._domain_cache:
            return self._domain_cache[key]

        expanded_text = expand_erp_acronyms(column_name)
        col_embedding = self.model.encode([expanded_text], convert_to_numpy=True)
        col_norm = np.linalg.norm(col_embedding, axis=1, keepdims=True)
        col_embedding_norm = col_embedding / np.where(col_norm == 0, 1, col_norm)

        similarities = np.dot(col_embedding_norm, self.domain_embeddings_norm.T)[0]
        best_idx = int(np.argmax(similarities))
        res = self.domain_names[best_idx]
        self._domain_cache[key] = res
        return res

    def translate_columns(
        self,
        source_columns: List[str],
        target_schema: TargetSchemaDefinitionDTO,
        threshold: float = 0.60,
        target_lang: str = "es"
    ) -> SemanticMappingSuggestionDTO:
        suggested_mapping = {}
        confidence_scores = {}
        mapped_sources = set()
        mapped_targets = set()

        map_to_use = SPANISH_TO_ENGLISH_MAP if target_lang.lower() == "en" else ENGLISH_TO_SPANISH_MAP

        # Nivel L1: Matriz Estándar ERP (0 ms).
        # Prevención de conflictos: un target solo puede ser reclamado por UNA fuente.
        for col in source_columns:
            upper_col = col.upper().strip()
            if upper_col in map_to_use:
                tgt = map_to_use[upper_col]
                if tgt in mapped_targets:
                    continue
                suggested_mapping[col] = tgt
                confidence_scores[col] = 1.0
                mapped_sources.add(col)
                mapped_targets.add(tgt)

        unmapped_for_l2 = [c for c in source_columns if c not in mapped_sources]
        if unmapped_for_l2 and target_schema and target_schema.schema_map:
            available_targets = [k for k in target_schema.schema_map.keys() if k not in mapped_targets]
            if available_targets:
                target_keys = available_targets
                target_texts = [f"{k}: {target_schema.schema_map[k]}" for k in target_keys]
                target_embeddings = self.model.encode(target_texts, convert_to_numpy=True)
                cleaned_sources = [expand_erp_acronyms(c) for c in unmapped_for_l2]
                source_embeddings = self.model.encode(cleaned_sources, convert_to_numpy=True)

                source_norms = np.linalg.norm(source_embeddings, axis=1, keepdims=True)
                target_norms = np.linalg.norm(target_embeddings, axis=1, keepdims=True)
                source_normed = source_embeddings / np.where(source_norms == 0, 1, source_norms)
                target_normed = target_embeddings / np.where(target_norms == 0, 1, target_norms)

                similarities = np.dot(source_normed, target_normed.T)
                
                from scipy.optimize import linear_sum_assignment
                row_ind, col_ind = linear_sum_assignment(-similarities)
                
                for i, best_j in zip(row_ind, col_ind):
                    score = float(similarities[i][best_j])
                    s_col = unmapped_for_l2[i]
                    if score >= threshold:
                        suggested_mapping[s_col] = target_keys[best_j]
                        confidence_scores[s_col] = round(score, 4)
                        mapped_sources.add(s_col)

        unmapped = [c for c in source_columns if c not in mapped_sources]
        return SemanticMappingSuggestionDTO(
            suggested_mapping=suggested_mapping,
            confidence_scores=confidence_scores,
            unmapped_columns=unmapped
        )
