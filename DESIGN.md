# COLE: design contract

Status: draft to validate (palette decided). Date: 2026-11-26. Product framing: `PRODUCT.md` and
`docs/produit/cadrage-site-statique.md`. Direction sheet: `.taste-skill/direction.json`
(seed 436372402, reprint with `node <skill>/scripts/draw.mjs --show`; the folder is git-ignored).

Precedence: owner > this file > ux-engine skill defaults. COLE is a GRAAL research
project, not a Baseline product: the Baseline design system does not apply.

## Direction: "The printed annual"

The site reads like a well-edited printed scientific report: a masthead, a tight
oversized title, text held to a strict column line, colour used in solid blocks the
way a two-colour print job would.

**Idea.** On this page, the three reading levels become the three formats of one
publication: the poster (level 1, plain language), the data sheet with its radar
plate (level 2, practitioners), the paper (level 3, scientific). The visitor picks
a format, not a difficulty.

**Live thing.** "Compare two models": pick two models, see their radar plates
overlaid by task category with one sentence stating the main difference. It uses the
real results, works with a thumb, and has a plain table fallback without script.

## Layout

- One vertical axis at about 42 percent of the viewport width. Headings start on it,
  body columns hang from it. The 0 to 42 percent zone holds notes or figures, or
  stays empty. On a phone the axis collapses to the left margin and notes move
  inline above their paragraph.
- Hero ("narrow talk, wide headline"): narrow left column (wordmark, one supporting
  sentence at 22px, one action), wide right column with a two-line headline in the
  heaviest weight, then a square-cornered picture cropped by the bottom edge, with an
  accent block carrying one real figure overlapping its corner.
- Sections alternate text pages (title on the axis, body in one or two columns of 34
  to 40ch) and full-bleed colour pages with one large figure or radar plate.
- One pair of equal outer margins at every width; no stretch of page taller than
  about half a screen with nothing in it; 120 to 240px between sections.
- One button shape (square corners), one radius, one pair of margins for the whole site.

## Type

Schibsted Grotesk only, loaded with `font-display: swap`.

- Display: weight 800, tracking -0.05em, leading 0.88, sentence case.
- Text: 400 for paragraphs, 600 for navigation and functional text, leading 1.4,
  tracking -0.01em. Running text is 16px or more in the full ink; nothing under 13px.
- Five steps maximum: `--step-small` 0.8125 to 0.875rem, `--step-body` 1.0625 to
  1.1875rem, `--step-lead` 1.25 to 1.625rem, `--step-head` 2 to 4rem, plus the hero
  display size (clamp(88px, 9.8vw, 150px) on desktop, 15vw on a phone).
- Headlines are two lines or fewer at every width. Numbers in tables use tabular
  figures; the table shows bare numbers and the unit "(%)" sits in the column header.
- Number format: one decimal in tables, two decimals on level 3 (scientific) pages,
  matching the paper.

## Colour

Decision (owner, 2026-11-26): Quebec blue and white, with a single warm accent for
the action. The dealt soot and lime palette is dropped. These hex values are our
own choices (not an official flag or institutional specification); contrast ratios
below were computed, not estimated.

```css
:root {
  --bg: #ffffff;            /* page ground */
  --tint: #e8eef8;          /* quiet surface step, never a line */
  --ink: #101a2b;           /* running text */
  --muted: #4a5568;         /* secondary text */
  --blue: #1d4a9a;          /* field colour and links */
  --deep: #0b2a5c;          /* opening and closing fields */
  --accent: #f2a900;        /* the single action colour */
  --accent-ink: #101a2b;
  --placeholder: #5a6475;
}
```

Roles and measured contrast (WCAG ratio):

| Pair | Ratio |
|---|---|
| `--ink` on `--bg` | 17.43 |
| `--muted` on `--bg` | 7.53 |
| `--muted` on `--tint` | 6.46 |
| `--ink` on `--tint` | 14.96 |
| white on `--blue` | 8.41 |
| `--blue` on `--bg` (links) | 8.41 |
| white on `--deep` | 14.00 |
| `--accent` on `--deep` | 6.97 |
| `--accent-ink` on `--accent` (buttons) | 8.68 |
| `--placeholder` on `--bg` | 5.98 |

Proportions: white ground with `--ink` text; the opening and closing sections are
full-bleed `--deep`; middle "colour pages" are one flat `--blue` or `--tint` field;
the accent appears on the primary action only (and at most one headline on a deep
ground). Surfaces separate by a step in tone, never by a line or a shadow. Radar
series use `--ink` and `--blue` on light fields, white and `--accent` on deep
fields, at most two series per plate. This is a page composition, not a dark theme:
there is still no dark mode toggle (non-objective of the framing).

## Data visualisation

- Charts live inside a root marked `data-chart`. Radar plates: two series at most per
  plate (ink and accent on a field), direct labels on axes, no rainbow, no gradient,
  no 3D, no invented numbers.
- Every chart has a keyboard-reachable table alternative with the same values
  (accessibility requirement of the framing).
- The leaderboard keeps real table semantics (th scope, aria-sort, sticky rank and
  model columns); numbers right-aligned in tabular figures; no row stripes drawn
  with lines, use tone steps.

## Imagery

No project photographs exist. Order of preference: (1) real pictures of the subject's
world from open collections, credited in the footer (Quebec City and Laval archives,
old maps, engravings of language and typography, museum objects), searched with
`scripts/assets.mjs`; (2) drawings made in code in one flat language in the page
palette (radar plates are the page's own pictures); (3) the dealt "People" set only
as honest atmosphere. At least four real pictures on the page. One treatment for all
pictures (greyscale with `grayscale(1) contrast(1.05)`, or all colour; not mixed).
Never claim a found picture as the project's own.

## Components

- Navigation: wordmark, four to five plain links (Leaderboard, Choose a model,
  Methodology, Papers, Contact), the language switch EN/FR, no chrome. No floating
  pill, no glass. Hit areas 44px.
- Contact for model-evaluation requests: a button (no email address shown) and a
  GitHub issue template link. No submission form.
- Cards: avoid; lists use the "cards that fold into spines" pattern only on desktop,
  stacked text cards on a phone.
- FAQ: answers as reading text in two columns (no accordion).
- Footer: the name first at full width, places and links under it; no crop of letters
  along their top edge (inspector fails it): crop at the bottom or a side.

## Motion

Signature move: masked headline (each hero line rises from behind its own baseline,
about 900ms, second line +110ms). Entrances per section part, staggered 60 to 90ms,
once. Feedback on every control. Transform and opacity only. Every move has a
`prefers-reduced-motion` variant that keeps the content and drops the travel. Tokens
and recipes: `ux-engine-plus:motion-design` and the skill's `references/motion.md`.

## Accessibility and i18n

EN and FR at parity (`translation.json` keys in English). `<html lang>` follows the
chosen language; document titles localised. Focus visible on every control (white
ring on dark and accent grounds, ink ring on light). Colour is never the only signal.

## Declared exceptions (WARN kept with a reason)

- The deep-blue opening and closing sections: part of the dealt composition (the
  printed annual's bracket pages), not a dark theme.
- Tabular and chart borders: real tables and chart axes may use lines.

## Open points for the owner

1. Photography plan: who supplies or approves the found pictures, and the credit line.
2. Wordmark: COLE set in the display face for now; a logo is out of scope.
