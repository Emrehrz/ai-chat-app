<script setup lang="ts">
import type { ChatMessage } from '@/lib/chat'
import MessageBubble from '@/components/chat/MessageBubble.vue'

defineProps<{
  messages: ChatMessage[]
}>()
</script>

<template>
  <div class="flex flex-col gap-3">
    <MessageBubble v-for="(m, idx) in messages" :key="idx" :message="m" />
  </div>
</template>


