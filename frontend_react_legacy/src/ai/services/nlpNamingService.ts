import { aiApi } from '../../shared/api/aiApi';

export class NlpNamingService {
  /**
   * Servicio de Infraestructura/IA especializado en consultar el modelo NLP
   * y asignar alias traducidos y limpios a las columnas seleccionadas.
   */
  static async applyNlpNamingSuggestions(
    sourceColumns: string[],
    updateColumnRule: (columnName: string, ruleKey: string, value: any) => void,
    targetLang: string = 'es'
  ): Promise<Record<string, string>> {
    if (!sourceColumns.length) return {};

    try {
      const suggestions = await aiApi.suggestMapping(sourceColumns, targetLang);
      
      Object.entries(suggestions).forEach(([origName, mappedName]) => {
        if (mappedName && mappedName.trim()) {
          updateColumnRule(origName, 'new_column_name', mappedName);
        }
      });

      return suggestions;
    } catch (error) {
      console.error('❌ Error al ejecutar el servicio de auto-nombrado NLP:', error);
      throw error;
    }
  }
}
