import { projectApi } from '../../project/api/projectApi';
import { bronzeApi } from '../../bronze/api/bronzeApi';
import { silverApi } from '../../silver/api/silverApi';
import { goldApi } from '../../gold/api/goldApi';
import { aiApi } from './aiApi';

export * from './types';
export { projectApi } from '../../project/api/projectApi';
export { bronzeApi } from '../../bronze/api/bronzeApi';
export { silverApi } from '../../silver/api/silverApi';
export { goldApi } from '../../gold/api/goldApi';
export { aiApi } from './aiApi';

export const apiClient = {
  ...projectApi,
  ...bronzeApi,
  ...silverApi,
  ...goldApi,
  ...aiApi,
  // Alias de compatibilidad (los componentes usan estos nombres)
  profileBronze: bronzeApi.profile,
  profileSilver: silverApi.profile,
  getBronzeRecords: bronzeApi.getRecords,
  getSilverRecords: silverApi.getRecords,
  getGoldBalances: goldApi.getBalances,
  getGoldAccountBalances: goldApi.getAccountBalances,
  clearProjectData: projectApi.clearProjectData || (async (id: string) => { 
    const res = await fetch(`/api/projects/${id}/clear-data`, { method: 'POST' });
    return res.json();
  }),
  uploadCSV: bronzeApi.uploadCSV,
  transformSilver: silverApi.transform,
  getAtomicitySuggestions: silverApi.getAtomicitySuggestions,
  suggestMapping: aiApi.suggestMapping,
  getColumnDetail: bronzeApi.getColumnDetail, // or maybe silver? It's in bronze mostly
};
