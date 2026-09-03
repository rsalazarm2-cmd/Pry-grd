from abc import ABC, abstractmethod
from typing import List
from .cleaning_ast import (
    CleaningASTNode, CleaningFunctionNode, CleaningRegexReplaceNode, 
    CleaningCastNode, CleaningCoalesceNode
)

class CleaningStrategy(ABC):
    @abstractmethod
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        pass

class TrimStrategy(CleaningStrategy):
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        varchar_node = CleaningCastNode(node, "VARCHAR", safe_cast=False)
        return CleaningFunctionNode("trim", [varchar_node])

class UppercaseStrategy(CleaningStrategy):
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        return CleaningFunctionNode("upper", [node])

class CleanDotsStrategy(CleaningStrategy):
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        return CleaningFunctionNode("replace", [node, ".", ""])

class CleanCommasStrategy(CleaningStrategy):
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        return CleaningFunctionNode("replace", [node, ",", ""])

class CleanColonsStrategy(CleaningStrategy):
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        return CleaningFunctionNode("replace", [node, ":", ""])

class CleanSpecialCharsStrategy(CleaningStrategy):
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        return CleaningRegexReplaceNode(node, r'[()\\/&%$#"!;=?¿¡*+\[\]{}|~^]', '', 'g')

class CleanAccentsAndNStrategy(CleaningStrategy):
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        current = node
        replacements = [
            (r'[áàäâ]', 'a'), (r'[éèëê]', 'e'), (r'[íìïî]', 'i'),
            (r'[óòöô]', 'o'), (r'[úùüû]', 'u'), (r'[ñÑ]', 'n'),
            (r'[ÁÀÄÂ]', 'A')
        ]
        for pattern, replace in replacements:
            current = CleaningRegexReplaceNode(current, pattern, replace, 'g')
        return current

class SmartDateCastStrategy(CleaningStrategy):
    """
    Parsea fechas evaluando dinámicamente si tienen el año a 2 dígitos (ej: 29/05/26).
    """
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        return CleaningFunctionNode("smart_date_cast", [node])

class CastStrategy(CleaningStrategy):
    def __init__(self, target_type: str, safe_cast: bool = True):
        self.target_type = target_type.upper()
        self.safe_cast = safe_cast
        
    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        return CleaningCastNode(node, self.target_type, self.safe_cast)

class DefaultImputationStrategy(CleaningStrategy):
    def __init__(self, target_type: str):
        self.target_type = target_type.upper()

    def apply(self, node: CleaningASTNode) -> CleaningASTNode:
        if self.target_type == "DOUBLE":
            return CleaningCoalesceNode([node, CleaningCastNode(0, "DOUBLE", safe_cast=False)])
        if self.target_type in ("INTEGER", "BIGINT"):
            return CleaningCoalesceNode([node, 0])
        if self.target_type in ("DATE", "TIMESTAMP"):
            return node
        return CleaningCoalesceNode([node, "NO_REGISTRADO"])

