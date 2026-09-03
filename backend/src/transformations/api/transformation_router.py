import logging
from typing import List, Dict, Any
from ninja import Router, Schema
from src.transformations.application.apply_transformations_use_case import ApplyTransformationsUseCase
from src.transformations.domain.transformation_strategies import (
    CalculateDaysDifferenceStrategy, ConcatDimensionsStrategy, CategorizeRiskStrategy
)

logger = logging.getLogger(__name__)
router = Router()

class TransformationRequest(Schema):
    target_alias: str
    strategy: str
    args: Dict[str, Any]

@router.post("/build-sql", tags=["Transformations Engine"])
def build_transformation_sql(request, payload: TransformationRequest) -> Dict[str, str]:
    """Generates the raw SQL string for an analytical transformation."""
    try:
        strategy_obj = None
        if payload.strategy == "DATE_DIFF":
            strategy_obj = CalculateDaysDifferenceStrategy(
                start_col=payload.args.get("start_col"), 
                end_col=payload.args.get("end_col")
            )
        elif payload.strategy == "CONCAT":
            strategy_obj = ConcatDimensionsStrategy(
                cols=payload.args.get("cols", []),
                separator=payload.args.get("separator", "_")
            )
        elif payload.strategy == "RISK_CATEGORY":
            strategy_obj = CategorizeRiskStrategy(
                days_col=payload.args.get("days_col"),
                high_risk_threshold=payload.args.get("threshold", 30)
            )
        else:
            return {"error": f"Strategy {payload.strategy} not supported"}
            
        use_case = ApplyTransformationsUseCase()
        sql_expr = use_case.execute_for_column(strategy_obj, payload.target_alias)
        
        return {"target_alias": payload.target_alias, "sql": sql_expr}
    except Exception as e:
        logger.error(f"Error building transformation SQL: {e}", exc_info=True)
        return {"error": str(e)}
