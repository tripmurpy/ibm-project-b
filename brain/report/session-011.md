# Session 011 - Backend API and bounded chat cache base

## Outcome

- Connected the React chat flow to `POST /v1/chat` with `sending`, `completed`, and `failed` UI states.
- Added UUID `request_id`, `thread_id`, and `message_id` to the API contract.
- Added an in-process TTL/LRU cache for bounded short-term history and idempotent retries.
- Connected backend adapters to the live Supabase hybrid-search RPC and the configured OpenAI-compatible LLM provider.
- Preserved the safety boundary: emergency checks run before retrieval, and empty published evidence abstains before the LLM call.

## Cache Boundary

- Cache stores at most the configured recent messages per thread and expires them after the configured TTL.
- Cache is local to one backend process and is not durable memory.
- Durable chat persistence, ownership, and cross-replica cache are deferred until authentication is connected.
- No semantic answer cache is used because medical/parenting answers must not be reused across users or changed context without a deliberate policy.

## Verification

- Backend unit tests: 3 passed.
- Frontend unit tests: 3 passed.
- Frontend production build passed.
- ASGI smoke test confirmed emergency escalation and idempotent retry cache hit.
- Live Supabase RPC connection passed; it returned zero published rows because the ingested source remains draft/pending.
- Live LLM provider connection passed with `qwen/qwen3.6-27b`.
