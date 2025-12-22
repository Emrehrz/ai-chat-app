<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar'
import { RouterLink, useRoute } from 'vue-router'
import { MessageSquare, FileText, Settings, Sparkles } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

const route = useRoute()

function linkClass(path: string) {
  const active = route.path === path
  return cn(
    'flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors',
    active
      ? 'bg-sidebar-accent text-sidebar-accent-foreground'
      : 'text-sidebar-foreground/80 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground',
  )
}
</script>

<template>
  <SidebarProvider>
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div class="flex items-center justify-between px-2">
          <div class="flex items-center gap-2">
            <Sparkles class="size-5 shrink-0" />
            <div class="flex flex-col group-data-[collapsible=icon]:hidden">
              <div class="text-sm font-semibold">AI Chat</div>
              <div class="rounded-full border px-2 py-0.5 text-[10px] text-sidebar-foreground/70">
                skeleton
              </div>
            </div>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton :as-child="true" :is-active="route.path === '/chat'" tooltip="Chat">
                  <RouterLink :class="linkClass('/chat')" to="/chat">
                    <MessageSquare class="size-4" />
                    <span>Chat</span>
                  </RouterLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton :as-child="true" :is-active="route.path === '/files'" tooltip="Files (RAG)">
                  <RouterLink :class="linkClass('/files')" to="/files">
                    <FileText class="size-4" />
                    <span>Files (RAG)</span>
                  </RouterLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton :as-child="true" :is-active="route.path === '/settings'" tooltip="Settings">
                  <RouterLink :class="linkClass('/settings')" to="/settings">
                    <Settings class="size-4" />
                    <span>Settings</span>
                  </RouterLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <div class="px-2 py-2 text-xs text-sidebar-foreground/60 group-data-[collapsible=icon]:hidden">
          Backend-driven agent logic + conditional tools.
        </div>
      </SidebarFooter>
    </Sidebar>

    <SidebarInset>
      <header class="flex h-14 shrink-0 items-center gap-2 px-4">
        <SidebarTrigger />
      </header>
      <main class="flex flex-1 min-h-0 flex-col overflow-hidden">
        <RouterView />
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
