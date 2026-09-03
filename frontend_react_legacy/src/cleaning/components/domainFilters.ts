import type { ColumnProfile } from '../../api/types';

export type DomainCategoryFilter = 'ALL' | 'MONETARY' | 'DATE' | 'ID' | 'TEXT';

export interface DomainOption {
  key: DomainCategoryFilter;
  label: string;
  iconName: 'Layers' | 'DollarSign' | 'Calendar' | 'Key' | 'FileText';
}

export const DOMAIN_OPTIONS: DomainOption[] = [
  { key: 'ALL', label: 'Todas las Columnas', iconName: 'Layers' },
  { key: 'MONETARY', label: 'Monetarias / Montos', iconName: 'DollarSign' },
  { key: 'DATE', label: 'Fechas y Períodos', iconName: 'Calendar' },
  { key: 'ID', label: 'Identificadores (IDs)', iconName: 'Key' },
  { key: 'TEXT', label: 'Texto / Descripciones', iconName: 'FileText' },
];

export const domainPredicates: Record<DomainCategoryFilter, (col: ColumnProfile) => boolean> = {
  ALL: () => true,
  MONETARY: (col) =>
    col.domain_category === 'MONETARY' ||
    ['ENTERED_DR', 'ENTERED_CR', 'ACCOUNTED_DR', 'ACCOUNTED_CR', 'DEBIT', 'CREDIT', 'AMOUNT', 'VALOR'].some((k) =>
      col.column_name.toUpperCase().includes(k)
    ),
  DATE: (col) =>
    col.domain_category === 'DATE' ||
    ['DATE', 'PERIOD', 'CREATION', 'POSTED'].some((k) => col.column_name.toUpperCase().includes(k)),
  ID: (col) =>
    col.column_name.toUpperCase().includes('ID') || col.column_name.toUpperCase().includes('CODE'),
  TEXT: (col) =>
    ['VARCHAR', 'ENUM', 'CHAR', 'TEXT'].includes((col.data_type || '').toUpperCase()) ||
    col.domain_category === 'GENERAL_ATTRIBUTE',
};
