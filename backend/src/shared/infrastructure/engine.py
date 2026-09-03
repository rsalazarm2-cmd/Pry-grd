import duckdb


class DuckDBEngine:
    """Gestor de Conexiones e Invocaciones del Motor OLAP DuckDB in-memory."""

    def __init__(self, db_connection: duckdb.DuckDBPyConnection = None):
        self.conn = db_connection or duckdb.connect(database=":memory:")

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        return self.conn
