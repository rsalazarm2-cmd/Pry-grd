<script setup lang="ts">
/**
 * CU-09: Constructor de Reglas Condicionales IF-THEN-ELSE con Árbol AST (No-Code).
 * CU-10: Inspector y Previsualización de Esqueleto (Schema Blueprint Preview).
 * Solución a Imperfección 5: Soporte para sub-grupos anidados ((A AND B) OR C).
 */
import { ref, onMounted } from 'vue'
import type { ConditionalRuleDTO, RuleConditionDTO, RuleGroupDTO, RuleEvaluationResultDTO } from '@/types/silver'
import { evaluateConditionalRule } from '@/api/silver_api'
import { apiGet } from '@/api/http_client'

const ruleName = ref('REGLA_RIESGO_FINANCIERO')
const resultCol = ref('CATEGORIA_RIESGO')
const thenVal = ref('RIESGO_CRITICO')
const elseVal = ref('NORMAL')
const availableColumns = ref<string[]>([])

const rootGroup = ref<RuleGroupDTO>({
  logical_operator: 'OR',
  conditions: [{ column_name: 'CARGO_MONEDA_FUNCIONAL', operator: 'GT', value: 100000 }],
  sub_groups: [
    {
      logical_operator: 'AND',
      conditions: [
        { column_name: 'ORIGEN_ASIENTO', operator: 'EQ', value: 'MANUAL' },
        { column_name: 'IS_WEEKEND', operator: 'IS_WEEKEND', value: '' },
      ],
      sub_groups: [],
    },
  ],
})

const isEvaluating = ref(false)
const previewResult = ref<RuleEvaluationResultDTO | null>(null)
const error = ref<string | null>(null)

async function loadColumns() {
  try {
    const prof = await apiGet<any>('/silver/profile')
    if (prof && prof.columns) {
      availableColumns.value = prof.columns.map((c: any) => typeof c === 'string' ? c : (c.column_name || c.name || ''))
    }
  } catch (err) {
    console.error('Error cargando columnas:', err)
  }
}

onMounted(loadColumns)

function addCondition(group: RuleGroupDTO) { group.conditions.push({ column_name: availableColumns.value[0] || 'ORIGEN_ASIENTO', operator: 'EQ', value: 'MANUAL' }) }
function addSubGroup(group: RuleGroupDTO) { group.sub_groups.push({ logical_operator: 'AND', conditions: [{ column_name: availableColumns.value[0] || 'CARGO_MONEDA_FUNCIONAL', operator: 'GT', value: 50000 }], sub_groups: [] }) }
function removeCondition(group: RuleGroupDTO, idx: number) { group.conditions.splice(idx, 1) }
function removeSubGroup(group: RuleGroupDTO, idx: number) { group.sub_groups.splice(idx, 1) }

async function handleEvaluate() {
  isEvaluating.value = true
  error.value = null
  previewResult.value = null

  const payload: ConditionalRuleDTO = {
    rule_name: ruleName.value,
    root_group: rootGroup.value,
    then_result_column: resultCol.value,
    then_value: thenVal.value,
    else_value: elseVal.value,
  }

  try {
    previewResult.value = await evaluateConditionalRule(payload)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Error evaluando regla'
  } finally {
    isEvaluating.value = false
  }
}
</script>

<template>
  <div class="rule-builder glass-card">
    <div class="builder-header">
      <div>
        <h3 class="builder-title">⚡ Constructor de Reglas Condicionales AST (No-Code)</h3>
        <p class="builder-subtitle">Soporte para grupos anidados con paréntesis ((A AND B) OR C)</p>
      </div>
      <button class="btn-eval" :disabled="isEvaluating" @click="handleEvaluate">
        {{ isEvaluating ? 'Evaluando...' : '🔍 Probar Regla (Preview SQL)' }}
      </button>
    </div>

    <!-- Form Config -->
    <div class="config-grid">
      <div class="field"><label>Nombre de Regla:</label><input v-model="ruleName" type="text" class="input-text"></div>
      <div class="field"><label>Columna Destino:</label><input v-model="resultCol" type="text" class="input-text"></div>
      <div class="field"><label>Valor SI Cumple (THEN):</label><input v-model="thenVal" type="text" class="input-text"></div>
      <div class="field"><label>Valor SINO (ELSE):</label><input v-model="elseVal" type="text" class="input-text"></div>
    </div>

    <!-- Root AST Group -->
    <div class="ast-root-group">
      <div class="group-header">
        <span class="group-label">Nodo Raíz (IF):</span>
        <select v-model="rootGroup.logical_operator" class="select-op">
          <option value="OR">Cumplir CUALQUIER Grupo (OR)</option>
          <option value="AND">Cumplir TODOS los Grupos (AND)</option>
        </select>
        <button class="btn-add" @click="addCondition(rootGroup)">+ Agregar Condición</button>
        <button class="btn-add-sub" @click="addSubGroup(rootGroup)">+ Agregar Sub-Grupo (Paréntesis)</button>
      </div>

      <!-- Root Conditions -->
      <div v-for="(cond, idx) in rootGroup.conditions" :key="`c-${idx}`" class="cond-row">
        <select v-model="cond.column_name" class="select-cond select-column">
          <option v-for="col in availableColumns" :key="col" :value="col">{{ col }}</option>
        </select>
        <select v-model="cond.operator" class="select-cond">
          <option value="GT">Mayor que (&gt;)</option>
          <option value="GTE">Mayor o igual (&ge;)</option>
          <option value="LT">Menor que (&lt;)</option>
          <option value="LTE">Menor o igual (&le;)</option>
          <option value="EQ">Igual a (==)</option>
          <option value="NEQ">Diferente de (!=)</option>
          <option value="IS_NULL">Es Nulo / Vacío</option>
          <option value="IS_WEEKEND">📅 Fin de Semana</option>
        </select>
        <input v-if="!['IS_NULL', 'IS_WEEKEND'].includes(cond.operator)" v-model="cond.value" type="text" placeholder="Valor" class="input-cond">
        <button class="btn-del" @click="removeCondition(rootGroup, idx)">✕</button>
      </div>

      <!-- Nested Sub-Groups (Paréntesis) -->
      <div v-for="(sub, sIdx) in rootGroup.sub_groups" :key="`s-${sIdx}`" class="nested-group">
        <div class="group-header">
          <span class="paren-badge">( Sub-Grupo #{{ sIdx + 1 }} )</span>
          <select v-model="sub.logical_operator" class="select-op">
            <option value="AND">AND (Todas)</option>
            <option value="OR">OR (Al menos una)</option>
          </select>
          <button class="btn-add" @click="addCondition(sub)">+ Condición</button>
          <button class="btn-del" @click="removeSubGroup(rootGroup, sIdx)">Eliminar Paréntesis</button>
        </div>

        <div v-for="(sCond, scIdx) in sub.conditions" :key="`sc-${scIdx}`" class="cond-row">
          <select v-model="sCond.column_name" class="select-cond select-column">
            <option v-for="col in availableColumns" :key="col" :value="col">{{ col }}</option>
          </select>
          <select v-model="sCond.operator" class="select-cond">
            <option value="GT">Mayor que (&gt;)</option>
            <option value="EQ">Igual a (==)</option>
            <option value="IS_NULL">Es Nulo</option>
            <option value="IS_WEEKEND">📅 Fin de Semana</option>
          </select>
          <input v-if="!['IS_NULL', 'IS_WEEKEND'].includes(sCond.operator)" v-model="sCond.value" type="text" placeholder="Valor" class="input-cond">
          <button class="btn-del" @click="removeCondition(sub, scIdx)">✕</button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <!-- CU-10 Schema Blueprint Preview -->
    <div v-if="previewResult" class="preview-result">
      <div class="preview-metrics">
        <div class="metric-box"><span class="m-val">{{ previewResult.matches_count }}</span><span class="m-lbl">Asientos Coincidentes</span></div>
        <div class="metric-box"><span class="m-val">{{ previewResult.matches_percentage }}%</span><span class="m-lbl">% del Total ({{ previewResult.total_rows }})</span></div>
      </div>
      <div class="sql-box"><code>{{ previewResult.sql_expression }}</code></div>
    </div>
  </div>
</template>

<style scoped>
.rule-builder { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.builder-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); pb: 0.5rem; }
.builder-title { font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin: 0; } .builder-subtitle { font-size: 0.75rem; color: #94a3b8; margin-top: 0.1rem; }
.btn-eval { background: linear-gradient(135deg, #10b981, #059669); color: #fff; font-weight: 600; padding: 0.45rem 1rem; border-radius: 6px; border: none; cursor: pointer; }
.config-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; } .field label { font-size: 0.75rem; color: #94a3b8; font-weight: 600; }
.input-text, .input-cond, .select-op, .select-cond { background: #090d16; border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 0.35rem 0.5rem; border-radius: 4px; font-size: 0.85rem; }
select option { background-color: #090d16; color: #f8fafc; }
.ast-root-group { display: flex; flex-direction: column; gap: 0.75rem; background: rgba(0,0,0,0.3); padding: 0.85rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); }
.nested-group { margin-left: 1.25rem; border-left: 3px solid #6366f1; padding-left: 0.75rem; display: flex; flex-direction: column; gap: 0.5rem; background: rgba(99, 102, 241, 0.05); padding: 0.6rem; border-radius: 4px; }
.group-header { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; flex-wrap: wrap; } .paren-badge { font-weight: 800; color: #818cf8; font-size: 0.8rem; }
.btn-add { background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; color: #60a5fa; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; }
.btn-add-sub { background: rgba(99, 102, 241, 0.2); border: 1px solid #6366f1; color: #a5b4fc; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; font-weight: 700; }
.cond-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; } .select-column { flex: 2; min-width: 160px; } .select-cond { flex: 1.5; min-width: 140px; } .input-cond { flex: 1.5; min-width: 110px; }
.btn-del { background: rgba(239, 68, 68, 0.2); color: #f87171; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.75rem; }
.preview-result { display: flex; flex-direction: column; gap: 0.5rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 6px; }
.preview-metrics { display: flex; gap: 1.5rem; } .metric-box { display: flex; flex-direction: column; } .m-val { font-size: 1.2rem; font-weight: 700; color: #34d399; } .m-lbl { font-size: 0.75rem; color: #94a3b8; }
.sql-box { background: rgba(0,0,0,0.5); padding: 0.5rem; border-radius: 4px; font-family: monospace; font-size: 0.8rem; color: #f59e0b; overflow-x: auto; }
.alert-error { padding: 0.5rem; background: rgba(239, 68, 68, 0.1); color: #f87171; border-radius: 4px; font-size: 0.85rem; }
</style>
