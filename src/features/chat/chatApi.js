const apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export async function sendChat({ requestId, threadId, question, replyTo }) {
  const response = await fetch(`${apiUrl}/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request_id: requestId, thread_id: threadId, question, reply_to: replyTo }),
  })

  if (!response.ok) {
    throw new Error(`Chat API returned HTTP ${response.status}`)
  }

  return response.json()
}
