# 📖 12. DICCIONARIO DE DATOS Y TIPOS PYDANTIC / TYPESCRIPT
### Especificación Completa de Contratos DTO, Interfaces y Schemas JSON
**Proyecto de Maestría en Analítica de Datos | Stack: Pydantic V2, TypeScript Strict Mode**

---

## 📌 1. CONTRATOS DE DATOS Y DTOS EN PYTHON (`src/shared/domain/journal_entry.py`)

### 1. `DatasetProfileDTO` (Perfil Estadístico de Dataset)
```python
class ColumnProfileDTO(BaseModel):
    name: str
    inferred_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    mean: Optional[float] = None
    min_val: Optional[str] = None
    max_val: Optional[str] = None

class DatasetProfileDTO(BaseModel):
    total_rows: int
    total_columns: int
    file_size_bytes: int
    file_hash_sha256: str
    columns: List[ColumnProfileDTO]
```

### 2. `BronzeToSilverRulesDTO` (Reglas de Transformación y Limpieza)
```python
class ColumnCleaningRuleDTO(BaseModel):
    source_column: str
    target_column: str
    target_type: str
    trim_whitespace: bool = True
    uppercase: bool = False
    impute_zero_if_null: bool = False

class BronzeToSilverRulesDTO(BaseModel):
    project_id: str
    column_rules: List[ColumnCleaningRuleDTO]
    filter_zero_rows: bool = False
```

---

## 🎨 2. INTERFACES DE TYPESCRIPT EN FRONTEND (`frontend/src/types/`)

### 1. `frontend/src/types/bronze.ts`
```typescript
export interface ColumnProfile {
  name: string;
  inferred_type: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  mean?: number;
  min_val?: string;
  max_val?: string;
}

export interface DatasetProfile {
  total_rows: number;
  total_columns: number;
  file_size_bytes: number;
  file_hash_sha256: string;
  columns: ColumnProfile[];
}
```
