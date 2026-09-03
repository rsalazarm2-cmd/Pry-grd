from typing import List, Union

class CleaningASTNode:
    """Clase base para todos los nodos del AST de limpieza de datos."""
    pass

class CleaningRawSQLNode(CleaningASTNode):
    def __init__(self, sql: str):
        self.sql = sql

class CleaningColumnNode(CleaningASTNode):
    def __init__(self, name: str):
        self.name = name

class CleaningFunctionNode(CleaningASTNode):
    def __init__(self, function_name: str, arguments: List[Union[CleaningASTNode, str, int, float]]):
        self.function_name = function_name
        self.arguments = arguments

class CleaningRegexReplaceNode(CleaningASTNode):
    def __init__(self, source_node: CleaningASTNode, pattern: str, replacement: str, flags: str = 'g'):
        self.source_node = source_node
        self.pattern = pattern
        self.replacement = replacement
        self.flags = flags

class CleaningCastNode(CleaningASTNode):
    def __init__(self, source_node: CleaningASTNode, target_type: str, safe_cast: bool = True):
        self.source_node = source_node
        self.target_type = target_type
        self.safe_cast = safe_cast

class CleaningCoalesceNode(CleaningASTNode):
    def __init__(self, arguments: List[Union[CleaningASTNode, str, int, float]]):
        self.arguments = arguments
