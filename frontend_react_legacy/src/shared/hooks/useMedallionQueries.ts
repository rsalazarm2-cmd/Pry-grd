import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useMedallionStore } from '../store/medallionStore';

export function useMedallionQueries() {
  const queryClient = useQueryClient();
  const state = useMedallionStore();

  const { data: profile, refetch: refetchProfile } = useQuery({
    queryKey: ['profile', state.activeProject?.id],
    queryFn: () => apiClient.profileBronze(state.activeProject?.id),
    enabled: !!state.activeProject?.id,
  });

  const { data: silverProfile, refetch: refetchSilverProfile } = useQuery({
    queryKey: ['silverProfile', state.activeProject?.id],
    queryFn: () => apiClient.profileSilver(state.activeProject?.id),
    enabled: !!state.activeProject?.id,
  });

  const { data: bronzeRecords, isLoading: bronzeLoading } = useQuery({
    queryKey: ['bronzeRecords', state.activeProject?.id, state.bronzeLimit, state.bronzeSearch, state.bronzeCol, JSON.stringify(state.bronzeExcelFilters)],
    queryFn: () => apiClient.getBronzeRecords(state.activeProject?.id, state.bronzeLimit, state.bronzeSearch, state.bronzeCol, Object.keys(state.bronzeExcelFilters).length > 0 ? JSON.stringify(state.bronzeExcelFilters) : undefined),
    enabled: !!state.activeProject?.id,
  });

  const { data: silverRecords, isLoading: silverLoading, refetch: refetchSilver } = useQuery({
    queryKey: ['silverRecords', state.activeProject?.id, state.silverFilterStatus, state.silverSearch, state.silverCol, JSON.stringify(state.silverExcelFilters)],
    queryFn: () => apiClient.getSilverRecords(state.activeProject?.id, state.silverFilterStatus, state.silverSearch, state.silverCol, Object.keys(state.silverExcelFilters).length > 0 ? JSON.stringify(state.silverExcelFilters) : undefined),
    enabled: !!state.activeProject?.id,
  });

  const { data: goldBalances, isLoading: goldLoading } = useQuery({
    queryKey: ['goldBalances', state.activeProject?.id, state.goldSearch, state.goldCol, JSON.stringify(state.goldLedgerExcelFilters)],
    queryFn: () => apiClient.getGoldBalances(state.activeProject?.id, state.goldSearch, state.goldCol, Object.keys(state.goldLedgerExcelFilters).length > 0 ? JSON.stringify(state.goldLedgerExcelFilters) : undefined),
    enabled: !!state.activeProject?.id,
  });

  const { data: goldAccountBalances, isLoading: goldAccountLoading } = useQuery({
    queryKey: ['goldAccountBalances', state.activeProject?.id, state.goldAccountSearch, state.goldAccountCol, JSON.stringify(state.goldAccountExcelFilters)],
    queryFn: () => apiClient.getGoldAccountBalances(state.activeProject?.id, state.goldAccountSearch, state.goldAccountCol, Object.keys(state.goldAccountExcelFilters).length > 0 ? JSON.stringify(state.goldAccountExcelFilters) : undefined),
    enabled: !!state.activeProject?.id,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => apiClient.uploadCSV(file, state.activeProject?.id),
    onSuccess: () => {
      refetchProfile();
      refetchSilverProfile();
      queryClient.invalidateQueries({ queryKey: ['bronzeRecords', state.activeProject?.id] });
      queryClient.invalidateQueries({ queryKey: ['silverRecords', state.activeProject?.id] });
      queryClient.invalidateQueries({ queryKey: ['goldBalances', state.activeProject?.id] });
    },
  });

  const transformMutation = useMutation({
    mutationFn: (payload: any) =>
      apiClient.transformSilver(payload, state.activeProject?.id),
    onSuccess: () => {
      refetchSilver();
      refetchSilverProfile();
      state.setActiveTab('silver');
    },
  });

  const clearDataMutation = useMutation({
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      queryClient.invalidateQueries({ queryKey: ['silverProfile'] });
      queryClient.invalidateQueries({ queryKey: ['bronzeRecords'] });
      queryClient.invalidateQueries({ queryKey: ['silverRecords'] });
      queryClient.invalidateQueries({ queryKey: ['goldBalances'] });
    },
    onError: (err: Error) => {
      alert(`Error al limpiar datos: ${err.message}`);
    }
  });

  return {
    profile,
    refetchProfile,
    silverProfile,
    refetchSilverProfile,
    bronzeRecords,
    bronzeLoading,
    silverRecords,
    silverLoading,
    refetchSilver,
    goldBalances,
    goldLoading,
    goldAccountBalances,
    goldAccountLoading,
    uploadMutation,
    transformMutation,
    clearDataMutation,
  };
}
