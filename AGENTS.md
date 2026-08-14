# AGENTS.md — Renti

> Panduan untuk agent AI yang bekerja di repo ini. Baca `docs/STRUCTURE.md` untuk arsitektur monorepo & `docs/API_CONTRACT.md` untuk kontrak API (single source of truth).

## Agent skills

### Issue tracker
Issues live as GitHub issues in this repo, managed via the `gh` CLI. External PRs are not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels
Five canonical roles map to the default label names (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs
Single-context: one `CONTEXT.md` + `docs/decisions/` (ADR) at the repo root. See `docs/agents/domain.md`.
