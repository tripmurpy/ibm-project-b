# Session 014 - Natural chat lifecycle and seamless specialist handoff

## Outcome

- Replaced static `Sekarang` labels with the actual local message time.
- Added a native typing lifecycle: animated waiting dots followed by progressively revealed assistant text.
- Added reply/quote support for both user and assistant bubbles and forwarded the quote through the chat API.
- Changed bounded session context from agent-isolated histories to one thread history so Mom and Koki Ben can reuse facts without re-interviewing the user.
- Added deterministic, opt-in cross-domain follow-up offers without naming the internal handoff mechanism.
- Made Mom's model prompt more conversational and allowed safe empathy such as `Ibu pasti khawatir` while continuing to block clinical certainty such as `pasti flu`.
- Reworded unsafe-generation fallback to distinguish existing evidence from unsupported model phrasing.

## Root Cause

- The reviewed pilek data was available. The generic unsafe fallback could occur after successful retrieval because the output filter rejected every use of `pasti`, including non-clinical empathy requested by the Mom prompt.
- Agent-isolated cache histories prevented smooth cross-domain continuation even though the API already supported multiple response sections.

## Verification

- Frontend: 5 tests passed and Vite production build passed.
- Backend: 23 tests passed and application bytecode compilation passed.
- Added focused regression checks for real timestamps, reply context, natural empathy, shared handoff context, and affirmative handoff routing.

## Boundary

- Text reveal is a client-side chat effect after the complete HTTP response arrives; transport-level token streaming remains unnecessary until latency testing proves it is needed.
- Durable conversation storage remains disabled until authentication and thread ownership are implemented.
