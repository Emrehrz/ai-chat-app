<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

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
    <div class="flex items-start gap-2 rounded-md border bg-background p-2">
      <slot name="prepend" />
      <div class="min-w-0 flex-1">
        <slot name="attachments" />
        <Textarea v-model="text" class="min-h-22 w-full resize-y border-0 p-0 shadow-none focus-visible:ring-0"
          placeholder="Type a message…" :disabled="disabled" @keydown.enter.exact.prevent="onSend" />
      </div>
      <div class="flex items-end gap-2">
        <slot name="actions" />
        <Button type="button" size="sm" :disabled="disabled" @click="onSend">Send</Button>
      </div>
    </div>
  </div>
</template>
