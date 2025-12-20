<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'

const props = defineProps<{
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'send', text: string): void
}>()

const text = ref('')

function onSend() {
  const trimmed = text.value.trim()
  if (!trimmed || props.disabled) return
  emit('send', trimmed)
  text.value = ''
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <textarea
      v-model="text"
      class="min-h-[88px] w-full resize-y rounded-md border bg-background px-3 py-2 text-sm"
      placeholder="Type a message…"
      :disabled="disabled"
      @keydown.enter.exact.prevent="onSend"
    />
    <div class="flex items-center justify-end gap-2">
      <Button type="button" :disabled="disabled" @click="onSend">Send</Button>
    </div>
  </div>
</template>


