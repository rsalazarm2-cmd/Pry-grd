<script setup lang="ts">
/**
 * Tabla de violaciones de Segregación de Funciones (Maker == Checker).
 * Detecta cuando el usuario que registra es el mismo que aprueba.
 */
import { CheckCircle, ShieldAlert } from '@lucide/vue'
import type { SegregacionFuncionesDTO } from '@/types/audit'

defineProps<{
  alertas: SegregacionFuncionesDTO[]
}>()
</script>

<template>
  <div class="sod-section">
    <h4 class="section-title">
      <ShieldAlert :size="18" /> Violaciones de Segregación de Funciones (Maker == Checker)
    </h4>

    <div v-if="alertas.length === 0" class="all-clear">
      <CheckCircle :size="16" />
      Ningún usuario registró y aprobó el mismo asiento contable.
    </div>

    <div v-else class="table-wrapper">
      <table class="medallion-table">
        <thead>
          <tr>
            <th>FOLIO_ASIENTO</th>
            <th>REGISTRADOR (MAKER)</th>
            <th>APROBADOR (CHECKER)</th>
            <th>MONTO TOTAL</th>
            <th>RIESGO</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(s, idx) in alertas" :key="idx">
            <td class="bold">{{ s.FOLIO_ASIENTO }}</td>
            <td class="danger">{{ s.USUARIO_REGISTRADOR }}</td>
            <td class="danger">{{ s.USUARIO_APROBADOR }}</td>
            <td>${{ Number(s.MONTO_TOTAL_ASIENTO).toLocaleString() }}</td>
            <td><span class="risk-badge">{{ s.NIVEL_RIESGO }}</span></td>
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
  color: var(--accent-rose);
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

.risk-badge {
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  background-color: rgba(239, 68, 68, 0.2);
  color: var(--accent-rose);
  font-weight: 700;
  font-size: 0.78rem;
}
</style>
