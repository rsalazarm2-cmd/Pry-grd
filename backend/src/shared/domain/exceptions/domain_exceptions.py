class DomainException(Exception):
    """Excepción base para todos los errores de Dominio del Datamart Medallion."""
    pass

class DatasetNotFoundError(DomainException):
    """Lanzada cuando un archivo o dataset Parquet no se encuentra en el almacenamiento."""
    def __init__(self, dataset_path: str):
        super().__init__(f"El dataset en la ruta '{dataset_path}' no existe.")
        self.dataset_path = dataset_path

class InvalidTransformationRuleError(DomainException):
    """Lanzada cuando una regla de transformación de Plata u Oro es lógicamente inválida."""
    def __init__(self, rule_name: str, reason: str):
        super().__init__(f"Regla '{rule_name}' inválida: {reason}")
        self.rule_name = rule_name
        self.reason = reason

class ProjectLockedError(DomainException):
    """Lanzada cuando un proyecto está siendo modificado concurrentemente."""
    def __init__(self, project_id: str):
        super().__init__(f"El proyecto '{project_id}' está bloqueado por otra operación.")
        self.project_id = project_id
