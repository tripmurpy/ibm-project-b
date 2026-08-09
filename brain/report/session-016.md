# Session 016 - Continuous composer focus and contextual fact memory

## Outcome

- Kept the textarea writable while a response is pending, disabled only duplicate submission, and restored focus after submit and request completion.
- Confirmed Mom and Koki Ben already read one shared history per thread.
- Fixed repeated questions by interpreting short replies against the immediately preceding assistant question.
- Negative replies such as `tidak ada` now satisfy the allergy-status question.
- Bare numeric ages and durations receive a unit clarification rather than the same question being repeated or a unit being guessed.
- Increased bounded thread history from 8 to 20 messages.
- Added root `REVISI.md` with all session issues, root causes, decisions, safety invariants, and regression checks.

## Verification

- Frontend: 5 tests passed and Vite production build passed.
- Backend: 29 tests passed and application bytecode compilation passed.

## Boundary

- Thread memory remains process-local and TTL-bound until authentication and durable ownership are implemented.
