---
name: sharepoint-data-ingestion
description: Use when a project's source data lives on company SharePoint rather than already being in the repo. Explains the current (manual) ingestion process and the status of automated ingestion.
---

# SharePoint data ingestion

## Current status: manual, interim

This GitHub Action runs non-interactively on `ubuntu-latest` with no
credentials for the company's SharePoint/Microsoft 365 tenant. It **cannot**
browse to a SharePoint URL and authenticate as a user — `WebFetch` against an
authenticated SharePoint link will just hit a login redirect, not the file.

Until proper ingestion is set up (see below), the process is:

1. A human downloads the relevant file(s) from SharePoint locally.
2. They're committed into `docs/sample-data/<project-name>/` in the repo
   (or attached to the triggering issue, in which case download them via
   the issue's attachment URL — GitHub attachment URLs *are* fetchable, since
   they don't require the tenant's SSO).
3. From there, treat them as any other source file per
   `CLAUDE.md` §3 (Discover/Profile).

**If you're asked to fetch something directly from a
`marlabseur.sharepoint.com` URL and no local copy exists in the repo or as
an issue attachment**, do not attempt to authenticate or work around it —
post a comment asking for the file to be attached to the issue or committed
to `docs/sample-data/`, and stop (per `CLAUDE.md` §1's ask-don't-guess rule —
this is a hard capability boundary, not a judgment call, but the resolution
still requires a human to act).

## Future: automated ingestion (not yet built)

If this becomes a recurring need, the real fix is a Microsoft Graph API app
registration (client credentials flow) with read access scoped to the
specific SharePoint site/library, its client ID/secret stored as GitHub
Actions secrets alongside `ANTHROPIC_API_KEY`, and a small script (e.g.
Python + `msal` + `requests`, or PowerShell + `PnP.PowerShell`) invoked via
the workflow's `Bash` step to pull files into `docs/sample-data/` before
Claude runs — or as a step Claude itself can invoke if the workflow's
`allowedTools` is widened to permit it.

This requires an IT/Azure AD admin to create the app registration — it's an
infrastructure decision outside what an agent run should do unprompted. If
you're a future Claude run considering building this, treat "set up
automated SharePoint ingestion" itself as a `docs/decisions/` cross-roads:
confirm scope (which site/library), auth approach, and secret naming with
the user before implementing.
