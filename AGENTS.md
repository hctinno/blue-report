# blue-report agent instructions

## Purpose

This repository is the HCT shared presentation design system, called **Blue Report**. One source produces HTML, PDF, PowerPoint, and DOCX output, and the rules are enforced by a script rather than by eye.

`docs/CODEX_DECK_PROMPT.md` is the full step-by-step work order, written for agents that cannot load `.claude/skills/`. **Read it before starting any deck, document, or board work** — it carries the complete asset tables with their `--deck` names. The rules below are its summary.

`docs/AGENT_WIRING.md` explains how to reach this repository from an agent session that started somewhere else.

## What is in here

Four separate lineages. They are not interchangeable: different page size, different type scale, different checker.

| Lineage | Page | Token prefix | Type floor | Checker |
|---|---|---|---|---|
| Slide decks | exactly 1920x1080 | `--br-fs-*` | 24px | `check_deck.py` — 17 items |
| A4 documents | 794x1123 portrait (1123x794 landscape) | `--bd-fs-*` | 14px (10.5pt) | `check_doc.py` — 9 items |
| Web boards | no fixed page; reflows with viewport | `--bw-fs-*` | 12.5px | `check_board.py` — 11 items |
| Live decks | no fixed page; 100dvh per slide, 16:9 rem scaling | `--bl-fs-*` | body 1.0rem · note 0.78rem | `check_live.py` — 16 items |

### Slide decks — 12, in `.claude/skills/blue-report/assets/`

| File | `--deck` name | Purpose | Slides |
|---|---|---|---|
| `deck-internal-report.html` | `internal` | internal monthly reporting | 9 |
| `deck-weekly-report.html` | `weekly` | organisation-wide weekly reporting | 7 |
| `deck-ax-weekly.html` | `ax` | one-page report for senior management, appendix behind it | 5 |
| `deck-team-weekly.html` | `team` | compressed team weekly, for a team lead | 2 |
| `deck-exec-report.html` | `exec` | executive reporting, conclusion first | 6 |
| `deck-allhands.html` | `allhands` | all-hands / townhall | 9 |
| `deck-sales-proposal.html` | `sales` | external proposal and sales | 10 |
| `deck-project-report.html` | `project` | project kickoff and completion | 9 |
| `deck-training.html` | `training` | training and technical explanation | 8 |
| `deck-strategy-report.html` | `strategy` | strategy reporting, argument form, asks for a decision | 16 |
| `deck-report.html` | `report` | high-density reporting, diagram-led | 19 |
| `deck-template.html` | `catalog` | catalog of all 19 layouts | 19 |

### A4 documents — 4

| File | `--deck` name | Purpose | Pages |
|---|---|---|---|
| `doc-minutes.html` | `minutes` | meeting minutes | 4 |
| `doc-policy.html` | `policy` | company rules and regulations | 6 |
| `doc-manual.html` | `manual` | manual and guide | 6 |
| `doc-notice.html` | `notice` | notice, complete in one page | 2 |

### Web boards — 5

Use these when the artefact is something people **change on screen**, not something they read. Boards load `blue-report.css` and `blue-web.css` together. They are not PPTX or PDF targets.

| File | `--deck` name | Purpose |
|---|---|---|
| `board-task.html` | `board` | task execution board — rail, KPI, filter table, memo (smallest sample) |
| `board-manage.html` | `manage` | management dashboard — 12 sections, 8 tables |
| `board-exec.html` | `execboard` | execution board — status pill per item, memo |
| `board-team.html` | `teamboard` | team board — 4-column kanban |
| `board-gap.html` | `gapcheck` | gap-check board — gap parent with response children |

### Live decks — 2, one of them the house standard

**Start every new report from `live-standard.html` (`--deck standard`).** It is the canonical
starting point: copy it and replace the content. Do not compose a deck from scratch and do not
invent chrome — the house look lives in this file and in `blue-live.css`.

Same purpose as a slide deck, different mechanics. No fixed page: one slide is `100dvh`, the root
font-size follows the viewport (`clamp(10.5px, min(1vw, 1.78vh), 20px)` — `1.78vh` is 16:9), and every
dimension inside is `rem`. Vertical scroll is review mode; one axis flip makes it a horizontal
presentation. It reads fine with JavaScript disabled — just scroll.

| File | `--deck` name | Purpose |
|---|---|---|
| `live-standard.html` | `standard` | **house standard — start here.** 12 slides of layout vocabulary |
| `live-brief.html` | `live` | live briefing — short-form sample |

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
- Start from a finished asset above, replacing content only. Do not invent a new visual style.
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

`verify_repo.py` builds the decks and runs `check_deck.py` on each, checks the four A4 documents with `check_doc.py`, checks the five boards with `check_board.py`, checks both live decks with `check_live.py`, checks the FCC/KC templates with the A4 rules, builds the PPTX files, re-derives `dist/` and compares it against what is committed, scans Korean text for mojibake, validates the plugin manifests, compares HTML and `pptx/content.js` for drift, and verifies the skill version was bumped when the skill folder changed. It exits 1 if anything fails. `.github/workflows/verify.yml` runs the same single command, so local and CI results cannot diverge.

If you change `assets/`, rebuild `dist/` and commit it: `build_single_file.py` three times —
once with no arguments, once with `--artifact --brand brand/hct/brand.json`, and once with
`--artifact --brand brand/hct/brand.json --deck minutes` for the A4 document. The dist check
fails otherwise.

PPTX content lives separately in `pptx/content.js`. The HTML decks are the source of truth, so change both when content changes. Colors cannot drift because `pptx/tokens.js` parses `assets/blue-report.css`.

The two content sources are deliberately not merged: hand-editing the HTML decks is how this system is used, and generating the HTML from data would remove that. Drift is caught mechanically instead — `scripts/check_content_sync.py` compares slide counts, deck titles, speaker notes, bar names and values, donut legends, and table headers and rows across both sources, and names the deck, slide, and field that diverged. `verify_repo.py` and CI run it, so changing only one side does not pass.

## Reporting

Write reports in Korean. Include the commands you ran, the pass/warn/fail counts from the checker you used, and the output paths. If you did not run the check, say so — do not write "완료" without it.
