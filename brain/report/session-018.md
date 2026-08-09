# Session 018 - Retrieval and health-answer safety regression repair

## Outcome

- Found that Mom passed `target_condition = batuk pilek` into health retrieval even though published health chunks use a null target condition; this filtered the valid `Batuk Pilek` chunk out and caused the user-facing empty-evidence fallback.
- Limited the target-condition filter to recipe retrieval only.
- Confirmed live Supabase contains the approved `Batuk Pilek` health chunk and that the corrected chat flow returns a citation.
- Replaced free-form model rewriting for Mom after health retrieval with a direct excerpt from the reviewed source. This removes the unreliable pattern of generating medical language first and attempting to filter every unsafe paraphrase afterwards.

## Verification

- Backend tests: 30 passed.
- Live flow `pilek -> usia -> durasi -> skrining gejala` completed with one source citation and without the empty-evidence fallback.

## Boundary

- Mom now prioritizes source fidelity and safety over conversational summarization. Future generated medical summaries require a structured, evidence-attributed contract before being exposed to users.
