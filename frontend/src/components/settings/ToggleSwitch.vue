<script setup lang="ts">
import { computed } from 'vue'
import { Switch } from '@/components/ui/switch'

const props = defineProps<{
  modelValue: boolean
  label: string
  description?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
}>()

const checked = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v),
})
</script>

<template>
  <div class="flex items-start justify-between gap-4">
    <div class="min-w-0 flex-1">
      <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        {{ label }}
      </label>
      <p v-if="description" class="mt-1 text-xs text-muted-foreground">
        {{ description }}
      </p>
    </div>

    <Switch :checked="checked" @update:checked="(v: boolean) => (checked = v)" :disabled="disabled" />
  </div>
</template>
