<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'

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
    <div class="min-w-0">
      <div class="text-sm font-medium">{{ label }}</div>
      <div v-if="description" class="mt-1 text-xs text-muted-foreground">
        {{ description }}
      </div>
    </div>

    <button
      type="button"
      role="switch"
      :aria-checked="checked"
      :disabled="disabled"
      :class="
        cn(
          'relative inline-flex h-6 w-11 flex-none items-center rounded-full border transition-colors',
          disabled && 'cursor-not-allowed opacity-60',
          checked ? 'bg-primary' : 'bg-muted',
        )
      "
      @click="checked = !checked"
    >
      <span
        :class="
          cn(
            'inline-block size-5 translate-x-0 rounded-full bg-background shadow transition-transform',
            checked && 'translate-x-5',
          )
        "
      />
    </button>
  </div>
</template>


