<script setup lang="ts">
import { computed } from 'vue'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
import ToggleSwitch from '@/components/settings/ToggleSwitch.vue'
import { useAppSettings } from '@/lib/settings'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'update:open', v: boolean): void }>()

const modelOpen = computed({
  get: () => props.open,
  set: (v: boolean) => emit('update:open', v),
})

const { settings } = useAppSettings()
</script>

<template>
  <Dialog v-model:open="modelOpen">
    <DialogContent class="sm:max-w-125">
      <DialogHeader>
        <DialogTitle>Capabilities</DialogTitle>
        <DialogDescription>
          These settings control which tools are available to the AI assistant. Changes are sent with every chat
          request.
        </DialogDescription>
      </DialogHeader>

      <Separator class="my-4" />

      <div class="space-y-6">
        <ToggleSwitch v-model="settings.webSearch" label="Web Search"
          description="When enabled, the backend may expose a web_search tool to the model." />

        <ToggleSwitch v-model="settings.imageGeneration" label="Image Generation"
          description="When enabled, the backend may expose an image generation tool." />

        <ToggleSwitch v-model="settings.dataAnalysis" label="Data Analysis"
          description="When enabled, the backend may expose a data analysis tool." />

        <ToggleSwitch v-model="settings.thinkMode" label="Think Mode"
          description="When enabled, assistant responses should be longer and more structured." />
      </div>
    </DialogContent>
  </Dialog>
</template>
