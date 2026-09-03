import { useState, useEffect } from 'react';
import type { Project } from '../api/client';

export function useMedallionState() {
  const [activeTab, setActiveTab] = useState<'bronze' | 'silver' | 'gold'>('bronze');
  const [themeMode, setThemeMode] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    if (themeMode === 'light') {
      document.body.classList.add('theme-light');
    } else {
      document.body.classList.remove('theme-light');
    }
  }, [themeMode]);

  const toggleTheme = () => setThemeMode(prev => (prev === 'dark' ? 'light' : 'dark'));

  // Estados de Proyecto Activo
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState<boolean>(true);
  const [isCleaningModalOpen, setIsCleaningModalOpen] = useState<boolean>(false);
  const [isAtomicityModalOpen, setIsAtomicityModalOpen] = useState<boolean>(false);
  const [transformError, setTransformError] = useState<string | null>(null);

  // Estados de Filtros y Búsqueda
  const [bronzeSearch, setBronzeSearch] = useState<string>('');
  const [bronzeCol, setBronzeCol] = useState<string>('TODOS');
  const [bronzeLimit, setBronzeLimit] = useState<number>(50);
  const [bronzeExcelFilters, setBronzeExcelFilters] = useState<Record<string, string[]>>({});

  const [silverSearch, setSilverSearch] = useState<string>('');
  const [silverCol, setSilverCol] = useState<string>('TODOS');
  const [silverFilterStatus, setSilverFilterStatus] = useState<string>('TODOS');
  const [silverExcelFilters, setSilverExcelFilters] = useState<Record<string, string[]>>({});

  const [goldSearch, setGoldSearch] = useState<string>('');
  const [goldCol, setGoldCol] = useState<string>('TODOS');
  const [goldLedgerExcelFilters, setGoldLedgerExcelFilters] = useState<Record<string, string[]>>({});

  const [goldAccountSearch, setGoldAccountSearch] = useState<string>('');
  const [goldAccountCol, setGoldAccountCol] = useState<string>('TODOS');
  const [goldAccountExcelFilters, setGoldAccountExcelFilters] = useState<Record<string, string[]>>({});

  const handleApplyFilter = (setFiltersFn: React.Dispatch<React.SetStateAction<Record<string, string[]>>>) =>
    (colName: string, selectedVals: string[] | undefined) => {
      setFiltersFn((prev) => {
        const next = { ...prev };
        if (selectedVals && selectedVals.length > 0) {
          next[colName] = selectedVals;
        } else {
          delete next[colName];
        }
        return next;
      });
    };

  return {
    activeTab,
    setActiveTab,
    themeMode,
    toggleTheme,
    activeProject,
    setActiveProject,
    isProjectModalOpen,
    setIsProjectModalOpen,
    isCleaningModalOpen,
    setIsCleaningModalOpen,
    isAtomicityModalOpen,
    setIsAtomicityModalOpen,
    transformError,
    setTransformError,
    bronzeSearch,
    setBronzeSearch,
    bronzeCol,
    setBronzeCol,
    bronzeLimit,
    setBronzeLimit,
    bronzeExcelFilters,
    setBronzeExcelFilters,
    silverSearch,
    setSilverSearch,
    silverCol,
    setSilverCol,
    silverFilterStatus,
    setSilverFilterStatus,
    silverExcelFilters,
    setSilverExcelFilters,
    goldSearch,
    setGoldSearch,
    goldCol,
    setGoldCol,
    goldLedgerExcelFilters,
    setGoldLedgerExcelFilters,
    goldAccountSearch,
    setGoldAccountSearch,
    goldAccountCol,
    setGoldAccountCol,
    goldAccountExcelFilters,
    setGoldAccountExcelFilters,
    handleApplyFilter,
  };
}
