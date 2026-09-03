from typing import Dict, List, Any, Optional

from src.shared.domain.journal_entry import TransformationRulesDTO
from src.bronze.domain.ast import ASTNode, ColumnNode
from src.bronze.domain.rules import (
    TransformationStrategy,
    TrimStrategy, UppercaseStrategy, CleanDotsStrategy, CleanCommasStrategy,
    CleanColonsStrategy, CleanSpecialCharsStrategy, CleanAccentsAndNStrategy,
    CastStrategy, ImputationStrategy
)

class ColumnTransformationPipeline:
    """Orquestador del Pipeline de Bronce que aplica las reglas de limpieza en cadena."""
    def __init__(self, col_name: str, target_name: str, strategies: List[TransformationStrategy]):
        self.col_name = col_name
        self.target_name = target_name
        self.strategies = strategies

    def build_ast(self) -> ASTNode:
        """Construye el AST completo aplicando las estrategias en orden secuencial."""
        node: ASTNode = ColumnNode(self.col_name)
        for strategy in self.strategies:
            node = strategy.apply(node)
        return node


class TransformationPipelineBuilder:
    """Constructor del Pipeline en la Capa Bronce para generar la Capa Plata limpia."""
    
    @staticmethod
    def _extract_global_settings(rules: Optional[TransformationRulesDTO]) -> Dict[str, bool]:
        return {
            "trim": getattr(rules, "global_trim_spaces", getattr(rules, "global_trim", True)) if rules else True,
            "uppercase": getattr(rules, "global_convert_uppercase", True) if rules else True,
            "chars": getattr(rules, "global_clean_special_chars", getattr(rules, "global_clean_accents_and_symbols", False)) if rules else False,
            "accents": getattr(rules, "global_clean_accents_and_n", False) if rules else False,
            "colons": getattr(rules, "global_clean_colons", False) if rules else False,
            "dots": getattr(rules, "global_clean_dots", False) if rules else False,
            "commas": getattr(rules, "global_clean_commas", False) if rules else False,
        }

    @staticmethod
    def _extract_column_settings(col: str, rule: Any, globals: Dict[str, bool]) -> Dict[str, Any]:
        return {
            "clean_chars": getattr(rule, "clean_special_chars", globals["chars"]) if rule and getattr(rule, "clean_special_chars", None) is not None else globals["chars"],
            "clean_dots": getattr(rule, "clean_dots", globals["dots"]) if rule and getattr(rule, "clean_dots", None) is not None else globals["dots"],
            "clean_commas": getattr(rule, "clean_commas", globals["commas"]) if rule and getattr(rule, "clean_commas", None) is not None else globals["commas"],
            "target_type": (getattr(rule, "target_data_type", "VARCHAR") or "VARCHAR").upper() if rule else "VARCHAR",
            "imputation": getattr(rule, "null_imputation", "DEFAULT") if rule else "DEFAULT",
            "group_cols": getattr(rule, "group_by_columns", []) if rule else [],
            "target_name": ((getattr(rule, "new_column_name", "") or "").strip() or col).upper() if rule else col.upper()
        }

    @staticmethod
    def _build_strategies(settings: Dict[str, Any], globals: Dict[str, bool], valid_group_cols: List[str]) -> List[TransformationStrategy]:
        strategies: List[TransformationStrategy] = []
        is_numeric = settings["target_type"] in ("DOUBLE", "INTEGER", "BIGINT")
        is_date = settings["target_type"] in ("DATE", "TIMESTAMP")
        
        # 1. Recorte de espacios SIEMPRE primero
        if globals["trim"]:
            strategies.append(TrimStrategy())

        # 2. Si la columna es DATE o TIMESTAMP, no alterar símbolos de fecha (/ : -)
        if is_date:
            strategies.append(CastStrategy(settings["target_type"], safe_cast=True))
            strategies.append(ImputationStrategy(settings["imputation"], settings["target_type"], valid_group_cols))
            return strategies

        if not is_numeric or settings["clean_dots"] or settings["clean_commas"]:
            strategies.append(CastStrategy("VARCHAR", safe_cast=False))
            
        if not is_numeric:
            if globals["accents"]:
                strategies.append(CleanAccentsAndNStrategy())
            if globals["colons"]:
                strategies.append(CleanColonsStrategy())
            if settings["clean_chars"]:
                strategies.append(CleanSpecialCharsStrategy())
                
        if settings["clean_dots"]:
            strategies.append(CleanDotsStrategy())
        if settings["clean_commas"]:
            strategies.append(CleanCommasStrategy())
            
        if not is_numeric and globals.get("uppercase", True):
            strategies.append(UppercaseStrategy())

        if settings["target_type"] != "VARCHAR" or is_numeric:
            strategies.append(CastStrategy(settings["target_type"], safe_cast=True))
            
        strategies.append(ImputationStrategy(settings["imputation"], settings["target_type"], valid_group_cols))
        return strategies


    @classmethod
    def build_from_dto(cls, rules: TransformationRulesDTO, column_names: List[str]) -> Dict[str, ColumnTransformationPipeline]:
        pipelines = {}
        global_settings = cls._extract_global_settings(rules)
        column_rules = getattr(rules, "column_rules", getattr(rules, "columns", {})) if rules else {}
        
        used_target_names: Dict[str, int] = {}

        for col in column_names:
            rule = column_rules.get(col)
            if rule and getattr(rule, "include_in_silver", True) is False:
                continue
                
            col_settings = cls._extract_column_settings(col, rule, global_settings)
            
            target_name = col_settings["target_name"]
            if target_name in used_target_names:
                used_target_names[target_name] += 1
                col_settings["target_name"] = f"{target_name}_{used_target_names[target_name]}"
            else:
                used_target_names[target_name] = 1

            valid_group_cols = [gc for gc in col_settings["group_cols"] if gc in column_names]
            strategies = cls._build_strategies(col_settings, global_settings, valid_group_cols)
            pipelines[col] = ColumnTransformationPipeline(col, col_settings["target_name"], strategies)
            
        return pipelines
