<script setup lang="ts">
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
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
  <div v-if="modelOpen" class="fixed inset-0 z-50">
    <div class="absolute inset-0 bg-black/50" @click="modelOpen = false" />

    <div class="absolute inset-0 flex items-center justify-center p-4">
      <div class="w-full max-w-lg rounded-lg border bg-card shadow-lg">
        <div class="flex items-center justify-between border-b p-4">
          <div>
            <div class="text-sm font-semibold">Capabilities</div>
            <div class="text-xs text-muted-foreground">
              These settings are sent with every chat request.
            </div>
          </div>
          <Button type="button" variant="ghost" size="sm" @click="modelOpen = false">Close</Button>
        </div>

        <div class="flex flex-col gap-4 p-4">
          <ToggleSwitch
            v-model="settings.webSearch"
            label="Web Search"
            description="When enabled, the backend may expose a web_search tool to the model."
          />

          <ToggleSwitch
            v-model="settings.imageGeneration"
            label="Image Generation"
            description="When enabled, the backend may expose an image generation tool."
          />

          <ToggleSwitch
            v-model="settings.dataAnalysis"
            label="Data Analysis"
            description="When enabled, the backend may expose a data analysis tool."
          />

          <ToggleSwitch
            v-model="settings.thinkMode"
            label="Think Mode"
            description="When enabled, assistant responses should be longer and more structured."
          />
        </div>

        <div class="flex items-center justify-end gap-2 border-t p-4">
          <Button type="button" variant="secondary" @click="modelOpen = false">Done</Button>
        </div>
      </div>
    </div>
  </div>
</template>


