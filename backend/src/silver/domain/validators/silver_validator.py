from typing import List, Optional
from dataclasses import dataclass
from src.shared.domain.exceptions.domain_exceptions import InvalidTransformationRuleError

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]

class SilverRecipeValidator:
    """Validador de Dominio Puro para validar recetas de transformación Plata antes de ejecutar SQL."""

    @staticmethod
    def validate(column_names: List[str], rules: Optional[Any] = None) -> ValidationResult:
        errors = []
        if not column_names:
            errors.append("El dataset fuente no contiene columnas procesables.")

        if rules and hasattr(rules, "column_rules") and rules.column_rules:
            for col_name, rule in rules.column_rules.items():
                if col_name not in column_names:
                    errors.append(f"La columna '{col_name}' especificada en las reglas de limpieza no existe en el dataset.")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
