from abc import ABC, abstractmethod
from typing import List
from .transformation_ast import (
    TransformationASTNode, TransColNode, TransDateDiffNode, 
    TransConcatNode, TransCaseWhenNode, TransConditionNode, TransLiteralNode
)

class TransformationStrategy(ABC):
    @abstractmethod
    def apply(self) -> TransformationASTNode:
        pass

class CalculateDaysDifferenceStrategy(TransformationStrategy):
    """Calcula la diferencia en días entre dos columnas de fecha."""
    def __init__(self, start_col: str, end_col: str):
        self.start_col = start_col
        self.end_col = end_col
        
    def apply(self) -> TransformationASTNode:
        start_node = TransColNode(self.start_col)
        end_node = TransColNode(self.end_col)
        return TransDateDiffNode('day', start_node, end_node)

class ConcatDimensionsStrategy(TransformationStrategy):
    """Concatena múltiples columnas para generar una llave primaria compuesta."""
    def __init__(self, cols: List[str], separator: str = "_"):
        self.cols = cols
        self.separator = separator
        
    def apply(self) -> TransformationASTNode:
        nodes = [TransColNode(col) for col in self.cols]
        return TransConcatNode(nodes, self.separator)

class CategorizeRiskStrategy(TransformationStrategy):
    """Ejemplo de lógica de negocio: Clasifica riesgo según días de diferencia."""
    def __init__(self, days_col: str, high_risk_threshold: int):
        self.days_col = days_col
        self.threshold = high_risk_threshold

    def apply(self) -> TransformationASTNode:
        col_node = TransColNode(self.days_col)
        threshold_node = TransLiteralNode(self.threshold)
        
        # Condition: days_col > threshold
        condition = TransConditionNode('>', col_node, threshold_node)
        
        return TransCaseWhenNode(
            conditions=[(condition, TransLiteralNode("RIESGO ALTO"))],
            default_node=TransLiteralNode("NORMAL")
        )
