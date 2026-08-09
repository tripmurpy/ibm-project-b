import assert from 'node:assert/strict'
import test from 'node:test'
import ChatMessage from './ChatMessage.js'

test('creates a normalized user message', () => {
  const message = ChatMessage.fromUser('  Halo  ')

  assert.equal(message.from, 'user')
  assert.equal(message.text, 'Halo')
  assert.ok(message.id)
  assert.match(message.time, /^\d{2}[.:]\d{2}$/)
})

test('keeps replied bubble context', () => {
  const replyTo = { id: 'mom-1', from: 'assistant', text: 'Usianya berapa, Bu?' }
  const message = ChatMessage.fromUser('5 tahun', replyTo)

  assert.equal(message.replyTo, replyTo)
})

test('rejects empty messages and unknown senders', () => {
  assert.throws(() => ChatMessage.fromUser('   '), /cannot be empty/)
  assert.throws(
    () => new ChatMessage({ from: 'system', text: 'Halo' }),
    /Unknown message sender/,
  )
})

test('creates a processing placeholder for the API lifecycle', () => {
  const message = ChatMessage.pending('pending-1')

  assert.equal(message.from, 'assistant')
  assert.equal(message.status, 'processing')
})

test('keeps the specialist label on assistant messages', () => {
  const message = ChatMessage.fromAssistant({ id: 'mom-1', answer: 'Halo, Bu.', agent: 'mom' })

  assert.equal(message.agent, 'mom')
})

test('deduplicates identical public citations', () => {
  const citation = { chunk_id: 'one', source_title: 'Menu sehat untuk anak sakit', page_start: null, page_end: null }
  const message = ChatMessage.fromAssistant({
    id: 'mom-2',
    answer: 'Jawaban dari buku.',
    citations: [citation, { ...citation, chunk_id: 'two' }],
  })

  assert.equal(message.citations.length, 1)
})

test('creates a warm welcome that explains the product naturally', () => {
  const message = ChatMessage.welcome()

  assert.equal(message.from, 'assistant')
  assert.match(message.text, /cerita|tanyakan/i)
  assert.match(message.text, /kesehatan ringan|menu/i)
})
