# Session 015 - Flexible clinical safety and live backend restart

## Outcome

- Restarted the FastAPI backend so the running service now loads the current source.
- Fixed comma-separated symptom negation: `tidak ada demam, batuk, sulit bernapas` no longer triggers emergency escalation; a contrast such as `tetapi sulit bernapas` still does.
- Replaced all-or-nothing answer blocking with sentence-level removal of case-specific clinical inference.
- When every generated sentence is unsafe, the model receives one constrained rewrite attempt before the safe fallback is used.
- Kept empathetic language and grounded book facts available while blocking reassurance or prognosis about the specific child.

## Live verification

- `GET /health` returned `ok` with retrieval and LLM configured.
- A four-turn pilek flow with a comma-separated negative symptom list completed at safety level `general`.
- The final response returned one citation from `Menu sehat untuk anak sakit` through Supabase retrieval.

## Verification

- Backend test suite: 27 tests passed.
- Python application bytecode compilation passed.

## Boundary

- The current sentence-level policy is deliberately narrow and deterministic. Add structured clinical claim classification only after evaluation data shows recurring cases it cannot distinguish.
