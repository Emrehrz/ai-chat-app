<script setup lang="ts">
import type { ChatMessage } from '@/lib/chat'
import MessageBubble from '@/components/chat/MessageBubble.vue'

defineProps<{
  messages: ChatMessage[]
  isLoading?: boolean
}>()
</script>

<template>
  <div class="flex flex-col gap-3">
    <div v-for="(m, idx) in messages" :key="idx" class="scroll-mt-4"
      :data-chat-last="idx === messages.length - 1 ? 'true' : undefined">
      <MessageBubble :message="m" />
    </div>

    <div v-if="isLoading" class="scroll-mt-4" data-chat-last="true">
      <MessageBubble :message="{ role: 'assistant', content: '' }" typing />
    </div>
  </div>
</template>
