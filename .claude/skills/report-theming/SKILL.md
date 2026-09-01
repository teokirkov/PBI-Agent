---
name: report-theming
description: Use when a project needs visual styling — a color theme and/or report layout — beyond Power BI's plain default. Covers the real Power BI Theme JSON schema, where client brand colors fit in, an accessible default palette to fall back on, and the honest split between theming (reliable) and visual layout (the fragile part of this whole pipeline).
---

# Report theming

## The two things people mean by "make it look better," and why they're not equally safe

1. **A color/text theme** — a single JSON file, officially documented,
   validated by Desktop on import. Low risk. This skill covers it in full.
2. **Visual layout** — which charts go where, sized how, on which page —
   is the hand-authored PBIR `page.json`/`visual.json` layer covered in
   `pbip-tmdl-structure/SKILL.md` and `CLAUDE.md` §2's visuals caveat. This
   is the least reliable part of the whole pipeline (see
   `projects/bi-task-1/NOTES.md`'s Desktop-attempt log for how much
   iteration the first real visual draft took). A theme can be handed off
   with high confidence; a bespoke layout should still be flagged as a
   rough draft, same as it already is.

Don't conflate the two in a response to the user — "yes to a theme" is a
much stronger promise than "yes to a layout."

## Where the color/text theme comes from

**Ask first (per `CLAUDE.md` §1 spirit, though this isn't strictly a
cross-roads — it's a preference, so a sensible default is fine to proceed
with, just say what you picked):**

- If the assignment/comment thread gives brand colors, a logo, or a
  described mood ("navy and gold," "match our website"), start from that.
- If nothing is given, don't ask and stall — use a well-designed default
  and say so in the summary comment. The default this repo has already
  validated is `projects/bi-task-1/ToyCoSalesTheme.json`'s palette:
  categorical `#2a78d6 #eb6834 #1baf7a #eda100 #e87ba4 #008300 #4a3aa7
  #e34948`, status `good #0ca30c / neutral #fab219 / bad #d03b3b`, chrome
  `background #fffdf9`, `secondaryBackground #faf7f0`,
  `firstLevelElements #1c1a17`, `secondLevelElements #5b564c`,
  `tableAccent #26417a`. Reuse it as-is for another generic/test project;
  derive a new one the same way (below) for a real client with their own
  brand.

## Accessibility is not optional, including for brand colors

Before adopting any palette — a client's brand colors included — check:

- **Contrast**: text/foreground colors need to hold up against the
  backgrounds they'll sit on. Aim for readable contrast on both
  `background` and `secondaryBackground` (rough guide: ~4.5:1 for body
  text, ~3:1 for large text/large UI elements).
- **Distinguishability of adjacent categorical colors**: two data colors
  that are perceptually close (as hues, and simulated for red/green and
  blue/yellow color-vision deficiency) will be genuinely hard to tell apart
  on a chart. If a client's brand palette only gives you 2-3 usable hues,
  don't force 8 data colors out of near-duplicates — extend with clearly
  distinct hues that still sit comfortably alongside the brand colors, and
  say what you added and why.

**If a client's exact brand colors fail either check** (e.g. their two
brand colors are both light and low-contrast on a white background), that
*is* a cross-roads per `CLAUDE.md` §1 — flag it in a comment with the
specific problem and a proposed fix (usually: keep the brand hue, shift its
lightness/saturation until it clears the check), rather than silently
shipping a theme that will look washed out or be hard to read.

## The real Power BI Theme JSON shape

Confirmed against Microsoft's own `report-themes-create-custom`
documentation — this is the actual schema Desktop validates on import, not
a guess:

```json
{
  "name": "Client Name Here",
  "dataColors": ["#hex", "#hex", "..."],
  "good": "#hex", "neutral": "#hex", "bad": "#hex",
  "maximum": "#hex", "center": "#hex", "minimum": "#hex", "null": "#hex",
  "firstLevelElements": "#hex",
  "secondLevelElements": "#hex",
  "thirdLevelElements": "#hex",
  "fourthLevelElements": "#hex",
  "background": "#hex",
  "secondaryBackground": "#hex",
  "tableAccent": "#hex",
  "textClasses": {
    "callout": { "fontFace": "...", "color": "#hex" },
    "title": { "fontFace": "...", "color": "#hex" },
    "header": { "fontFace": "...", "color": "#hex" },
    "label": { "fontFace": "...", "color": "#hex" }
  }
}
```

- `name` is the only required field; only set what you actually want to
  change from Power BI's defaults.
- `dataColors` — chart series colors, in order. Power BI auto-generates
  extra shades if more series appear than colors provided.
- `good`/`neutral`/`bad` — waterfall and KPI visual status colors. Keep
  these visually distinct from the `dataColors` set — a status color that
  matches a series color reads as that series, not as a status.
- `maximum`/`center`/`minimum` — the 3-color gradient used in conditional
  formatting. If the palette has a natural diverging pair (e.g. a
  "good direction" and "bad direction" hue), use those as
  `maximum`/`minimum` with a neutral gray `center` — don't invent an
  unrelated third hue here.
- `firstLevelElements` through `fourthLevelElements`, `background`,
  `secondaryBackground`, `tableAccent` — structural colors (text, gridlines,
  backgrounds, table accents). See the official doc's full mapping table if
  a specific visual element needs targeting; the common case is just setting
  these seven plus the data colors.
- `textClasses` — only the four *primary* classes (`callout`, `title`,
  `header`, `label`) need setting; secondary classes (bold, small, light
  variants) inherit automatically. `callout` is what Card/KPI visuals use
  for their big number — this is usually the one place worth a distinct
  face (e.g. a monospace/tabular face) if the project wants numbers to
  read as data instrumentation rather than prose.

## The font caveat — say this explicitly whenever a theme sets a custom `fontFace`

**Power BI Desktop only renders fonts installed in Windows — it does not
support web fonts.** A `fontFace` naming a font the viewer doesn't have
installed fails silently: Desktop falls back to a default (usually Segoe
UI) with no error. If a theme specifies a non-default font, say so in the
summary comment and name the font(s) to install (most are free — e.g. any
Google Fonts family has downloadable desktop `.ttf`/`.otf` files) —
otherwise the person applying the theme will see working colors and wonder
why the typography "didn't take."

## How to apply a theme (until baking it into the PBIP is worth the risk)

Commit the theme as a plain `.json` file in the project folder (e.g.
`projects/<name>/<Name>Theme.json`) rather than wiring it into
`report.json`'s `customTheme`/`resourcePackages`. The human applies it
via *View → Themes → Browse for themes* in Desktop — a few clicks, and it
doesn't add another hand-authored PBIR structure on top of the report
layer, which is already this pipeline's least reliable part. Revisit
baking it in only once the report layer itself has a track record of
opening clean on the first try.
