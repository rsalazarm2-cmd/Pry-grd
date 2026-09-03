export const CALCULATED_FUNCTIONS = [
  {
    value: 'DAYS_BETWEEN',
    label: '📅 Días entre dos Fechas',
    description: 'Calcula la diferencia en días entre Fecha A y Fecha B',
    requiredCols: 2,
    colLabel: ['Fecha Inicio (A)', 'Fecha Fin (B)'],
    resultType: 'INTEGER',
    defaultAlias: 'DIAS_TRANSCURRIDOS',
  },
  {
    value: 'DAY_OF_WEEK',
    label: '🗓️ Día de la Semana',
    description: 'Extrae el nombre del día (Monday, Tuesday...) de una columna de fecha',
    requiredCols: 1,
    colLabel: ['Columna Fecha'],
    resultType: 'VARCHAR',
    defaultAlias: 'DIA_SEMANA',
  },
  {
    value: 'MONTH_NAME',
    label: '📆 Nombre del Mes',
    description: 'Extrae el nombre del mes (January, February...) de una columna de fecha',
    requiredCols: 1,
    colLabel: ['Columna Fecha'],
    resultType: 'VARCHAR',
    defaultAlias: 'NOMBRE_MES',
  },
  {
    value: 'YEAR_EXTRACT',
    label: '📊 Año',
    description: 'Extrae el año como entero de una columna de fecha',
    requiredCols: 1,
    colLabel: ['Columna Fecha'],
    resultType: 'INTEGER',
    defaultAlias: 'AÑO',
  },
  {
    value: 'CONCAT_FIELDS',
    label: '🔗 Concatenar Campos',
    description: 'Une el contenido de dos o más columnas en un solo campo de texto',
    requiredCols: 2,
    colLabel: ['Columna A', 'Columna B'],
    resultType: 'VARCHAR',
    defaultAlias: 'CAMPO_CONCATENADO',
  },
] as const;

export const CALCULATED_FUNC_ICONS: Record<string, string> = {
  DAYS_BETWEEN: '📅',
  DAY_OF_WEEK: '🗓️',
  MONTH_NAME: '📆',
  YEAR_EXTRACT: '📊',
  CONCAT_FIELDS: '🔗',
};

export const COMBINE_OPERATIONS = [
  { value: 'SUM', label: '➕ Sumar (+)', numericOnly: true },
  { value: 'SUBTRACT', label: '➖ Restar (-)', numericOnly: true },
  { value: 'MULTIPLY', label: '✖️ Multiplicar (×)', numericOnly: true },
  { value: 'DIVIDE', label: '➗ Dividir (÷)', numericOnly: true },
  { value: 'CONCAT', label: '🔗 Concatenar (Texto)', numericOnly: false },
] as const;

export const COMBINE_OPERATION_SYMBOLS: Record<string, string> = {
  SUM: '+',
  SUBTRACT: '−',
  MULTIPLY: '×',
  DIVIDE: '÷',
  CONCAT: '||',
};
