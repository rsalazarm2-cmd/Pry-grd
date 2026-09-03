<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card bg-slate-900 border border-slate-800 p-5 rounded-xl text-slate-100 w-96 space-y-4">
      <h3 class="text-sm font-bold text-slate-200">🗄️ Crear Vista Plata & Configurar Join</h3>
      
      <div>
        <label class="text-xs text-slate-400">Nombre de la Vista (para ORO):</label>
        <input v-model="name" type="text" placeholder="ej. PARTIDAS_DEBITO" class="w-full mt-1 p-2 bg-slate-950 border border-slate-800 rounded text-xs text-slate-200" />
      </div>

      <div>
        <label class="text-xs text-slate-400">Tipo de Relación / SQL Join:</label>
        <select v-model="joinType" class="w-full mt-1 p-2 bg-slate-950 border border-slate-800 rounded text-xs text-indigo-400 font-bold">
          <option value="INNER">🔗 INNER JOIN (Solo Coincidencias Exacatas)</option>
          <option value="LEFT">🔗 LEFT JOIN (Todas las Cabeceras + Detalle)</option>
          <option value="RIGHT">🔗 RIGHT JOIN (Todos los Detalles + Cabecera)</option>
          <option value="FULL">🔗 FULL OUTER JOIN (Matriz Completa NIIF)</option>
        </select>
      </div>

      <div>
        <label class="text-xs text-slate-400">Descripción / Subtítulo:</label>
        <input v-model="subtitle" type="text" placeholder="ej. Asientos con saldo a favor" class="w-full mt-1 p-2 bg-slate-950 border border-slate-800 rounded text-xs text-slate-200" />
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <button @click="$emit('close')" class="px-3 py-1.5 bg-slate-800 text-slate-400 rounded text-xs hover:bg-slate-700">Cancelar</button>
        <button @click="confirm" class="px-4 py-1.5 bg-indigo-600 text-white rounded text-xs font-bold hover:bg-indigo-500">Crear Vista con Join</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ show: boolean }>()
const emit = defineEmits(['close', 'create'])

const name = ref('')
const subtitle = ref('')
const joinType = ref<'INNER' | 'LEFT' | 'RIGHT' | 'FULL'>('LEFT')

function confirm() {
  if (!name.value.trim()) return
  emit('create', { name: name.value.trim().toUpperCase(), subtitle: subtitle.value.trim() || 'Vista Plata para Capa Oro', joinType: joinType.value })
  name.value = ''; subtitle.value = ''; joinType.value = 'LEFT'
}
</script>

<style scoped>
.modal-backdrop { position: absolute; inset: 0; background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center; z-index: 100; }
</style>
