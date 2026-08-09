# Session 017 - Query understanding and grounded recipe UX

## Outcome

- Reproduced the three screenshot issues across frontend rendering, router state, recipe retrieval, source cleaning, and live Supabase data.
- Preserved explicit recipe constraints: target condition, food versus drink form, age, and allergy.
- Removed automatic cross-selling and made clarification copy shorter, warmer, and user-centered.
- Made Koki Ben render reviewed structured recipe fields without LLM rewriting.
- Added clear specialist and source labels, deduplicated identical citations, and replaced the robotic welcome copy.
- Quarantined `Smoothie Avokad` without deleting it; the live recipe and knowledge chunk now have `medical_review_status = 'pending'`.

## Verification

- Frontend and data tests: 8 passed.
- Backend tests: 36 passed.
- Python compile check and Vite production build passed.
- Ingestion validation passed with 43 ready documents and 25 eligible recipe documents.
- Live query `Makanan untuk anak 5 tahun yang batuk pilek, alergi udang` routed to Koki Ben, returned a solid-food recipe for target condition `batuk pilek`, preserved structured ingredients and instructions, and returned one book citation.
- Browser flow on `http://localhost:5173` showed the warm welcome, `Menu anak` label, deterministic recipe structure, and one labeled `Sumber` item.

## Boundary

- `Smoothie Avokad` remains stored for audit and requires physical-book verification before it can be republished.
- Screenshot review confirms visible hierarchy and affordance only; full WCAG verification was not performed.
