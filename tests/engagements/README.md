# Test Engagements — Quarantine Zone

**Every engagement in this directory is TEST DATA. None of these are real clients.**

This directory exists because synthetic test banks (Harborlight, Zenith, PBCOM Demo, Bank X)
previously lived under `engagements/` alongside real clients, and the knowledge-harvester
extracted their fabricated metrics into the shared knowledge base as if they were real,
anonymized, client-validated benchmarks. See `knowledge/learnings/EXTRACTION_REGISTRY.md`
(2026-07_retail_assessment [SYNTHETIC] row) for the contamination incident this fixes.

## The rules

1. **All test/synthetic/demo engagements live here** — never under `engagements/`.
   `engagements/` is for real clients only.
2. **Every test engagement carries a `.synthetic` marker file** at its root. Agents,
   skills, and scripts must treat any engagement containing `.synthetic` (or any path
   under `tests/`) as non-client data.
3. **Knowledge harvest is quarantined.** A pipeline or skill run against a test
   engagement must write its harvest to `<engagement>/outputs/knowledge_harvest/`
   **inside this directory** — never to `knowledge/domains/`, `knowledge/learnings/`,
   or any other shared knowledge path.
4. **Retrieval must exclude this directory.** Benchmark, pain-point, and journey
   retrieval (`/domain-*`, `benchmark-librarian`) must never source values from
   `tests/`. Anything tagged `[Synthetic-Test]` in shared knowledge is fabricated
   and must not be cited in client work.
5. **Contents are gitignored** (except this README). Some test engagements contain
   real source material used as test input (e.g. `test_wsfs` holds real WSFS
   documents) — PII/anonymization rules still apply to those.

## Creating a new test engagement

```bash
mkdir -p tests/engagements/<name>/{inputs,outputs}
cat > tests/engagements/<name>/.synthetic <<'EOF'
synthetic: true
created: <YYYY-MM-DD>
purpose: <what this test validates>
harvest_policy: quarantine   # harvest goes to outputs/knowledge_harvest/, never knowledge/
EOF
```

Then run the pipeline against `tests/engagements/<name>` exactly as you would a real
engagement directory.

## Current inventory

| Directory | What it is |
|-----------|------------|
| `harborlight_synthetic/` | Fictional NAM credit union — 2026-07 skill-first pipeline live test |
| `2602_Zenith_Nigeria/` | Fictional Nigerian retail bank — Cortex ontology demos |
| `pbcom_demo/` | Demo engagement |
| `bank_x_demo/` | Demo engagement |
| `test_wsfs/` | Test copy of **real** WSFS inputs — not fictional; PII rules apply |
