<script setup lang="ts">
/**
 * Card KPI genérica reutilizable.
 * Muestra un valor numérico con etiqueta y color de acento configurable.
 */

defineProps<{
  value: string | number
  label: string
  accentColor?: string
}>()
</script>

<template>
  <div class="kpi-card" :style="{ '--kpi-accent': accentColor ?? 'var(--accent-cyan)' }">
    <span class="kpi-value">{{ typeof value === 'number' ? value.toLocaleString() : value }}</span>
    <span class="kpi-label">{{ label }}</span>
  </div>
</template>

<style scoped>
.kpi-card {
  padding: 1rem;
  border-radius: 12px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-glass);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: var(--kpi-accent);
}

.kpi-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--kpi-accent);
  line-height: 1;
}

.kpi-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  text-align: center;
  letter-spacing: 0.02em;
}
</style>
