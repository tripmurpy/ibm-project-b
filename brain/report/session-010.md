# Session 010 - BGE-M3 ingest and relational audit

## Outcome

- Regenerated cleaning output and removed one stale review artifact from the ready directory.
- Validated 44 ready Markdown files; held 10 unsafe or structurally ambiguous files for manual review.
- Generated 44 normalized dense embeddings locally with `BAAI/bge-m3` at 1024 dimensions.
- Ingested one source, 26 structured recipes, 8 structured tips, and 44 knowledge chunks into the IBM Supabase project.
- Verified all 26 recipe chunks and 8 tip chunks resolve through live PostgREST relationships; orphan count is zero.
- Verified the source remains draft/pending and hybrid retrieval returns zero rows before human review.

## Reproducible checks

```powershell
npm run data:validate
npm run data:audit
```

## Safety boundary

The ingest completed, but no medical content was auto-approved or published. The separate `cookpal.ai` project was not modified.
