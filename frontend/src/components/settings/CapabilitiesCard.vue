<script setup lang="ts">
import { Globe, Image, PieChart, Sparkles } from 'lucide-vue-next'
import { Switch } from '@/components/ui/switch'
import { useAppSettings } from '@/lib/settings'

defineProps<{
  compact?: boolean
}>()

const { settings } = useAppSettings()
</script>

<template>
  <div class="rounded-lg border bg-card shadow-sm" :class="compact ? 'p-4' : 'p-6'">
    <div :class="compact ? 'mb-4' : 'mb-6'">
      <h2 :class="compact ? 'text-base font-semibold' : 'text-2xl font-bold'">Chat controls</h2>
      <p class="mt-1 text-sm text-muted-foreground">Capabilities</p>
    </div>

    <div :class="compact ? 'space-y-3' : 'space-y-4'">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center rounded-full bg-primary/10"
            :class="compact ? 'size-9' : 'size-10'">
            <Globe class="size-5 text-primary" />
          </div>
          <span :class="compact ? 'text-sm font-medium' : 'text-base font-medium'">Web Search</span>
        </div>
        <Switch :checked="settings.webSearch" @update:checked="(v: boolean) => (settings.webSearch = v)" />
      </div>

      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center rounded-full bg-primary/10"
            :class="compact ? 'size-9' : 'size-10'">
            <Image class="size-5 text-primary" />
          </div>
          <span :class="compact ? 'text-sm font-medium' : 'text-base font-medium'">Image Generation</span>
        </div>
        <Switch :checked="settings.imageGeneration" @update:checked="(v: boolean) => (settings.imageGeneration = v)" />
      </div>

      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center rounded-full bg-primary/10"
            :class="compact ? 'size-9' : 'size-10'">
            <PieChart class="size-5 text-primary" />
          </div>
          <span :class="compact ? 'text-sm font-medium' : 'text-base font-medium'">Data Analysis</span>
        </div>
        <Switch :checked="settings.dataAnalysis" @update:checked="(v: boolean) => (settings.dataAnalysis = v)" />
      </div>

      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center rounded-full bg-primary/10"
            :class="compact ? 'size-9' : 'size-10'">
            <Sparkles class="size-5 text-primary" />
          </div>
          <span :class="compact ? 'text-sm font-medium' : 'text-base font-medium'">Think</span>
        </div>
        <Switch :checked="settings.thinkMode" @update:checked="(v: boolean) => (settings.thinkMode = v)" />
      </div>
    </div>
  </div>
</template>
