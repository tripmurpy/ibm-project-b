# Session 013 - Warm Mom flow and selective knowledge publication

## Outcome

- Replaced rigid Mom follow-up copy with deterministic validation, fact reflection, a short reason for each question, associated-symptom screening, and recurrence-frequency handling.
- Normalized informal Indonesian repetition such as `pilek2` before fact extraction and retrieval.
- Added negation-aware red-flag handling so `tidak ada demam atau sulit bernapas` is not escalated while `tapi sulit bernapas` remains urgent.
- Moved Mom content-type filtering into `search_knowledge` before top-k ranking.
- Disabled exposed Qwen reasoning, constrained response length, removed decorative output, and blocked unsupported clinical inference.
- Constrained Koki Ben to one complete recipe and one citation, with hard allergy filtering and no recipes for children under one year.

## Published data

- Re-embedded 44 ready documents with normalized BGE-M3 1024-dimensional vectors.
- Published the source after operator authorization.
- Published one cleaned `batuk-pilek` health chunk as `approved`.
- Published 26 recipes and 26 recipe chunks as `not_required` for medical review.
- Kept 17 chunks pending and kept all 10 cleaning review-queue files outside ingestion.

## Live evidence

- Mom hybrid retrieval returns one reviewed health row for a pilek query.
- Koki Ben hybrid retrieval returns five eligible recipe candidates and sends only the highest-ranked safe recipe to generation.
- End-to-end Mom generation returns a grounded answer with one citation.
- End-to-end Koki Ben generation returns one complete recipe with one citation and no medical-benefit claim.

## Verification

- Backend: 21 tests passed and application bytecode compilation passed.
- Frontend: 4 tests passed and Vite production build passed.
- Live Supabase audit: 44 chunks, 0 orphan relations, normalized 1024-dimensional vectors, Mom retrieval 1 row, and Koki retrieval 5 rows.
- Local and remote migration histories match through `20260809055549`.
- Application duplicate-body scan found no repeated function implementations.

## Boundaries

- The remaining health and nutrition content is not published because the source contains claims that require separate safety review.
- Durable personal memory remains disabled until authentication and thread ownership exist.
- Supabase performance advisor returned no findings. Security advisor still reports the pre-existing public `rls_auto_enable()` security-definer grants; this session did not alter that unrelated function.
