export function inferSilverTypeFromColumn(col: {
  column_name: string;
  data_type?: string;
  sample_values?: string[];
}): string {
  const nameUpper = col.column_name.toUpperCase().trim();
  const rawTypeUpper = (col.data_type || '').toUpperCase().trim();

  // 1. Si el tipo de datos ya es un tipo específico numérico o de fecha en DuckDB
  if (
    rawTypeUpper &&
    rawTypeUpper !== 'VARCHAR' &&
    rawTypeUpper !== 'STRING' &&
    rawTypeUpper !== 'TEXT'
  ) {
    if (
      rawTypeUpper.includes('DOUBLE') ||
      rawTypeUpper.includes('FLOAT') ||
      rawTypeUpper.includes('DECIMAL') ||
      rawTypeUpper.includes('NUMERIC')
    ) {
      return 'DOUBLE';
    }
    if (rawTypeUpper.includes('BIGINT') || rawTypeUpper.includes('HUGEINT')) {
      return 'BIGINT';
    }
    if (rawTypeUpper.includes('INT')) {
      return 'INTEGER';
    }
    if (rawTypeUpper.includes('TIMESTAMP') || rawTypeUpper.includes('DATETIME')) {
      return 'TIMESTAMP';
    }
    if (rawTypeUpper.includes('DATE')) {
      return 'DATE';
    }
    if (rawTypeUpper.includes('BOOL')) {
      return 'BOOLEAN';
    }
  }

  // 2. Heurística avanzada por nombre de columna contables/financieros
  if (
    [
      'ENTERED_DR',
      'ENTERED_CR',
      'ACCOUNTED_DR',
      'ACCOUNTED_CR',
      'DEBIT',
      'CREDIT',
      'AMOUNT',
      'VALOR',
      'SALDO',
      'MONTO',
      'TOTAL',
      'PRICE',
      'TAX',
      'BALANCE',
    ].some((k) => nameUpper === k || nameUpper.endsWith(`_${k}`) || nameUpper.startsWith(`${k}_`))
  ) {
    return 'DOUBLE';
  }

  if (
    [
      'DATE',
      'PERIOD',
      'CREATION_DATE',
      'POSTED_DATE',
      'GL_DATE',
      'EFFECTIVE_DATE',
      'FECHA',
    ].some((k) => nameUpper.includes(k))
  ) {
    return 'DATE';
  }

  if (
    [
      'ID',
      'HEADER_ID',
      'LINE_NUM',
      'BATCH_ID',
      'SEQUENCE_NUM',
      'CODE_COMBINATION_ID',
      'LEDGER_ID',
    ].some((k) => nameUpper.includes(k) || nameUpper.endsWith('_ID'))
  ) {
    return 'BIGINT';
  }

  // 3. Inspección por valores de muestra reales de la columna
  if (col.sample_values && col.sample_values.length > 0) {
    const validSamples = col.sample_values.filter((s) => s && s.trim() !== '');
    if (validSamples.length > 0) {
      const isAllDecimal = validSamples.every((s) => /^-?\d+[\.,]\d+$/.test(s.trim()));
      if (isAllDecimal) return 'DOUBLE';

      const isAllInteger = validSamples.every((s) => /^-?\d+$/.test(s.trim()));
      if (isAllInteger) {
        return nameUpper.includes('ID') || validSamples.some((s) => s.length > 9)
          ? 'BIGINT'
          : 'INTEGER';
      }

      const isAllDate = validSamples.every(
        (s) =>
          /^\d{4}[-\/]\d{2}[-\/]\d{2}/.test(s.trim()) ||
          /^\d{2}[-\/]\d{2}[-\/]\d{4}/.test(s.trim())
      );
      if (isAllDate) return 'DATE';
    }
  }

  return 'VARCHAR';
}

export function mapBronzeTypeToSilverType(bronzeType?: string): string {
  return inferSilverTypeFromColumn({ column_name: '', data_type: bronzeType });
}
