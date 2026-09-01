# The Correct Route — Claude GitHub Agent Setup

This is the clean, minimal path — no dead ends, no local Node/npm
install, no VS Code Desktop, no OAuth token detour. Everything runs
inside a **GitHub Codespace**, using an **Anthropic API key**. The only
things that happen outside the Codespace are clicking around on
GitHub.com and the Anthropic Console in your browser.

If you're setting this up on a new repo, follow this top to bottom.

---

## What you need before starting
- A GitHub account with permission to create repos
- An **Anthropic API key** — either your own (console.anthropic.com →
  API Keys → Create Key) or one provisioned by your org's admin/IT if
  your account sits under a company-managed Anthropic Console org

That's it. No Node.js, no npm, no git installation, no local terminal
setup of any kind is required.

---

## Step 1 — Create the GitHub repository
**Where:** GitHub.com (browser)

1. github.com → **"+"** (top right) → **New repository**
2. Name it, leave it empty (no README, no `.gitignore`, no license)
3. **Create repository**

---

## Step 2 — Open it in a Codespace
**Where:** GitHub.com (browser)

1. On the repo's page → green **Code** button → **Codespaces** tab →
   **Create codespace on main**
2. This opens a full cloud dev environment with Node.js and git already
   installed — nothing to set up locally.

---

## Step 3 — Install Claude Code and log in
**Where:** Codespace terminal (opens automatically at the bottom)

```
npm install -g @anthropic-ai/claude-code
claude
```
- First run shows a theme picker — use arrow keys + Enter, no typing
  needed
- Follow the login prompt

---

## Step 4 — Install the GitHub App and workflow
**Where:** Codespace terminal, inside the running `claude` session

```
/install-github-app
```
- Authorize the app on your repo via the browser prompt
- Say **yes** when asked to set up the GitHub Actions workflow file —
  this creates `.github/workflows/claude.yml`

Exit the session when done:
```
exit
```

---

## Step 5 — Add your project files
**Where:** Codespace terminal

If you already have project files locally (e.g. a `CLAUDE.md` and
supporting folders — such as this repo's scaffold), the simplest route is
to push them from your local machine — this only needs **git**, not
Node/npm, so it works even on locked-down machines:
```
cd "path/to/your/local/project"
git init
git add .
git commit -m "Add project files"
git remote add origin https://github.com/yourusername/your-repo.git
git branch -M main
git push -u origin main
```
Then, back in the Codespace terminal:
```
git pull origin main
```

**Alternatively**, if you're starting fresh with no local files, just
create them directly in the Codespace terminal using the file editor or
`cat > filename << 'EOF' ... EOF` heredocs, then:
```
git add .
git commit -m "Add project files"
git push origin main
```

---

## Step 6 — Get your Anthropic API key
**Where:** console.anthropic.com (browser)

1. Log in at console.anthropic.com
2. **API Keys** → **Create Key**
3. Copy the key immediately (shown once)

If you get an "Organization is blocking new organization creation for
domain [yourcompany.com]" message, your company already has a
managed Anthropic Console org — you'll need your IT/org admin to either
provision a key for you or grant you Console access.

---

## Step 7 — Add the key as a GitHub secret
**Where:** GitHub.com (browser)

1. Repo → **Settings → Secrets and variables → Actions**
2. **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: paste your key
5. **Add secret**

---

## Step 8 — Configure the workflow file
**Where:** Codespace terminal

This repo already ships a configured `.github/workflows/claude.yml` (see
that file) — you shouldn't need to hand-write it. If you do need to
regenerate or adjust it, overwrite it with something like:
```
cat > .github/workflows/claude.yml << 'EOF'
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: |
            --allowedTools "WebSearch,WebFetch,Read,Write,Edit,Bash(git:*)"
EOF
```

Push it:
```
git add .
git commit -m "Configure Claude GitHub Action with API key and web tools"
git push origin main
```

**Note:** `WebFetch` works out of the box. `WebSearch` additionally
requires it to be enabled on your API key's organization in the
Anthropic Console (a separate account-level setting, not something
`claude_args` alone controls) — check Console → org settings if search
calls return `Web search is not enabled for this organization`.

**A note specific to this repo's use case:** reading `.xlsx` source files
and generating TMDL/M reliably may need more than the `Bash(git:*)` scope
above — e.g. Python with `pandas`/`openpyxl` for data profiling. Widening
`Bash` scope in an automated CI workflow is a real security-relevant
change (broader blast radius if something goes wrong in a run), so treat
it as a deliberate decision, not a default — see
`docs/decisions/` once you make a call here, and log it there.

---

## Step 9 — Test it
**Where:** GitHub.com (browser)

1. Open (or create) any issue in the repo
2. **Comment** on it — not the issue body:
   ```
   @claude <your request>
   ```
3. Check the **Actions** tab — a run should appear within seconds
4. Claude will update its comment on the issue with progress and
   results, and open a PR if it makes any changes

**Signs it's working correctly:** the Action log shows real tool use
(reading files, fetching URLs) and takes more than a few hundred
milliseconds; `total_cost_usd` is greater than 0.

**Signs of a credential problem:** an instant failure (`duration_ms`
near 0, `total_cost_usd: 0`, `is_error: true`) — double-check the secret
name is exactly `ANTHROPIC_API_KEY` and the key itself is valid.

---

## Summary — the whole route in one glance

| Step | Where | What |
|---|---|---|
| 1 | GitHub.com | Create empty repo |
| 2 | GitHub.com | Open in Codespace |
| 3 | Codespace terminal | Install Claude Code, log in |
| 4 | Codespace terminal | `/install-github-app` |
| 5 | Local (git only) or Codespace | Push project files |
| 6 | Anthropic Console | Create API key |
| 7 | GitHub.com | Add key as `ANTHROPIC_API_KEY` secret |
| 8 | Codespace terminal | Configure `claude.yml` with the key + web tools |
| 9 | GitHub.com | Test with an `@claude` comment on an issue |

No local Node.js, no npm on your own machine, no VS Code Desktop, no
OAuth token — the Codespace and an API key are all that's needed.
