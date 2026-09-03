import { useState } from 'react';
import { useMedallionStore } from '../../shared/store/medallionStore';
import { useMedallionQueries } from '../../shared/hooks/useMedallionQueries';

export const useSilverWorkspaceController = () => {
  const [showConfig, setShowConfig] = useState(false);
  const [showLineage, setShowLineage] = useState(false);
  const [showSemanticMapping, setShowSemanticMapping] = useState(false);
  const [showDimensions, setShowDimensions] = useState(false);

  const state = useMedallionStore();
  const {
    silverProfile: profile,
    silverRecords,
    silverLoading,
    transformMutation,
  } = useMedallionQueries();

  const isProcessing = transformMutation.isPending;
  const isGeneratingGold = false;

  const handleProcessSilver = async () => {
    try {
      await transformMutation.mutateAsync({
        split_rules: state.splitRules,
        combine_rules: state.combineRules.filter((r) => r.enabled),
        calculated_field_rules: state.calculatedFieldRules.filter((r) => r.enabled),
        semantic_mapping: state.semanticMapping,
      });
    } catch (err) {
      console.error(err);
    }
  };

  const toggleValueTools = () => {
    setShowConfig((prev) => !prev);
    setTimeout(() => {
      document.getElementById('config-panel-silver')?.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  return {
    showConfig,
    setShowConfig,
    showLineage,
    setShowLineage,
    showSemanticMapping,
    setShowSemanticMapping,
    showDimensions,
    setShowDimensions,
    profile,
    silverRecords,
    silverLoading,
    isProcessing,
    isGeneratingGold,
    state,
    handleProcessSilver,
    toggleValueTools,
  };
};
