<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'

const files = ref<File[]>([])

function onPick(e: Event) {
  const input = e.target as HTMLInputElement
  files.value = Array.from(input.files ?? [])
}

function onUpload() {
  // TODO: Wire to backend upload endpoint when implemented.
  alert(`Selected ${files.value.length} file(s). Upload is not implemented yet.`)
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <h1 class="text-lg font-semibold">Files (RAG)</h1>
      <p class="text-sm text-muted-foreground">
        Upload documents to associate with the current session. (Skeleton only)
      </p>
    </div>

    <section class="rounded-lg border bg-card p-4">
      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div class="font-medium">Upload</div>
          <div class="text-xs text-muted-foreground">TODO: type/size validation</div>
        </div>

        <input
          class="block w-full rounded-md border bg-background px-3 py-2 text-sm"
          type="file"
          multiple
          @change="onPick"
        />

        <div v-if="files.length" class="text-sm">
          <div class="mb-2 text-muted-foreground">Selected:</div>
          <ul class="list-disc pl-5">
            <li v-for="f in files" :key="f.name">{{ f.name }} ({{ f.size }} bytes)</li>
          </ul>
        </div>

        <div class="flex gap-2">
          <Button type="button" @click="onUpload">Upload (stub)</Button>
          <Button type="button" variant="secondary" @click="files = []">Clear</Button>
        </div>
      </div>
    </section>

    <section class="rounded-lg border bg-card p-4">
      <div class="flex flex-col gap-2">
        <div class="font-medium">How it will work (TODO)</div>
        <ul class="list-disc pl-5 text-sm text-muted-foreground">
          <li>Backend extracts text, chunks content, embeds, stores in ChromaDB.</li>
          <li>Chunks are associated with a session id.</li>
          <li>Chat calls retrieval only when needed and injects context.</li>
        </ul>
      </div>
    </section>
  </div>
</template>


