# Decision log

This is the agent's persistent memory across runs (see `CLAUDE.md` §0 — each
GitHub Action run is stateless and only has this repo to remember from).

Every time a run hits a cross-roads per `CLAUDE.md` §1 and gets an answer
from the user, it should add one file here: `NNNN-short-slug.md`, numbered
sequentially, using `0000-template.md` as the starting point. Never edit or
delete a past decision to change its outcome — if a decision is later
reversed, add a new file that supersedes it and says so; the old one stays
as a record of what was decided when and why.

Decisions apply per-project unless explicitly marked as repo-wide
conventions (e.g. a modeling default that should now apply to every future
project, not just the one it came up in).
