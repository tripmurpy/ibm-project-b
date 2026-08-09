# Backend chat base

Run locally after installing dependencies:

```powershell
python -m pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
python -m unittest discover -s backend/tests
uvicorn app.main:app --app-dir backend --reload
```

The app reads local server settings from the repository `.env`; secrets are never sent to the browser. `POST /v1/chat` accepts:

```json
{
  "request_id": "uuid",
  "thread_id": "uuid-or-null",
  "question": "string"
}
```

`request_id` makes retries idempotent. `thread_id` keeps bounded short-term histories isolated by agent in an in-process TTL cache. A short follow-up stays with the active agent. The base cache is intentionally single-process; replace it with Redis only when deployment uses multiple backend replicas. Supabase remains the durable source of truth once authentication and thread ownership are connected.

The response keeps legacy `answer` and adds agent-aware output:

```json
{
  "route": "knowledge|recipe|mixed|clarify|escalate|out_of_scope",
  "sections": [
    {
      "agent": "mom|koki_ben",
      "answer": "string",
      "citations": [],
      "needs_clarification": false
    }
  ]
}
```

Mom validates the mother's concern, reflects known facts, explains why the next fact is needed, then collects complaint, age, duration, associated symptoms, and recurrence frequency when applicable. Informal repetition such as `pilek2` is normalized. Koki Ben collects age and allergy constraints, rejects the unscoped corpus for babies under one, and grounds one complete recipe in one citation. Both use the same workflow implementation with separate declarative policies and isolated session histories.

Provider behavior:

- Supabase hybrid retrieval is enabled when the project URL and service-role key exist.
- The OpenAI-compatible LLM adapter is enabled when `LLM_API_KEY` or the legacy `OPENAI_API_KEY` exists.
- If retrieval has no published/reviewed evidence, the backend abstains before spending an LLM call.
- `GET /health` reports only configured/unconfigured states and never returns credentials.
