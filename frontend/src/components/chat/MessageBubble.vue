<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'
import type { UiChatMessage } from '@/lib/chat'
import AttachmentChips from '@/components/chat/AttachmentChips.vue'

const props = defineProps<{ message: UiChatMessage; typing?: boolean }>()

const isUser = computed(() => props.message.role === 'user')
const isAssistant = computed(() => props.message.role === 'assistant')
</script>

<template>
  <div :class="cn('flex flex-col gap-2', isUser ? 'items-end' : 'items-start')">
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
      <template v-if="typing">
        <div class="flex items-center gap-1 py-1">
          <span class="inline-block size-2 rounded-full bg-foreground/60 animate-bounce" style="animation-delay: 0ms" />
          <span class="inline-block size-2 rounded-full bg-foreground/60 animate-bounce" style="animation-delay: 120ms" />
          <span class="inline-block size-2 rounded-full bg-foreground/60 animate-bounce" style="animation-delay: 240ms" />
        </div>
      </template>
      <template v-else>
        {{ message.content }}
      </template>
    </div>

    <AttachmentChips v-if="message.attachments?.length" :attachments="message.attachments" />
  </div>
</template>
