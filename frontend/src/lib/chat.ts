import { computed, ref } from 'vue'
import { useAppSettings } from '@/lib/settings'

export type ChatRole = 'user' | 'assistant' | 'system' | 'tool'

export type ChatMessage = {
  role: ChatRole
  content: string
}

export type ToolCallLog = {
  name: string
  input?: Record<string, unknown>
  output_preview?: string
  error?: string | null
}

export type ChatResponse = {
  session_id: string
  assistant_message?: ChatMessage | null
  tool_calls?: ToolCallLog[]
  error?: string | null
}

function apiBaseUrl() {
  // Optional: you can set VITE_API_BASE_URL in your local env.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const env = (import.meta as any).env as Record<string, string | undefined>
  return env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
}

export function useChat() {
  const { asBackendPayload } = useAppSettings()

  const sessionId = ref<string | null>(null)
  const messages = ref<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        'Hi! This is the frontend skeleton. Hook me up to the FastAPI /chat endpoint when ready.',
    },
  ])

  const toolCalls = ref<ToolCallLog[]>([])
  const isLoading = ref(false)
  const lastError = ref<string | null>(null)

  const canSend = computed(() => !isLoading.value)

  async function send(userText: string) {
    if (!userText.trim() || isLoading.value) return

    lastError.value = null
    toolCalls.value = []
    isLoading.value = true

    messages.value.push({ role: 'user', content: userText })

    try {
      const res = await fetch(`${apiBaseUrl()}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          messages: messages.value,
          settings: asBackendPayload.value,
        }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(`HTTP ${res.status}: ${text}`)
      }

      const data = (await res.json()) as ChatResponse
      sessionId.value = data.session_id
      if (data.tool_calls) toolCalls.value = data.tool_calls

      if (data.error) {
        lastError.value = data.error
        return
      }

      if (data.assistant_message?.content) {
        messages.value.push({ role: 'assistant', content: data.assistant_message.content })
      } else {
        messages.value.push({
          role: 'assistant',
          content: '(No assistant message returned — endpoint not implemented yet.)',
        })
      }
    } catch (e) {
      // If backend isn't ready yet, keep the UI usable.
      const msg = e instanceof Error ? e.message : 'Unknown error'
      lastError.value = msg
      messages.value.push({
        role: 'assistant',
        content: `Backend call failed (skeleton fallback): ${msg}`,
      })
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    sessionId.value = null
    toolCalls.value = []
    lastError.value = null
    messages.value = [
      { role: 'assistant', content: 'New session started. (Skeleton)' },
    ]
  }

  return {
    sessionId,
    messages,
    toolCalls,
    isLoading,
    lastError,
    canSend,
    send,
    reset,
  }
}


