from typing import Dict, Any, List

class RelationalKeyGenerator:
    """
    Servidor atómico de dominio para la inyección de claves relacionales PK y FK 
    entre las entidades de la Capa Plata.
    """

    @staticmethod
    def inject_relational_keys(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for entity in entities:
            name = entity.get("entity_name", "").upper()
            cols = entity.get("selected_columns", [])
            
            if "CABECERA" in name or "HEADER" in name:
                if "FOLIO_ASIENTO_ID" not in cols:
                    cols.insert(0, "FOLIO_ASIENTO_ID")
            else:
                if "FK_FOLIO_ASIENTO_ID" not in cols:
                    cols.insert(0, "FK_FOLIO_ASIENTO_ID")
            
            entity["selected_columns"] = cols
        return entities
