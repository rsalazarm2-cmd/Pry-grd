from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from src.bronze.domain.ast import (
    ASTNode, ColumnNode, CastNode, FunctionNode, 
    RegexReplaceNode, CoalesceNode, AnalyticFunctionNode
)
from src.cleaning.domain.cleaning_strategies import (
    TrimStrategy as C_Trim,
    UppercaseStrategy as C_Upper,
    CleanDotsStrategy as C_Dots,
    CleanCommasStrategy as C_Commas,
    CleanColonsStrategy as C_Colons,
    CleanSpecialCharsStrategy as C_Chars,
    CleanAccentsAndNStrategy as C_Accents
)
from src.cleaning.domain.cleaning_ast import CleaningColumnNode
from src.cleaning.infrastructure.duckdb_cleaning_queries import DuckDbCleaningQueries

class RawSQLNode(ASTNode):
    def __init__(self, sql: str):
        self.sql = sql
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return self.sql # Directly return the SQL

class TransformationStrategy(ABC):
    """Interfaz abstracta para una regla de transformación (Strategy Pattern)."""
    @abstractmethod
    def apply(self, node: ASTNode) -> ASTNode:
        pass

# Adapter para reutilizar las estrategias del nuevo motor de limpieza
from src.cleaning.domain.cleaning_ast import CleaningColumnNode, CleaningRawSQLNode

class CleaningAdapterStrategy(TransformationStrategy):
    def __init__(self, cleaning_strategy):
        self.cleaning_strategy = cleaning_strategy
        
    def apply(self, node: ASTNode) -> ASTNode:
        if isinstance(node, ColumnNode):
            c_node = CleaningColumnNode(node.name)
        elif isinstance(node, RawSQLNode):
            c_node = CleaningRawSQLNode(node.sql)
        else:
            # Si recibimos un CastNode o similar antes de un adapter,
            # forzamos a resolver su SQL usando el visitor global
            from src.silver.infrastructure.duckdb_silver_query_builder import DuckDBASTVisitor
            visitor = DuckDBASTVisitor()
            sql = node.accept(visitor)
            c_node = CleaningRawSQLNode(sql)
            
        result_c_node = self.cleaning_strategy.apply(c_node)
        sql = DuckDbCleaningQueries.build_cleaning_expression(result_c_node)
        return RawSQLNode(sql)

class TrimStrategy(CleaningAdapterStrategy):
    def __init__(self): super().__init__(C_Trim())

class UppercaseStrategy(CleaningAdapterStrategy):
    def __init__(self): super().__init__(C_Upper())

class CleanDotsStrategy(CleaningAdapterStrategy):
    def __init__(self): super().__init__(C_Dots())

class CleanCommasStrategy(CleaningAdapterStrategy):
    def __init__(self): super().__init__(C_Commas())

class CleanColonsStrategy(CleaningAdapterStrategy):
    def __init__(self): super().__init__(C_Colons())

class CleanSpecialCharsStrategy(CleaningAdapterStrategy):
    def __init__(self): super().__init__(C_Chars())

class CleanAccentsAndNStrategy(CleaningAdapterStrategy):
    def __init__(self): super().__init__(C_Accents())

class CastStrategy(TransformationStrategy):
    def __init__(self, target_type: str, safe_cast: bool = True):
        self.target_type = target_type.upper()
        self.safe_cast = safe_cast
        
    def apply(self, node: ASTNode) -> ASTNode:
        if self.target_type == "CHAR":
            left_node = FunctionNode("left", [node, 3])
            return CastNode(left_node, "VARCHAR", self.safe_cast)
        
        return CastNode(node, self.target_type, self.safe_cast)

class ImputationStrategy(TransformationStrategy):
    def __init__(self, imputation_type: str, target_type: str, group_cols: List[str]):
        self.imputation_type = imputation_type
        self.target_type = target_type.upper()
        self.group_cols = group_cols

    def apply(self, node: ASTNode) -> ASTNode:
        if self.imputation_type == "NULL":
            return node
            
        if self.imputation_type == "DEFAULT":
            return self._build_default(node)
            
        if self.imputation_type == "ZERO":
            return self._build_zero(node)
            
        if self.imputation_type == "EMPTY":
            return self._build_empty(node)
            
        if self.imputation_type == "UNKNOWN":
            return self._build_unknown(node)
            
        if self.imputation_type.startswith("ADVANCED"):
            return self._build_advanced(node)
            
        return node
        
    def _build_zero(self, node: ASTNode) -> ASTNode:
        if self.target_type in ("DOUBLE", "FLOAT", "DECIMAL", "NUMERIC"):
            return CoalesceNode([node, CastNode(0, "DOUBLE", safe_cast=False)])
        return CoalesceNode([node, 0])
        
    def _build_empty(self, node: ASTNode) -> ASTNode:
        return CoalesceNode([node, ""])
        
    def _build_unknown(self, node: ASTNode) -> ASTNode:
        return CoalesceNode([node, "DESCONOCIDO"])
        
    def _build_default(self, node: ASTNode) -> ASTNode:
        if self.target_type == "DOUBLE":
            return CoalesceNode([node, CastNode(0, "DOUBLE", safe_cast=False)])
        if self.target_type in ("INTEGER", "BIGINT"):
            return CoalesceNode([node, 0])
        if self.target_type in ("DATE", "TIMESTAMP"):
            return node
        return CoalesceNode([node, "NO_REGISTRADO"])


    def _build_advanced(self, node: ASTNode) -> ASTNode:
        analytic_func = None
        if "MEAN" in self.imputation_type and self.target_type in ("DOUBLE", "INTEGER", "BIGINT"):
            avg_node = AnalyticFunctionNode("AVG", node, self.group_cols)
            analytic_func = FunctionNode("round", [avg_node, 2])
        elif "MEDIAN" in self.imputation_type and self.target_type in ("DOUBLE", "INTEGER", "BIGINT"):
            median_node = AnalyticFunctionNode("MEDIAN", node, self.group_cols)
            analytic_func = FunctionNode("round", [median_node, 2])
        elif "MODE" in self.imputation_type:
            analytic_func = AnalyticFunctionNode("MODE", node, self.group_cols)
            
        if analytic_func:
            fallback = self._build_default(node).children[1]
            return CoalesceNode([node, analytic_func, fallback])
            
        return self._build_default(node)

class PrefixDuplicateStrategy(TransformationStrategy):
    """Estrategia para anteponer el prefijo DUP_ a identificadores de asientos sospechosos."""
    def __init__(self, prefix: str = "DUP_"):
        self.prefix = prefix

    def apply(self, node: ASTNode) -> ASTNode:
        return FunctionNode("concat", [self.prefix, node])

