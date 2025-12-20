<script setup lang="ts">
import { ref } from 'vue'
import SidebarNav from '@/components/nav/SidebarNav.vue'
import TopBar from '@/components/nav/TopBar.vue'
import SettingsDialog from '@/components/settings/SettingsDialog.vue'

const settingsOpen = ref(false)
</script>

<template>
  <div class="min-h-dvh bg-background text-foreground">
    <div class="grid min-h-dvh grid-cols-[260px_1fr]">
      <aside class="border-r bg-sidebar text-sidebar-foreground">
        <SidebarNav />
      </aside>

      <div class="flex min-w-0 flex-col">
        <TopBar @open-settings="settingsOpen = true" />
        <main class="min-h-0 flex-1 overflow-auto">
          <div class="mx-auto w-full max-w-5xl p-4 md:p-6">
            <slot />
          </div>
        </main>
      </div>
    </div>

    <SettingsDialog v-model:open="settingsOpen" />
  </div>
</template>


