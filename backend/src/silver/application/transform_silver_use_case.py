from src.shared.domain.journal_entry import SilverTransformationResultDTO, BronzeToSilverRulesDTO
from src.shared.domain.journal_entry_repository import JournalEntryRepository
from src.bronze.domain.pipeline import TransformationPipelineBuilder

class TransformSilverDataUseCase:
    """
    Caso de uso Orquestador para estandarizar y enriquecer datos en la Capa Plata.
    Aplica el patrón de Responsabilidad Única: coordina el Dominio Puro con la Infraestructura.
    """

    def __init__(self, repository: JournalEntryRepository):
        self.repository = repository

    def execute(
        self,
        bronze_parquet_path: str,
        target_silver_path: str,
        rules: BronzeToSilverRulesDTO = None,
    ) -> SilverTransformationResultDTO:
        # 1. Habla con Infraestructura: "Dame el esquema crudo actual"
        column_names = self.repository.get_parquet_schema(bronze_parquet_path)
        
        # 2. Habla con Dominio Puro: "Construye los árboles de intenciones abstractas"
        pipelines = TransformationPipelineBuilder.build_from_dto(rules, column_names)
        
        # 3. Ordena a Infraestructura: "Ejecuta estos árboles nativamente en tu motor SQL"
        result_dto = self.repository.execute_silver_ast_pipelines(
            bronze_parquet_path, 
            target_silver_path, 
            pipelines
        )
        
        return result_dto
