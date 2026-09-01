# 0010 — Report theming as a repeatable, documented capability

- **Project:** repo-wide (new skill + convention)
- **Date:** 2026-09-01
- **Status:** decided

## The fork in the road

BI Task 1's report loaded with default Power BI styling — basic charts on a
white background. The user asked for it to look better, and separately asked
a forward-looking question: if a future client gives the agent a brand
brief, can the agent produce a matching theme (and layout) on its own,
without a human doing this by hand each time?

## What was decided

1. A real Power BI Theme JSON was produced for BI Task 1
   (`projects/bi-task-1/ToyCoSalesTheme.json`), confirmed against Microsoft's
   own `report-themes-create-custom` documentation rather than guessed.
   Since it's test data with no real client, the palette was designed
   fresh: 8 categorical data colors (an accessibility-checked set — CVD and
   low-vision contrast verified on adjacent pairs), status colors kept
   distinct from the categorical set, warm-neutral chrome, and
   `tableAccent` as the one brand-accent color. Applied via Desktop's
   *View → Themes → Browse for themes*, not baked into `report.json`'s
   `customTheme`/`resourcePackages` — see the reasoning in
   `.claude/skills/report-theming/SKILL.md`.
2. **New skill: `report-theming`.** Documents the real theme JSON schema,
   where client brand input fits (ask first; default to a validated
   palette if nothing is given), the accessibility checks a brand palette
   must still clear even when a client insists on their own colors, and
   the Desktop-only-fonts caveat for any theme that sets a custom
   `fontFace`.
3. **Explicit split, repo-wide, between theming and layout.** A color/text
   theme is a single well-documented JSON file Desktop validates on
   import — reliable. Visual *layout* (which charts, where, how sized) is
   the hand-authored PBIR `page.json`/`visual.json` layer this project
   spent an entire session's worth of Desktop-attempt cycles debugging
   (see `projects/bi-task-1/NOTES.md`). The skill instructs against
   answering "can it theme and layout visuals" with one yes — theming is a
   much safer promise than layout, and the response should say so.

## Why

The user's question was specifically about *repeatability* — not "can you
make this one report nicer" but "can the agent do this for a client on its
own next time." Answering that well means writing down the method (schema,
accessibility checks, font caveat, default palette), not just producing one
good file this session.

## Consequences

- Future projects should default to a themed report rather than Power BI's
  plain default, using `report-theming/SKILL.md`'s validated default
  palette when no client brand exists yet.
- A client's real brand colors, when given, must still pass the
  accessibility checks in that skill — a failing brand color is a
  `CLAUDE.md` §1 cross-roads (flag it, propose a lightness/saturation fix),
  not something to silently ship or silently override.
- This does **not** change the confidence level of hand-authored PBIR
  visuals/layout — that remains best-effort per `CLAUDE.md` §2, unaffected
  by how reliable theming turned out to be.
