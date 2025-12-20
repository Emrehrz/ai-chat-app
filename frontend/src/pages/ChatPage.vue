<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
import ChatPanel from '@/components/chat/ChatPanel.vue'
</script>

<template>
  <AppShell>
    <div class="flex flex-col gap-4">
      <div>
        <h1 class="text-lg font-semibold">Chat</h1>
        <p class="text-sm text-muted-foreground">
          Tool-calling chat skeleton (history + settings will be sent with every request).
        </p>
      </div>

      <ChatPanel />
    </div>
  </AppShell>
</template>


