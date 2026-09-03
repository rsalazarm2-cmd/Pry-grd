import logging
from typing import List, Dict, Any
from ninja import Router, Schema
from src.cleaning.application.clean_dataset_use_case import CleanDatasetUseCase
from src.cleaning.domain.cleaning_strategies import (
    TrimStrategy, UppercaseStrategy, CleanSpecialCharsStrategy, 
    SmartDateCastStrategy, DefaultImputationStrategy
)

logger = logging.getLogger(__name__)
router = Router()

class CleanColumnRequest(Schema):
    column_name: str
    strategies: List[str]
    target_type: str = "VARCHAR"

@router.post("/build-sql", tags=["Cleaning Engine"])
def build_cleaning_sql(request, payload: CleanColumnRequest) -> Dict[str, str]:
    """Generates the raw SQL string for cleaning a specific column using the AST Engine."""
    try:
        strategy_objects = []
        for strat in payload.strategies:
            if strat == "TRIM": strategy_objects.append(TrimStrategy())
            elif strat == "UPPER": strategy_objects.append(UppercaseStrategy())
            elif strat == "CLEAN_SPECIAL": strategy_objects.append(CleanSpecialCharsStrategy())
            elif strat == "SMART_DATE": strategy_objects.append(SmartDateCastStrategy())
            elif strat == "IMPUTE_DEFAULT": strategy_objects.append(DefaultImputationStrategy(payload.target_type))
            
        use_case = CleanDatasetUseCase()
        sql_expr = use_case.execute_for_column(payload.column_name, strategy_objects)
        
        return {"column": payload.column_name, "sql": sql_expr}
    except Exception as e:
        logger.error(f"Error building cleaning SQL: {e}", exc_info=True)
        return {"error": str(e)}
