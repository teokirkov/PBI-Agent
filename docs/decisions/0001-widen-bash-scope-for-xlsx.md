# 0001 — Widen Bash scope in claude.yml to allow python3 for .xlsx profiling

- **Project:** repo-wide (infrastructure convention, not project-specific)
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

The agent's core job requires profiling and reading `.xlsx` source files.
The `Read` tool alone doesn't reliably parse Excel workbooks (sheets,
merged headers, typed columns), so some form of scripted access is needed —
realistically Python with `pandas`/`openpyxl`. But `.github/workflows/claude.yml`
ran on `ubuntu-latest` with `Bash` scoped to `Bash(git:*)` only, and widening
`Bash` scope in an unattended CI job is a real security-relevant change
(bigger blast radius if a run misbehaves or is manipulated by adversarial
content it reads). Options considered:

1. Leave `Bash(git:*)` only — Claude can't profile `.xlsx` files at all,
   undermining the agent's main purpose.
2. Widen to plain `Bash(*)` — unrestricted shell, simplest but the largest
   possible blast radius.
3. Widen narrowly to `Bash(python3:*)` + `Bash(pip install:*)` — enough to
   run Python-based profiling/transform-checking scripts, without granting
   arbitrary shell command execution.

## What was decided

Option 3: `.github/workflows/claude.yml`'s `allowedTools` now includes
`Bash(python3:*),Bash(pip install:*)` in addition to `Bash(git:*)`.

## Why

Narrowest scope that unblocks the core use case. `python3:*` still lets
Claude run arbitrary Python code (so it isn't a hard sandbox), but it rules
out a large class of other shell-based actions (no arbitrary `curl`, `rm`,
`chmod`, etc. outside of what git/python already permit) compared to plain
`Bash(*)`.

## Consequences

- Claude can now install (`pip install pandas openpyxl` etc.) and run
  Python scripts as part of a run to profile/read `.xlsx` (and `.csv`, which
  it could already read directly) source files.
- If a future need arises for other CLI tools (e.g. a SharePoint/Graph API
  ingestion script — see `.claude/skills/sharepoint-data-ingestion/SKILL.md`),
  that's a separate scope decision, not automatically covered by this one.
- This is a repo-wide infrastructure decision, not scoped to one project —
  it applies to every future `@claude` run.
