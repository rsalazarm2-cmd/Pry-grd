import { useQuery } from '@tanstack/react-query';

export interface AlertaDescuadreDTO {
  FOLIO_ASIENTO: string;
  LIBRO_CONTABLE: string;
  PERIODO_CONTABLE: string;
  TOTAL_CARGOS_CALCULADO: number;
  TOTAL_ABONOS_CALCULADO: number;
  TOTAL_CARGOS_CABECERA: number;
  DIFERENCIA_DESCUADRE: number;
  TIPO_ALERTA: string;
}

export interface SegregacionFuncionesDTO {
  FOLIO_ASIENTO: string;
  USUARIO_REGISTRADOR: string;
  USUARIO_APROBADOR: string;
  FECHA_REGISTRO: string;
  MONTO_TOTAL_ASIENTO: number;
  NIVEL_RIESGO: string;
}

export interface InformeIntegridadAuditoriaDTO {
  total_asientos_analizados: number;
  total_descuadres_detectados: number;
  total_violaciones_sod: number;
  monto_total_descuadrado: number;
  alertas_descuadre: AlertaDescuadreDTO[];
  alertas_sod: SegregacionFuncionesDTO[];
}

const API_BASE_URL = 'http://localhost:8000/api/audit';

export const useAuditIntegrity = (parquetPath: string) => {
  const reportQuery = useQuery<InformeIntegridadAuditoriaDTO>({
    queryKey: ['auditReport', parquetPath],
    queryFn: async () => {
      if (!parquetPath) throw new Error('Ruta de archivo Parquet no especificada');
      const res = await fetch(`${API_BASE_URL}/report?parquet_path=${encodeURIComponent(parquetPath)}`);
      if (!res.ok) throw new Error('Error al cargar informe de auditoría');
      return res.json();
    },
    enabled: Boolean(parquetPath),
  });

  return {
    report: reportQuery.data,
    isLoading: reportQuery.isLoading,
    isError: reportQuery.isError,
    error: reportQuery.error,
    refetch: reportQuery.refetch,
  };
};
