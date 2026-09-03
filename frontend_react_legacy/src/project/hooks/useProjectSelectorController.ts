import { useState, useEffect } from 'react';
import { apiClient } from '../../shared/api/client';
import type { Project } from '../../shared/api/client';

export const useProjectSelectorController = (
  isOpen: boolean,
  activeProject: Project | null,
  onSelectProject: (project: Project | null) => void,
  onClose: () => void
) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newDomain, setNewDomain] = useState('GENERAL_LEDGER');

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getProjects();
      setProjects(data);
      if (data.length === 0) {
        setShowCreateForm(true);
      }
    } catch (err) {
      console.error('Error cargando proyectos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadProjects();
    }
  }, [isOpen]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    try {
      const created = await apiClient.createProject({
        name: newName.trim(),
        description: newDesc.trim(),
        domain: newDomain,
      });

      setNewName('');
      setNewDesc('');
      setShowCreateForm(false);
      await loadProjects();
      onSelectProject(created);
    } catch (err: any) {
      alert(err?.message || 'Error creando proyecto.');
    }
  };

  const handleDelete = async (e: React.MouseEvent, projectId: string) => {
    e.stopPropagation();
    if (!confirm(`¿Estás seguro de eliminar el proyecto "${projectId}" y todos sus datos Medallion?`)) return;

    try {
      await apiClient.deleteProject(projectId);
      if (activeProject?.id === projectId) {
        onSelectProject(null);
      }
      await loadProjects();
    } catch (err: any) {
      console.error('Error al eliminar proyecto:', err);
      alert(err?.message || 'Error eliminando proyecto.');
    }
  };

  return {
    projects,
    loading,
    showCreateForm,
    setShowCreateForm,
    newName,
    setNewName,
    newDesc,
    setNewDesc,
    newDomain,
    setNewDomain,
    handleCreate,
    handleDelete,
  };
};
