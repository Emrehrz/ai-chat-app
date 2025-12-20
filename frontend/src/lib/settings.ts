import { computed, reactive, watch } from 'vue'

export type AppSettings = {
  webSearch: boolean
  imageGeneration: boolean
  dataAnalysis: boolean
  thinkMode: boolean
}

const STORAGE_KEY = 'ai-chat-app:settings:v1'

function defaultSettings(): AppSettings {
  return {
    webSearch: false,
    imageGeneration: false,
    dataAnalysis: false,
    thinkMode: false,
  }
}

function loadSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return defaultSettings()
    const parsed = JSON.parse(raw) as Partial<AppSettings>
    return { ...defaultSettings(), ...parsed }
  } catch {
    return defaultSettings()
  }
}

const state = reactive<AppSettings>(loadSettings())

watch(
  () => ({ ...state }),
  (next) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    } catch {
      // ignore storage errors for the skeleton
    }
  },
  { deep: true },
)

export function useAppSettings() {
  const settings = state

  const asBackendPayload = computed(() => ({
    web_search: settings.webSearch,
    image_generation: settings.imageGeneration,
    data_analysis: settings.dataAnalysis,
    think_mode: settings.thinkMode,
  }))

  return { settings, asBackendPayload }
}


