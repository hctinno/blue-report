# blue-report agent instructions

## Purpose

This repository is the HCT shared presentation design system, called **Blue Report**. One source produces HTML, PDF, PowerPoint, and DOCX output, and the rules are enforced by a script rather than by eye.

`docs/CODEX_DECK_PROMPT.md` is the entrypoint for agents that cannot load `.claude/skills/`. **Read it before starting deck, document, or board work**; it routes to the canonical skill, business intake and visual selection instructions. The rules below are its summary.

`docs/AGENT_WIRING.md` explains how to reach this repository from an agent session that started somewhere else.

## Business intake and visual direction

For new presentation work, follow `.claude/skills/blue-report/SKILL.md` first.
Clarify the business purpose, audience, delivery, content, output format, length and motion preferences.
Render cover and body samples of the same content into actual PNGs, explain the differences,
and get a style choice or explicit delegation before producing the full deck.
See `references/business-presentation-intake.md` and `references/visual-style-selection.md` inside the skill.
Template routing does not bypass these content and style decisions. Preserve an already chosen style for targeted edits.

## What is in here

Four separate lineages. They are not interchangeable: different page size, different type scale, different checker.

| Lineage | Page | Token prefix | Type floor | Checker |
|---|---|---|---|---|
| Slide decks | exactly 1920x1080 | `--br-fs-*` | 24px | `check_deck.py` — 17 items |
| A4 documents | 794x1123 portrait (1123x794 landscape) | `--bd-fs-*` | 14px (10.5pt) | `check_doc.py` — 9 items |
| Web boards | no fixed page; reflows with viewport | `--bw-fs-*` | 12.5px | `check_board.py` — 11 items |
| Live decks | no fixed page; 100dvh per slide, 16:9 rem scaling | `--bl-fs-*` | body 1.0rem · note 0.78rem | `check_live.py` — 27 items |

### Templates to choose from — 4, in `.claude/skills/blue-report/assets/`

| What you are making | `--deck` name | File | Lineage |
|---|---|---|---|
| any report or presentation (default) | `standard` | `live-standard.html` | live deck |
| a component the standard deck lacks — copy the whole slide | `livecatalog` | `live-catalog.html` | live deck parts catalog (51 slides) |
| meeting minutes (printed A4) | `minutes` | `doc-minutes.html` | A4 document |
| a dashboard people change on screen | `manage` | `board-manage.html` | web board |

**Every report or presentation is built from the standard deck** — executive reports, weekly
reports, strategy reports, decision requests, Q&A and appendices included. Those slide types are all
in the standard deck and the parts catalog. Route the output family from the request without repeating known facts: minutes → `minutes`,
dashboard / status board → `manage`, everything else → `standard`.

### Archived templates — `assets/archive/`

Removed from the menu, still buildable by name and still checked. **Use one only when the user names
it, or when a `.pptx` file is required.** Never pick one on your own.

| Group | `--deck` names | Note |
|---|---|---|
| fixed-page decks 1920x1080 — 12 | `internal` · `weekly` · `ax` · `team` · `exec` · `allhands` · `sales` · `project` · `training` · `strategy` · `report` · `catalog` (19 layouts) | source for the PPTX build (`pptx/`) |
| A4 documents — 3 | `policy` · `manual` · `notice` | |
| web boards — 4 | `board` · `execboard` · `teamboard` · `gapcheck` | |
| live briefing | `live` | a smaller standard deck |
| FCC/KC reports — 14 | `assets/archive/fcc-kc/` | certification test reports only |

Archived files load their CSS and viewer as `../`. Do not copy them by hand — build with `apply_brand.py`,
which fixes the paths in the output.

### Live decks — the house standard and the parts catalog

**Start every new report from `live-standard.html` (`--deck standard`).** It is the canonical
starting point: copy it and replace the content. Do not compose a deck from scratch and do not
invent chrome — the house look lives in this file and in `blue-live.css`.

Same purpose as a slide deck, different mechanics. No fixed page: one slide is `100dvh`, the root
font-size follows the viewport (`clamp(10.5px, min(1vw, 1.78vh), 20px)` — `1.78vh` is 16:9), and every
dimension inside is `rem`. Vertical scroll is review mode; one axis flip makes it a horizontal
presentation. It reads fine with JavaScript disabled — just scroll.

| File | `--deck` name | Purpose |
|---|---|---|
| `live-standard.html` | `standard` | **house standard — start here.** 15 slides: cover, agenda, gist, chapter dividers, body, roadmap, decision, closing, appendix divider, Q&A, glossary |
| `live-catalog.html` | `livecatalog` | **parts catalog, 51 slides.** 38 components, 12 animation families, widgets, evidence/document/video overlays, 135 icons — one slide per component |

**Need a component the standard deck does not have** (Gantt, org chart, role matrix, donut, stacked
or waterfall bars, heat map, flow diagram, pipeline, screen mock-up, tabs, scenes, route map,
simulation, evidence/document/video overlay)? Copy **the whole slide** from `live-catalog.html` into
your deck and replace its content. Each catalog slide names its component and code in the top rail
(C01, T03, …). Do not invent class names — a class that is not in `blue-live.css` does nothing.
The component index, widget attributes, data formats (evidence JSON, stacked-bar JSON, document,
video), speaker-note syntax and keyboard map (PowerPoint slide-show keys: F5, Shift+F5, Alt+F5, B/W, P pen,
Ctrl+I/E, F1; overridable with `<script type="application/json" id="bl-keys">`) are in `.claude/skills/blue-report/README.md`, chapter
「6-3. 라이브 덱」.

Colour comes from `data-c="1"…"6" | navy | ok | warn | alert | mute`, never an inline colour.
Text below 1.0rem is allowed only on the label classes (`.bl-lbl`, `.bl-cap`, `.bl-mini`, `.bl-axis`,
`.bl-dl`, `.bl-leg`, `.bl-num`, `.bl-pill`, `.bl-badge`, `.bl-delta`, `.bl-asof`, `.bl-pgref`,
`.bl-stamp`, `.bl-conf`, `.bl-seg`). Build donuts with `scripts/donut.py --live`. Icons are
`<i class="bl-i bl-i--name">` from the 135 names in `scripts/make_icons.py`.

Bundle the finished deck with `apply_brand.py --brand <brand.json> --deck <file> --title "Deck title" --single-file -o out.html`.
Without `--title`, the `docTitle` in brand.json replaces the deck title in every footer. Then run
`check_live.py out.html --shots out/` (27 items) and page through the per-slide PNGs. To preview a working
copy before bundling, put `blue-report.css`, `blue-live.css`, `live-viewer.js` and `fonts/` next to it.
Every slide must fit one 16:9 screen — check item 27 fails a slide whose body runs under the footer.

**Page chrome is mandatory, not decorative.** Every slide carries all of it, and `check_live.py`
fails the deck when any piece is missing:

| Part | Markup | What it holds |
|---|---|---|
| Top rail | `<header class="bl-hd">` | `<span class="bl-code"><b>NN</b>section</span>` + `.bl-sp` + `.br-mark` |
| Bottom rail | `<footer class="bl-rf">` | `.bl-rf-name` (deck title) + `.bl-pg` (page) |
| Watermark | `<div class="br-watermark" data-on="…">` | brand logotype, bottom-right, faint |
| Progress line | `<div id="bl-prog">` | one per deck, before `<main>` |

`apply_brand.py` fills both `.br-mark` and `.br-watermark` from `brand.json`, so leave the
placeholder markup exactly as the standard deck has it.

The `data-on` value is the **opposite** of the slide for the rail mark, because the mark sits on the
rail and the rail colour is the opposite of the page:

| Slide | Rail | Rail mark | Watermark |
|---|---|---|---|
| light (default) | dark | `data-on="dark"` | `data-on="light"` |
| dark (`bl-sl--dark`) | white | `data-on="light"` | `data-on="dark"` |

Write dimensions in `rem`, never `px` — `check_live.py` rejects literal px in `bl-` rules. The three
exceptions are 1px borders, the scaling engine's own `clamp`, and blur/shadow radii.

Put the key phrase of a title inside `<em>` — the highlight band is drawn there and nowhere else.

### FCC/KC certification reports — 14

Separate family under the same design system. See `docs/FCC_KC_REPORT_TEMPLATE_SYSTEM.md` and its integration guide. `verify_repo.py` checks them with the A4 rules.

## Working rules

- Work in the current checkout root. Paths here are relative to it — never assume a specific drive or directory.
- Read `.claude/skills/blue-report/README.md` first. It is the self-contained spec: color tokens, type scale, spacing, chart rules, and writing style. `.claude/skills/blue-report/references/rules.md` is the condensed rule list.
- Start from a finished asset above, replacing content only. Preserve house tokens and chrome; compare the supported content-layout directions before full production.
- Ask the user which purpose applies before choosing when the request does not make it obvious. Deck, A4 document, board, and live deck are four different answers — do not guess between them. When the request is simply "a report" or "a deck" with no further constraint, the answer is the live standard deck.
- Example figures, department names, and wording in the assets are usage samples, not placeholders. Replace them with real content.
- Hard rules: use `--br-*` CSS custom properties only and add no raw hex; donut charts only, never pie, and generate them with `scripts/donut.py` rather than computing angles by hand; Korean copy in 개조식 (noun-ending) form — neither polite endings (`~합니다`) nor plain declaratives (`~한다`, `~없다`); speaker notes in `data-notes` are exempt; slides are exactly 1920x1080; no slide text below 24px; data marks keep at least 2:1 contrast against the backdrop they actually sit on; the brand mark stays in the top-right margin band and body content never intrudes there.
- Write output to `decks-out/`, which is gitignored. Do not scatter result files in the checkout root.
- Save Korean text as UTF-8 and treat mojibake patterns such as `???`, `濡`, `湲`, `遺`, `媛`, `李` as blocking corruption.
- Preserve user changes. Inspect `git status` before editing.
- Do not commit, push, reset, or delete branches unless the user explicitly requests it.
- Never print or store API keys, tokens, cookies, or passwords.

## Generators and checks

Python and Node only — no Claude Code dependency. Use `python3` on macOS and Linux.

```bash
# Whole-repository check. Required after changing templates, scripts, or docs.
# CI runs exactly this on every push and pull request.
python scripts/verify_repo.py

# Per-artefact checks. Required before reporting the work complete.
python .claude/skills/blue-report/scripts/check_deck.py  decks-out/deck.html
python .claude/skills/blue-report/scripts/check_doc.py   decks-out/doc.html
python .claude/skills/blue-report/scripts/check_board.py decks-out/board.html
python .claude/skills/blue-report/scripts/check_live.py  decks-out/live.html

# Build. --deck takes any name from the four tables above.
python .claude/skills/blue-report/scripts/apply_brand.py --brand brand/hct/brand.json --deck internal --single-file -o decks-out/deck.html
python .claude/skills/blue-report/scripts/to_pdf.py decks-out/deck.html
node   .claude/skills/blue-report/pptx/build.js --brand brand/hct/brand.json --out decks-out
```

`build_single_file.py` bundles decks and A4 documents only — it takes neither a board nor a live name, because both have their own structure (boards have no viewer; live decks use `.bl-sl` and `live-viewer.js`). Bundle either with `apply_brand.py --single-file` instead.

Progressive reveal works in every deck: put `data-f="1"`, `"2"`, … on elements and they open one step
at a time **in presentation mode only**. Review mode always shows everything, so a deck never looks
empty when opened. The deck viewer also has a laser pointer (`L`), a presenter script window (`S`),
number-then-Enter jump, and a control bar that appears only at the very bottom edge while presenting.

`check_deck.py` enforces 17 rules mechanically: banned sentence endings, pie charts, donut dasharray arithmetic, off-token hex, slide size, body-region overlap between stacked siblings, minimum font size, 2:1 contrast for data marks, resolvable mark colors, body safe area, leader-line annotations, bar-length arithmetic, brand-mark presence, watermark placement, mark/body overlap, watermark asset distinctness, and logo variant against background luminance. Its report is the completion evidence — a run with failures is not "done".

`check_board.py` additionally re-checks the **rendered** DOM for banned endings, because board content often lives in JavaScript data that a source scan cannot see.

`verify_repo.py` builds the decks and runs `check_deck.py` on each, checks the A4 documents with `check_doc.py` and the boards with `check_board.py` (archived ones included), checks the three live decks and their branded outputs with `check_live.py`, presses through the live engine (paging, steps, page-number jump, present mode, laser, overlays, evidence tabs, document, video, tabs, presenter popup and its in-page fallback — 40 checks on the catalog source and its single-file output), checks the FCC/KC templates with the A4 rules, builds the PPTX files, re-derives `dist/` and compares it against what is committed, scans Korean text for mojibake, validates the plugin manifests, compares HTML and `pptx/content.js` for drift, and verifies the skill version was bumped when the skill folder changed. It exits 1 if anything fails. `.github/workflows/verify.yml` runs the same single command, so local and CI results cannot diverge.

If you change `assets/`, rebuild `dist/` and commit it: `build_single_file.py` three times —
once with no arguments, once with `--artifact --brand brand/hct/brand.json`, and once with
`--artifact --brand brand/hct/brand.json --deck minutes` for the A4 document. The dist check
fails otherwise.

PPTX content lives separately in `pptx/content.js`. The HTML decks are the source of truth, so change both when content changes. Colors cannot drift because `pptx/tokens.js` parses `assets/blue-report.css`.

The two content sources are deliberately not merged: hand-editing the HTML decks is how this system is used, and generating the HTML from data would remove that. Drift is caught mechanically instead — `scripts/check_content_sync.py` compares slide counts, deck titles, speaker notes, bar names and values, donut legends, and table headers and rows across both sources, and names the deck, slide, and field that diverged. `verify_repo.py` and CI run it, so changing only one side does not pass.

## Reporting

Write reports in Korean. Include the commands you ran, the pass/warn/fail counts from the checker you used, and the output paths. If you did not run the check, say so — do not write "완료" without it.
