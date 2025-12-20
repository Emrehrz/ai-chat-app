<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
import type { ChatMessage } from '@/lib/chat'

const props = defineProps<{ message: ChatMessage }>()

const isUser = computed(() => props.message.role === 'user')
const isAssistant = computed(() => props.message.role === 'assistant')
</script>

<template>
  <div :class="cn('flex', isUser ? 'justify-end' : 'justify-start')">
    <div
      :class="
        cn(
          'max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm leading-relaxed',
          isUser && 'bg-primary text-primary-foreground',
          isAssistant && 'bg-muted text-foreground',
          !isUser && !isAssistant && 'bg-card text-foreground border',
        )
      "
    >
      {{ message.content }}
    </div>
  </div>
</template>


