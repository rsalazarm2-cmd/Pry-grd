from typing import Any
from src.bronze.domain.ast import (
    ASTVisitor, ASTNode, ColumnNode, CastNode, FunctionNode,
    RegexReplaceNode, CoalesceNode, AnalyticFunctionNode
)

from src.shared.infrastructure.date_helpers import build_smart_date_cast_sql, build_smart_timestamp_cast_sql

class DuckDBASTVisitor(ASTVisitor):
    """
    Traductor concreto que convierte nodos de un Árbol de Sintaxis Abstracta (AST)
    a sentencias SQL nativas y ultra-optimizadas para DuckDB.
    """
    
    def visit_column(self, node: ColumnNode) -> str:
        # En SQL, los nombres de columna deben ir entre comillas dobles para evitar problemas con palabras reservadas
        return f'"{node.name}"'

    def visit_cast(self, node: CastNode) -> str:
        if isinstance(node.child, ASTNode):
            child_sql = node.child.accept(self)
        elif isinstance(node.child, str):
            child_sql = f"'{node.child}'"
        else:
            child_sql = str(node.child)
            
        target = node.target_type.upper()
        if target == "DATE":
            return build_smart_date_cast_sql(child_sql)
        elif target == "TIMESTAMP":
            return build_smart_timestamp_cast_sql(child_sql)

        if node.safe_cast:
            return f"TRY_CAST({child_sql} AS {node.target_type})"
        return f"CAST({child_sql} AS {node.target_type})"

    def visit_function(self, node: FunctionNode) -> str:
        # Evalúa los argumentos: si son nodos AST los visita, si son literales los interpola
        args_sql = []
        for arg in node.args:
            if isinstance(arg, ASTNode):
                args_sql.append(arg.accept(self))
            elif isinstance(arg, str):
                # Literales string en SQL van con comillas simples
                args_sql.append(f"'{arg}'")
            else:
                # Literales numéricos o booleanos
                args_sql.append(str(arg))
                
        return f"{node.name}({', '.join(args_sql)})"

    def visit_regex_replace(self, node: RegexReplaceNode) -> str:
        child_sql = node.child.accept(self)
        return f"regexp_replace({child_sql}, '{node.pattern}', '{node.replace}', '{node.flags}')"

    def visit_coalesce(self, node: CoalesceNode) -> str:
        args_sql = []
        for arg in node.children:
            if isinstance(arg, ASTNode):
                args_sql.append(arg.accept(self))
            elif isinstance(arg, str) and not arg.startswith(('DATE ', 'TIMESTAMP ')):
                args_sql.append(f"'{arg}'")
            else:
                args_sql.append(str(arg))
                
        return f"coalesce({', '.join(args_sql)})"

    def visit_analytic_function(self, node: AnalyticFunctionNode) -> str:
        child_sql = node.child.accept(self)
        partition_sql = ""
        if node.partition_by:
            partition_cols = [f'"{col}"' for col in node.partition_by]
            partition_sql = f"PARTITION BY {', '.join(partition_cols)}"
            
        return f"{node.function_name}({child_sql}) OVER ({partition_sql})"


class DuckDbSilverQueryBuilder:
    """Constructor principal que orquesta la generación de la query final."""
    
    @staticmethod
    def build_select_expressions(pipelines: dict, selected_cols: list[str] = None) -> list[str]:
        """
        Recibe un diccionario de pipelines {columna_origen: ColumnTransformationPipeline}
        y devuelve una lista de strings con las sentencias SELECT de DuckDB.
        Si se pasa selected_cols, filtra únicamente las columnas indicadas para modelado multitabla.
        """
        visitor = DuckDBASTVisitor()
        select_expressions = []
        
        for col_name, pipeline in pipelines.items():
            if selected_cols and col_name not in selected_cols and pipeline.target_name not in selected_cols:
                continue
            # 1. Construir el árbol de intenciones (AST) puramente lógico
            ast_root = pipeline.build_ast()
            
            # 2. Traducir el AST a SQL de DuckDB usando el Visitor
            sql_expr = ast_root.accept(visitor)
            
            # 3. Empaquetar con el alias
            select_expressions.append(f'{sql_expr} AS "{pipeline.target_name}"')
            
        return select_expressions

