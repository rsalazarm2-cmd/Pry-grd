from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class TopFrequencyItem(BaseModel):
    value: str
    count: int
    percentage: float

class ColumnProfileDTO(BaseModel):
    column_name: str
    domain_category: str
    data_type: str
    null_count: int
    total_rows: int
    null_percentage: float
    unique_count: int
    uniqueness_ratio: float
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    mean_value: Optional[float] = None
    stddev_value: Optional[float] = None
    sum_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    top_frequencies: List[TopFrequencyItem] = Field(default_factory=list)
    sample_values: List[str] = Field(default_factory=list)
    contains_dots: bool = False
    contains_commas: bool = False
    status_label: str = Field(default="Unknown")
    status_color: str = Field(default="gray")

class DatasetProfileDTO(BaseModel):
    file_path: str
    total_rows: int
    total_columns: int
    file_size_bytes: int
    data_health_score: float = Field(default=100.0)
    constant_columns_count: int = Field(default=0)
    null_columns_count: int = Field(default=0)
    perfect_columns_count: int = Field(default=0)
    columns: List[ColumnProfileDTO] = Field(default_factory=list)
    domain_summary: Dict[str, int] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
