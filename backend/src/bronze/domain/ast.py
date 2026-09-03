from abc import ABC, abstractmethod
from typing import List, Any

class ASTNode(ABC):
    """Nodo base abstracto del Árbol de Sintaxis Abstracta (AST) de transformación."""
    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        pass

class ASTVisitor(ABC):
    """Patrón Visitor para desacoplar el árbol lógico del motor SQL objetivo."""
    @abstractmethod
    def visit_column(self, node: 'ColumnNode') -> Any:
        pass
    @abstractmethod
    def visit_cast(self, node: 'CastNode') -> Any:
        pass
    @abstractmethod
    def visit_function(self, node: 'FunctionNode') -> Any:
        pass
    @abstractmethod
    def visit_regex_replace(self, node: 'RegexReplaceNode') -> Any:
        pass
    @abstractmethod
    def visit_coalesce(self, node: 'CoalesceNode') -> Any:
        pass
    @abstractmethod
    def visit_analytic_function(self, node: 'AnalyticFunctionNode') -> Any:
        pass

class ColumnNode(ASTNode):
    def __init__(self, name: str):
        self.name = name
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_column(self)

class CastNode(ASTNode):
    def __init__(self, child: Any, target_type: str, safe_cast: bool = True):
        self.child = child
        self.target_type = target_type
        self.safe_cast = safe_cast
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_cast(self)

class FunctionNode(ASTNode):
    def __init__(self, name: str, args: List[Any]):
        self.name = name
        self.args = args
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function(self)

class RegexReplaceNode(ASTNode):
    def __init__(self, child: ASTNode, pattern: str, replace: str, flags: str = 'g'):
        self.child = child
        self.pattern = pattern
        self.replace = replace
        self.flags = flags
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_regex_replace(self)

class CoalesceNode(ASTNode):
    def __init__(self, children: List[Any]):
        self.children = children
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_coalesce(self)

class AnalyticFunctionNode(ASTNode):
    def __init__(self, function_name: str, child: ASTNode, partition_by: List[str]):
        self.function_name = function_name
        self.child = child
        self.partition_by = partition_by
    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_analytic_function(self)
