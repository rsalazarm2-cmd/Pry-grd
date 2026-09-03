import React from 'react';
import { Database, ShieldCheck, BarChart3 } from 'lucide-react';

interface TabNavigationProps {
  activeTab: 'bronze' | 'silver' | 'gold';
  onTabChange: (tab: 'bronze' | 'silver' | 'gold') => void;
}

export const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
}) => {
  const tabs = [
    {
      id: 'bronze' as const,
      label: '1. Capa Bronce',
      sublabel: 'Crudo Inmutable & Ingesta',
      icon: Database,
      activeColor: 'var(--accent-amber)',
      activeBg: 'rgba(245, 158, 11, 0.12)',
    },
    {
      id: 'silver' as const,
      label: '2. Capa Plata',
      sublabel: 'Tipado, Limpieza & ENUMs',
      icon: ShieldCheck,
      activeColor: 'var(--accent-cyan)',
      activeBg: 'rgba(56, 189, 248, 0.12)',
    },
    {
      id: 'gold' as const,
      label: '3. Capa Oro',
      sublabel: 'Datamarts Libros & PyG',
      icon: BarChart3,
      activeColor: 'var(--accent-purple)',
      activeBg: 'rgba(168, 85, 247, 0.12)',
    },
  ];

  return (
    <div style={{ width: '100%', marginBottom: '1.5rem' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '0.75rem',
        width: '100%',
      }}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.85rem 1.25rem',
                borderRadius: '12px',
                border: isActive
                  ? `2px solid ${tab.activeColor}`
                  : '1px solid var(--border-glass)',
                backgroundColor: isActive ? tab.activeBg : 'var(--bg-input)',
                cursor: 'pointer',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                textAlign: 'left',
                boxShadow: isActive ? 'var(--card-shadow)' : 'none',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                <div style={{
                  padding: '0.55rem',
                  borderRadius: '10px',
                  backgroundColor: isActive ? tab.activeBg : 'rgba(148, 163, 184, 0.1)',
                  color: isActive ? tab.activeColor : 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Icon size={20} />
                </div>
                <div>
                  <div style={{
                    fontSize: '0.92rem',
                    fontWeight: 700,
                    color: isActive ? tab.activeColor : 'var(--text-main)',
                    lineHeight: '1.2',
                  }}>
                    {tab.label}
                  </div>
                  <div style={{
                    fontSize: '0.78rem',
                    color: 'var(--text-muted)',
                    fontWeight: 500,
                    marginTop: '0.15rem',
                  }}>
                    {tab.sublabel}
                  </div>
                </div>
              </div>

              {isActive && (
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: tab.activeColor,
                  boxShadow: `0 0 8px ${tab.activeColor}`,
                }} />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
