<script setup lang="ts">
/**
 * KPIs de Auditoría Forense.
 * Muestra métricas clave: asientos analizados, descuadres, violaciones SoD.
 */
import type { InformeIntegridadAuditoriaDTO } from '@/types/audit'
import KpiCard from '@/components/layout/KpiCard.vue'

defineProps<{
  report: InformeIntegridadAuditoriaDTO
}>()
</script>

<template>
  <div class="audit-kpis">
    <KpiCard
      :value="report.total_asientos_analizados"
      label="Asientos Analizados"
      accent-color="var(--accent-cyan)"
    />
    <KpiCard
      :value="report.total_descuadres_detectados"
      label="Descuadres Partida Doble"
      accent-color="var(--accent-amber)"
    />
    <KpiCard
      :value="report.total_violaciones_sod"
      label="Violaciones SoD"
      accent-color="var(--accent-rose)"
    />
    <KpiCard
      :value="`$${report.monto_total_descuadrado.toLocaleString()}`"
      label="Monto Descuadrado"
      accent-color="var(--accent-purple)"
    />
  </div>
</template>

<style scoped>
.audit-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
}
</style>
