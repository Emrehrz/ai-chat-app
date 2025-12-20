<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
import { Button } from '@/components/ui/button'
import SettingsDialog from '@/components/settings/SettingsDialog.vue'
import { useAppSettings } from '@/lib/settings'
import { ref } from 'vue'

const { settings } = useAppSettings()
const open = ref(false)
</script>

<template>
  <AppShell>
    <div class="flex flex-col gap-6">
      <div>
        <h1 class="text-lg font-semibold">Settings</h1>
        <p class="text-sm text-muted-foreground">
          Capability toggles are enforced by the backend; frontend only sends settings with each request.
        </p>
      </div>

      <section class="rounded-lg border bg-card p-4">
        <div class="flex items-center justify-between gap-4">
          <div class="flex flex-col">
            <div class="font-medium">Capability toggles</div>
            <div class="text-sm text-muted-foreground">Open the settings dialog to edit.</div>
          </div>
          <Button type="button" @click="open = true">Open</Button>
        </div>
      </section>

      <section class="rounded-lg border bg-card p-4">
        <div class="font-medium">Current values</div>
        <pre class="mt-2 overflow-auto rounded-md bg-muted p-3 text-xs">{{ settings }}</pre>
      </section>

      <SettingsDialog v-model:open="open" />
    </div>
  </AppShell>
</template>


