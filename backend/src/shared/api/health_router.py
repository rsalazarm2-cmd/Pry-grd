from ninja import Router
from pydantic import BaseModel

router = Router()


class HealthCheckDTO(BaseModel):
    status: str
    architecture: str
    engine: str
    version: str


@router.get("/health", response=HealthCheckDTO, tags=["Health"])
def health_check(request):
    return HealthCheckDTO(
        status="healthy",
        architecture="Clean Architecture / Hexagonal (Puertos y Adaptadores)",
        engine="DuckDB Nativo + Parquet (Medallion Multi-Proyecto)",
        version="1.1.0",
    )
