<script setup lang="ts">
import type { UiAttachment } from '@/lib/chat'
import { AlertTriangle, CheckCircle2, FileText, Loader2, X } from 'lucide-vue-next'

defineProps<{
  attachments: UiAttachment[]
  removable?: boolean
}>()

const emit = defineEmits<{
  (e: 'remove', id: string): void
}>()
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <div
      v-for="a in attachments"
      :key="a.id"
      class="inline-flex max-w-full items-center gap-2 rounded-full border bg-muted px-3 py-1 text-xs"
      :class="
        a.status === 'uploaded'
          ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
          : a.status === 'warning'
            ? 'border-amber-200 bg-amber-50 text-amber-900'
            : a.status === 'error'
              ? 'border-destructive/30 bg-destructive/10 text-destructive'
              : 'text-muted-foreground'
      "
      :title="a.detail || a.filename"
    >
      <Loader2 v-if="a.status === 'uploading'" class="size-3.5 animate-spin" />
      <CheckCircle2 v-else-if="a.status === 'uploaded'" class="size-3.5" />
      <AlertTriangle v-else-if="a.status === 'warning' || a.status === 'error'" class="size-3.5" />
      <FileText v-else class="size-3.5" />

      <span class="max-w-56 truncate font-medium">{{ a.filename }}</span>

      <button
        v-if="removable"
        type="button"
        class="rounded-full p-0.5 hover:bg-black/5"
        :title="`Remove ${a.filename}`"
        @click="emit('remove', a.id)"
      >
        <X class="size-3.5" />
      </button>
    </div>
  </div>
</template>


