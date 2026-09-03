from typing import List, Union, Any

class TransformationASTNode:
    """Clase base para todos los nodos del AST de transformaciones (Enriquecimiento)."""
    pass

class TransColNode(TransformationASTNode):
    def __init__(self, name: str):
        self.name = name

class TransLiteralNode(TransformationASTNode):
    def __init__(self, value: Any):
        self.value = value

class TransDateDiffNode(TransformationASTNode):
    def __init__(self, date_part: str, start_date_node: TransformationASTNode, end_date_node: TransformationASTNode):
        self.date_part = date_part
        self.start_date_node = start_date_node
        self.end_date_node = end_date_node

class TransConcatNode(TransformationASTNode):
    def __init__(self, nodes: List[TransformationASTNode], separator: str = ""):
        self.nodes = nodes
        self.separator = separator

class TransCaseWhenNode(TransformationASTNode):
    def __init__(self, conditions: List[tuple[TransformationASTNode, TransformationASTNode]], default_node: TransformationASTNode):
        self.conditions = conditions # List of (condition_expr, result_expr)
        self.default_node = default_node

class TransConditionNode(TransformationASTNode):
    def __init__(self, operator: str, left: TransformationASTNode, right: TransformationASTNode):
        self.operator = operator
        self.left = left
        self.right = right
