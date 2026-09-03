from src.cleaning.domain.cleaning_ast import (
    CleaningASTNode, CleaningColumnNode, CleaningFunctionNode, 
    CleaningRegexReplaceNode, CleaningCastNode, CleaningCoalesceNode, CleaningRawSQLNode
)

class DuckDbCleaningQueries:
    """
    Traduce los Nodos AST de Limpieza al dialecto SQL de DuckDB.
    Incluye Motor Inteligente de Fechas (soporta años a 2 y 4 dígitos, ISO, Oracle).
    """
    @classmethod
    def build_cleaning_expression(cls, node: CleaningASTNode) -> str:
        builder = cls()
        return builder.visit(node)

    def visit(self, node: CleaningASTNode) -> str:
        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: CleaningASTNode):
        raise NotImplementedError(f"No hay visit_{type(node).__name__.lower()} definido.")

    def visit_cleaningcolumnnode(self, node: CleaningColumnNode) -> str:
        return f'"{node.name}"'
        
    def visit_cleaningrawsqlnode(self, node: CleaningRawSQLNode) -> str:
        return node.sql

    def visit_cleaningfunctionnode(self, node: CleaningFunctionNode) -> str:
        if node.function_name == "smart_date_cast":
            col_sql = self.visit(node.arguments[0])
            return f"({self._build_smart_date_expr(col_sql)})::DATE"
        
        args = []
        for arg in node.arguments:
            if isinstance(arg, CleaningASTNode):
                args.append(self.visit(arg))
            elif isinstance(arg, str):
                args.append(f"'{arg}'")
            else:
                args.append(str(arg))
        return f"{node.function_name}({', '.join(args)})"

    def visit_cleaningregexreplacenode(self, node: CleaningRegexReplaceNode) -> str:
        src = self.visit(node.source_node)
        return f"regexp_replace({src}, '{node.pattern}', '{node.replacement}', '{node.flags}')"

    def _build_smart_date_expr(self, src: str) -> str:
        base = f"trim(CAST({src} AS VARCHAR))"
        clean = f"split_part(split_part({base}, 'T', 1), ' ', 1)"
        return f"""CASE
            WHEN regexp_matches({clean}, '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{2}}$') THEN COALESCE(TRY_STRPTIME({clean}, '%d/%m/%y'), TRY_STRPTIME({clean}, '%m/%d/%y'))
            WHEN regexp_matches({clean}, '^[0-9]{{1,2}}-[0-9]{{1,2}}-[0-9]{{2}}$') THEN COALESCE(TRY_STRPTIME({clean}, '%d-%m-%y'), TRY_STRPTIME({clean}, '%m-%d-%y'))
            WHEN regexp_matches({clean}, '^[0-9]{{4}}-[0-9]{{1,2}}-[0-9]{{1,2}}$') THEN TRY_CAST({clean} AS DATE)
            WHEN regexp_matches({clean}, '^[0-9]{{4}}/[0-9]{{1,2}}/[0-9]{{1,2}}$') THEN TRY_STRPTIME({clean}, '%Y/%m/%d')
            WHEN regexp_matches({clean}, '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$') THEN COALESCE(TRY_STRPTIME({clean}, '%d/%m/%Y'), TRY_STRPTIME({clean}, '%m/%d/%Y'))
            WHEN regexp_matches({clean}, '^[0-9]{{1,2}}-[A-Za-z]{{3}}-[0-9]{{4}}$') THEN TRY_STRPTIME({clean}, '%d-%b-%Y')
            ELSE TRY_CAST({clean} AS DATE)
        END"""

    def _build_smart_timestamp_expr(self, src: str) -> str:
        base = f"trim(CAST({src} AS VARCHAR))"
        clean_ts = f"replace({base}, 'T', ' ')"
        date_part = self._build_smart_date_expr(src)
        return f"""CASE
            WHEN regexp_matches({clean_ts}, '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{2}}') THEN CAST(({date_part}) AS TIMESTAMP)
            ELSE COALESCE(TRY_STRPTIME({clean_ts}, '%Y-%m-%d %H:%M:%S'), TRY_STRPTIME({clean_ts}, '%d/%m/%Y %H:%M:%S'), TRY_CAST({clean_ts} AS TIMESTAMP), CAST(({date_part}) AS TIMESTAMP))
        END"""

    def visit_cleaningcastnode(self, node: CleaningCastNode) -> str:
        src = self.visit(node.source_node)
        tgt = node.target_type.upper()
        if tgt == "DATE":
            return f"({self._build_smart_date_expr(src)})::DATE"
        if tgt == "TIMESTAMP":
            return f"({self._build_smart_timestamp_expr(src)})::TIMESTAMP"
        cast_func = "TRY_CAST" if node.safe_cast else "CAST"
        return f"{cast_func}({src} AS {tgt})"

    def visit_cleaningcoalescenode(self, node: CleaningCoalesceNode) -> str:
        args = []
        for arg in node.arguments:
            if isinstance(arg, CleaningASTNode):
                args.append(self.visit(arg))
            elif isinstance(arg, str) and not arg.startswith(("DATE", "TIMESTAMP")):
                args.append(f"'{arg}'")
            else:
                args.append(str(arg))
        return f"COALESCE({', '.join(args)})"
