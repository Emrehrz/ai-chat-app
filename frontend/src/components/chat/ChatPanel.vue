<script setup lang="ts">
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import MessageList from '@/components/chat/MessageList.vue'
import MessageComposer from '@/components/chat/MessageComposer.vue'
import { useChat } from '@/lib/chat'

const chat = useChat()

const sessionLabel = computed(() => chat.sessionId.value ?? '(new session)')
</script>

<template>
  <section class="flex flex-col gap-4 rounded-lg border bg-card p-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-col">
        <div class="text-sm font-medium">Session</div>
        <div class="text-xs text-muted-foreground">
          {{ sessionLabel }}
        </div>
      </div>

      <div class="flex items-center gap-2">
        <Button type="button" variant="secondary" size="sm" :disabled="chat.isLoading.value" @click="chat.reset">
          New session
        </Button>
      </div>
    </div>

    <div class="rounded-md border bg-background p-3">
      <MessageList :messages="chat.messages.value" />
    </div>

    <div v-if="chat.toolCalls.value.length" class="rounded-md border bg-muted p-3">
      <div class="text-xs font-medium">Tool calls (debug)</div>
      <pre class="mt-2 overflow-auto text-xs">{{ chat.toolCalls.value }}</pre>
    </div>

    <div v-if="chat.lastError.value" class="rounded-md border border-destructive/40 bg-destructive/10 p-3">
      <div class="text-xs font-medium text-destructive">Error</div>
      <div class="mt-1 text-xs text-destructive">{{ chat.lastError.value }}</div>
    </div>

    <MessageComposer :disabled="!chat.canSend.value" @send="chat.send" />
  </section>
</template>


