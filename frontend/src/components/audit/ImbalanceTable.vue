<script setup lang="ts">
/**
 * Tabla de alertas de descuadre de partida doble.
 * Muestra asientos donde Cargos ≠ Abonos.
 */
import { CheckCircle, AlertTriangle } from '@lucide/vue'
import type { AlertaDescuadreDTO } from '@/types/audit'

defineProps<{
  alertas: AlertaDescuadreDTO[]
}>()
</script>

<template>
  <div class="imbalance-section">
    <h4 class="section-title">
      <AlertTriangle :size="18" /> Asientos Descuadrados Detectados
    </h4>

    <div v-if="alertas.length === 0" class="all-clear">
      <CheckCircle :size="16" />
      100% de la muestra cumple la integridad de partida doble.
    </div>

    <div v-else class="table-wrapper">
      <table class="medallion-table">
        <thead>
          <tr>
            <th>FOLIO_ASIENTO</th>
            <th>PERIODO</th>
            <th>CARGOS (DEBE)</th>
            <th>ABONOS (HABER)</th>
            <th>DIFERENCIA</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(d, idx) in alertas" :key="idx">
            <td class="bold">{{ d.FOLIO_ASIENTO }}</td>
            <td>{{ d.PERIODO_CONTABLE }}</td>
            <td>${{ Number(d.TOTAL_CARGOS_CALCULADO).toLocaleString() }}</td>
            <td>${{ Number(d.TOTAL_ABONOS_CALCULADO).toLocaleString() }}</td>
            <td class="danger bold">${{ Number(d.DIFERENCIA_DESCUADRE).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--accent-amber);
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.all-clear {
  padding: 0.75rem;
  color: var(--accent-emerald);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.table-wrapper { overflow-x: auto; }
.bold { font-weight: 700; }
.danger { color: var(--accent-rose); }
</style>
