import React from 'react';
import { Layers, DollarSign, Calendar, Key, FileText } from 'lucide-react';
import type { ColumnProfile } from '../../api/types';
import { DOMAIN_OPTIONS, domainPredicates, type DomainCategoryFilter } from './domainFilters';

interface DomainFilterPillsProps {
  columns: ColumnProfile[];
  selectedDomain: DomainCategoryFilter;
  onSelectDomain: (domain: DomainCategoryFilter) => void;
}

export const DomainFilterPills: React.FC<DomainFilterPillsProps> = ({
  columns,
  selectedDomain,
  onSelectDomain,
}) => {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'DollarSign': return <DollarSign size={14} />;
      case 'Calendar': return <Calendar size={14} />;
      case 'Key': return <Key size={14} />;
      case 'FileText': return <FileText size={14} />;
      default: return <Layers size={14} />;
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      flexWrap: 'wrap',
    }}>
      {DOMAIN_OPTIONS.map((opt) => {
        const count = columns.filter(domainPredicates[opt.key]).length;
        const isActive = selectedDomain === opt.key;

        return (
          <button
            key={opt.key}
            onClick={() => onSelectDomain(opt.key)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.4rem 0.85rem',
              borderRadius: '20px',
              border: isActive ? '1px solid var(--accent-indigo)' : '1px solid var(--border-glass)',
              backgroundColor: isActive ? 'rgba(79, 70, 229, 0.15)' : 'var(--bg-input)',
              color: isActive ? 'var(--accent-indigo)' : 'var(--text-muted)',
              fontSize: '0.8rem',
              fontWeight: isActive ? 700 : 500,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {getIcon(opt.iconName)}
            <span>{opt.label}</span>
            <span style={{
              fontSize: '0.7rem',
              padding: '0.05rem 0.4rem',
              borderRadius: '10px',
              backgroundColor: isActive ? 'rgba(99, 102, 241, 0.25)' : 'rgba(148, 163, 184, 0.15)',
              color: isActive ? 'var(--accent-indigo)' : 'var(--text-muted)',
              fontWeight: 700,
            }}>
              {count}
            </span>
          </button>
        );
      })}
    </div>
  );
};
