from ninja import NinjaAPI

from src.shared.api.health_router import router as health_router
from src.project.api.project_router import router as project_router
from src.bronze.api.bronze_router import router as bronze_router
from src.silver.api.silver_router import router as silver_router
from src.gold.api.gold_router import router as gold_router
from src.ai_translator.api.translator_router import router as ai_router
from src.shared.api.pipeline_router import router as pipeline_router
from src.shared.middle_layer.middle_layer_router import router as middle_layer_router
from src.cleaning.api.cleaning_router import router as cleaning_router
from src.transformations.api.transformation_router import router as transformation_router
from audit_system.backend.api.views import router as audit_router
from src.core.api.audit_trail_router import router as audit_trail_router

api = NinjaAPI(
    title="Medallion Analytics API",
    version="1.1.0",
    description="API REST para la Arquitectura Medallion (Bronce, Plata, Oro) utilizando Clean Architecture, DuckDB Nativo y Parquet.",
)

# Registro de API Routers por Sub-dominio de Negocio
api.add_router("/", health_router)
api.add_router("/", project_router)
api.add_router("/bronze", bronze_router)
api.add_router("/silver", silver_router)
api.add_router("/gold", gold_router)
api.add_router("/audit", audit_router)
api.add_router("/core", audit_trail_router)
api.add_router("/ai", ai_router)
api.add_router("/pipeline", pipeline_router)
api.add_router("/middle-layer", middle_layer_router)
api.add_router("/cleaning", cleaning_router)
api.add_router("/transformations", transformation_router)
