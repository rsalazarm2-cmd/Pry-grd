from src.transformations.domain.transformation_ast import (
    TransformationASTNode, TransColNode, TransDateDiffNode, 
    TransConcatNode, TransCaseWhenNode, TransConditionNode, TransLiteralNode
)

class DuckDbTransformationQueries:
    """
    Traduce los Nodos AST de Transformación (Enriquecimiento) al dialecto SQL de DuckDB.
    Actúa como un 'Paquete SQL' para operaciones analíticas y de negocio.
    """
    @classmethod
    def build_transformation_expression(cls, node: TransformationASTNode) -> str:
        builder = cls()
        return builder.visit(node)

    def visit(self, node: TransformationASTNode) -> str:
        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: TransformationASTNode):
        raise NotImplementedError(f"No hay visit_{type(node).__name__.lower()} definido.")

    def visit_transcolnode(self, node: TransColNode) -> str:
        return f'"{node.name}"'

    def visit_transliteralnode(self, node: TransLiteralNode) -> str:
        if isinstance(node.value, str):
            return f"'{node.value}'"
        return str(node.value)

    def visit_transdatediffnode(self, node: TransDateDiffNode) -> str:
        start_sql = self.visit(node.start_date_node)
        end_sql = self.visit(node.end_date_node)
        return f"date_diff('{node.date_part}', {start_sql}::DATE, {end_sql}::DATE)"

    def visit_transconcatnode(self, node: TransConcatNode) -> str:
        parts = []
        for n in node.nodes:
            parts.append(f"COALESCE(CAST({self.visit(n)} AS VARCHAR), '')")
        
        sep = f" || '{node.separator}' || "
        return sep.join(parts)

    def visit_transconditionnode(self, node: TransConditionNode) -> str:
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"{left} {node.operator} {right}"

    def visit_transcasewhennode(self, node: TransCaseWhenNode) -> str:
        cases = []
        for condition, result in node.conditions:
            cond_sql = self.visit(condition)
            res_sql = self.visit(result)
            cases.append(f"WHEN {cond_sql} THEN {res_sql}")
            
        cases_sql = " ".join(cases)
        default_sql = self.visit(node.default_node)
        return f"CASE {cases_sql} ELSE {default_sql} END"
