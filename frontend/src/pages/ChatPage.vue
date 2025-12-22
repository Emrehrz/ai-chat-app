<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Globe, Image, Paperclip, PieChart, Settings, Sparkles, Upload } from 'lucide-vue-next'
import MessageList from '@/components/chat/MessageList.vue'
import MessageComposer from '@/components/chat/MessageComposer.vue'
import CapabilitiesCard from '@/components/settings/CapabilitiesCard.vue'
import { useChat } from '@/lib/chat'
import { useAppSettings } from '@/lib/settings'

const chat = useChat()
const { settings: appSettings } = useAppSettings()

const sessionLabel = computed(() => chat.sessionId.value ?? '(new session)')
const controlsOpen = ref(false)

const hasMessages = computed(() => (chat.messages.value ?? []).some((m) => m.role === 'user'))

const selectedFiles = ref<File[]>([])
const isUploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const scrollAreaRef = ref<HTMLElement | null>(null)
const autoScrollArmed = ref(false)

const enabledCapabilityBadges = computed(() => {
  const out: Array<{ key: string; label: string; icon: unknown }> = []
  if (appSettings.webSearch) out.push({ key: 'web', label: 'Web', icon: Globe })
  if (appSettings.imageGeneration) out.push({ key: 'img', label: 'Image', icon: Image })
  if (appSettings.dataAnalysis) out.push({ key: 'data', label: 'Data', icon: PieChart })
  if (appSettings.thinkMode) out.push({ key: 'think', label: 'Think', icon: Sparkles })
  return out
})

function scrollToLastMessage(behavior: ScrollBehavior = 'smooth') {
  const root = scrollAreaRef.value
  if (!root) return
  const last = root.querySelector('[data-chat-last="true"]') as HTMLElement | null
  last?.scrollIntoView({ behavior, block: 'start' })
}

function onSend(text: string) {
  autoScrollArmed.value = true
  void chat.send(text)
  void nextTick(() => scrollToLastMessage('smooth'))
}

watch(
  () => (chat.messages.value ?? []).length,
  () => {
    if (!autoScrollArmed.value) return
    void nextTick(() => scrollToLastMessage('smooth'))
  },
)

watch(
  () => chat.isLoading.value,
  (loading) => {
    if (!autoScrollArmed.value) return
    void nextTick(() => scrollToLastMessage(loading ? 'smooth' : 'smooth'))
    if (!loading) autoScrollArmed.value = false
  },
)

function triggerFilePicker() {
  fileInputRef.value?.click()
}

function onFilePick(e: Event) {
  const input = e.target as HTMLInputElement
  selectedFiles.value = Array.from(input.files ?? [])
  if (selectedFiles.value.length) {
    void onUpload()
  }
}

async function onUpload() {
  if (!selectedFiles.value.length || isUploading.value) return

  isUploading.value = true
  try {
    const formData = new FormData()
    selectedFiles.value.forEach((f) => formData.append('files', f))
    if (chat.sessionId.value) {
      formData.append('session_id', chat.sessionId.value)
    }

    const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
    const res = await fetch(`${apiBase}/files/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const text = await res.text()
      throw new Error(`Upload failed: ${text}`)
    }

    const data = await res.json()
    if (data.session_id && !chat.sessionId.value) {
      chat.sessionId.value = data.session_id
    }

    selectedFiles.value = []
    if (fileInputRef.value) fileInputRef.value.value = ''
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Upload failed'
    alert(`Upload error: ${msg}`)
  } finally {
    isUploading.value = false
  }
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
  if (!selectedFiles.value.length && fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}
</script>

<template>
  <div class="flex h-full min-h-0 flex-col">
    <!-- Empty state: centered on desktop, bottom on mobile -->
    <div v-if="!hasMessages" class="flex flex-1 items-center justify-center p-4 md:items-center md:justify-center">
      <div class="w-full max-w-3xl">
        <div class="mb-6 text-center">
          <h2 class="text-2xl font-semibold">AI Chat Assistant</h2>
          <p class="mt-2 text-sm text-muted-foreground">Configure capabilities, upload files, and start chatting.</p>
        </div>

        <div class="rounded-lg p-4">
          <!-- Controls row (Add file + Settings) -->
          <div class="relative mb-3 flex items-center gap-2">
            <Button type="button" variant="outline" class="w-fit" @click="triggerFilePicker">
              <Upload class="mr-2 size-4" />
              Add file
            </Button>

            <Popover :open="controlsOpen" @update:open="(v: boolean) => (controlsOpen = v)">
              <PopoverTrigger as-child>
                <Button type="button" variant="outline" class="w-fit">
                  <Settings class="mr-2 size-4" />
                  Settings
                </Button>
              </PopoverTrigger>
              <PopoverContent side="top" align="end" class="w-[calc(100vw-2rem)] p-0 sm:w-95">
                <CapabilitiesCard compact />
              </PopoverContent>
            </Popover>

            <div v-if="enabledCapabilityBadges.length" class="ml-auto hidden items-center gap-2 sm:flex">
              <span v-for="b in enabledCapabilityBadges" :key="b.key"
                class="inline-flex items-center gap-1 rounded-full border bg-muted px-2 py-1 text-[11px] text-muted-foreground"
                :title="`Enabled: ${b.label}`">
                <component :is="b.icon" class="size-3.5 text-primary" />
                <span class="font-medium text-foreground">{{ b.label }}</span>
              </span>
            </div>
          </div>

          <MessageComposer :disabled="!chat.canSend.value" @send="onSend">
            <template #prepend>
              <input ref="fileInputRef" type="file" multiple class="hidden" @change="onFilePick" />
              <button type="button" class="rounded-md p-2 hover:bg-accent" title="Attach files"
                @click="triggerFilePicker">
                <Paperclip class="size-4" />
              </button>
            </template>
            <template #attachments>
              <div v-if="selectedFiles.length" class="mb-2 flex flex-wrap gap-2">
                <button v-for="(f, idx) in selectedFiles" :key="f.name" type="button"
                  class="inline-flex max-w-full items-center gap-2 rounded-full border bg-muted px-3 py-1 text-xs hover:bg-muted/70"
                  :title="`Remove ${f.name}`" @click="removeFile(idx)">
                  <span class="max-w-56 truncate">{{ f.name }}</span>
                  <span class="text-muted-foreground">×</span>
                </button>
              </div>
            </template>
            <template #actions>
              <span v-if="isUploading" class="px-2 text-xs text-muted-foreground">Uploading…</span>
            </template>
          </MessageComposer>

          <div class="mt-2 text-xs text-muted-foreground">Session: {{ sessionLabel }}</div>
        </div>
      </div>
    </div>

    <!-- Active chat: only the message area scrolls; input stays pinned to bottom -->
    <div v-else class="flex flex-1 min-h-0 flex-col">
      <!-- Extra bottom padding so the last message has breathing room above the fixed composer -->
      <div ref="scrollAreaRef" class="min-h-0 flex-1 overflow-y-auto p-4 pb-56">
        <div class="mx-auto max-w-3xl space-y-4">
          <MessageList :messages="chat.messages.value ?? []" :is-loading="chat.isLoading.value" />

          <div v-if="chat.lastError.value" class="rounded-md border border-destructive/40 bg-destructive/10 p-3">
            <div class="text-xs font-medium text-destructive">Error</div>
            <div class="mt-1 text-xs text-destructive">{{ chat.lastError.value }}</div>
          </div>

        </div>
      </div>

      <!-- Sticky, compact composer like Gemini: centered panel, not full-width -->
      <div class="fixed bottom-0 right-0 left-0 z-10 p-4">
        <div class="mx-auto w-full max-w-3xl">
          <div class="rounded-2xl border bg-card/95 p-3 shadow-sm backdrop-blur supports-backdrop-filter:bg-card/80">
            <!-- Controls row (Add file + Settings) -->
            <div class="relative mb-3 flex items-center gap-2">
              <Button type="button" variant="outline" class="w-fit" @click="triggerFilePicker">
                <Upload class="mr-2 size-4" />
                Add file
              </Button>

              <Popover :open="controlsOpen" @update:open="(v: boolean) => (controlsOpen = v)">
                <PopoverTrigger as-child>
                  <Button type="button" variant="outline" class="w-fit">
                    <Settings class="mr-2 size-4" />
                    Settings
                  </Button>
                </PopoverTrigger>
                <PopoverContent side="top" align="end" class="w-[calc(100vw-2rem)] p-0 sm:w-95">
                  <CapabilitiesCard compact />
                </PopoverContent>
              </Popover>

              <div v-if="enabledCapabilityBadges.length" class="ml-auto hidden items-center gap-2 sm:flex">
                <span v-for="b in enabledCapabilityBadges" :key="b.key"
                  class="inline-flex items-center gap-1 rounded-full border bg-muted px-2 py-1 text-[11px] text-muted-foreground"
                  :title="`Enabled: ${b.label}`">
                  <component :is="b.icon" class="size-3.5 text-primary" />
                  <span class="font-medium text-foreground">{{ b.label }}</span>
                </span>
              </div>

            </div>

            <MessageComposer :disabled="!chat.canSend.value" @send="onSend">
              <template #prepend>
                <input ref="fileInputRef" type="file" multiple class="hidden" @change="onFilePick" />
                <button type="button" class="rounded-md p-2 hover:bg-accent" title="Attach files"
                  @click="triggerFilePicker">
                  <Paperclip class="size-4" />
                </button>
              </template>
              <template #attachments>
                <div v-if="selectedFiles.length" class="mb-2 flex flex-wrap gap-2">
                  <button v-for="(f, idx) in selectedFiles" :key="f.name" type="button"
                    class="inline-flex max-w-full items-center gap-2 rounded-full border bg-muted px-3 py-1 text-xs hover:bg-muted/70"
                    :title="`Remove ${f.name}`" @click="removeFile(idx)">
                    <span class="max-w-56 truncate">{{ f.name }}</span>
                    <span class="text-muted-foreground">×</span>
                  </button>
                </div>
              </template>
              <template #actions>
                <span v-if="isUploading" class="px-2 text-xs text-muted-foreground">Uploading…</span>
              </template>
            </MessageComposer>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
