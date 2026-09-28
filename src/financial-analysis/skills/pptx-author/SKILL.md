---
name: pptx-author
description: Build a .pptx deck as a file on disk using the officecli CLI — for pitch decks, tearsheets, IC presentations, client reports, and any FSI deliverable that is a PowerPoint. Covers slide structure, typed shapes, tables, charts, template mounting, and the pre-delivery visual QA pass. Use whenever a finance task must produce a .pptx rather than describe one.
---

# pptx-author

Build PowerPoint decks as **file artifacts** with `officecli`. This is the toolchain skill behind
`pitch-deck`, `teaser`, `cim-builder`, `strip-profile`, `morning-note`, `tear-sheet`,
`ic-memo`, and `deck-refresh`.

For the full officecli element vocabulary and the visual-design rules, load **`officecli-pptx`**
(and **`officecli-pitch-deck`** for investor decks specifically). This skill is the FSI layer:
deck structure, financial-data discipline, and QA.

## Output contract

- Write to `./out/<name>.pptx`. Create `./out/` if missing.
- Return the relative path in your final message.
- **No external sends.** This skill writes a file; it never emails, uploads, or shares.

## Build loop

```bash
mkdir -p out
officecli create out/deck.pptx --force
officecli batch out/deck.pptx --commands "$(cat batch.json)"
officecli close out/deck.pptx
```

Batch again — a deck is many shapes, and batch is atomic so a bad item rolls back rather than
half-building the deck.

### Mounting a firm template

`create` has no `--template` flag — **copy the template and edit the copy**, which preserves its
theme, masters, and layouts:

```bash
cp ./templates/firm-template.pptx out/deck.pptx
officecli query out/deck.pptx "slidelayout"      # the template's REAL layout names
officecli close out/deck.pptx                    # release the original before editing in place
```

Never guess layout names — they differ per template. List them, then reference one:
`--prop layout="Title and Content"`.

Note `layout=` is **metadata only**: it does not materialize that layout's placeholder slots. Pass
`--prop title=` / `--prop text=` (or add a `placeholder` explicitly) to actually create the shapes.

## Slide anatomy

```bash
officecli add out/deck.pptx / --type slide --prop title="Valuation Summary" --prop text="EV bridge to equity value"
officecli add out/deck.pptx /slide[1] --type shape \
  --prop text="Implied share price $142.30, 18% upside" \
  --prop x=1cm --prop y=12cm --prop w=20cm --prop h=2cm \
  --prop fill=1F4E79 --prop color=FFFFFF --prop size=14
```

`--prop title=` and `--prop text=` on a slide auto-emit the title and body placeholders. To add
shapes explicitly, target `/slide[N]`. On pptx, `color=` unambiguously means **text** color — there is
no cell-style ambiguity like there is on xlsx.

For anything beyond a slide + text shape — tables, charts, pictures, geometry — check
`officecli help pptx <element>` first.

## Conventions

### One idea per slide

The title is the **takeaway**, not the topic. "Implied share price $142, 18% upside" beats "Valuation
Summary". The body exists to support that sentence. A slide whose title only labels its section is a
slide with no argument.

### Every number traces to the model

If a figure comes from a workbook, footnote the sheet and cell: `(DCF!B34)`. A number in a deck that
nobody can trace back is the single most common way these decks get sent back. Build the deck
**from** the model, not from a copy-paste of its screen.

### Tables for financials, charts for trends

- Multi-period financials (P&L, comps table, sources & uses) → **table**, not a chart. The reader
  wants the digits.
- A single trend over time (revenue build, margin path, share price) → **chart**.
- Never present a 2×2 or a stacked bar where a table is the honest form.

```bash
officecli add out/deck.pptx /slide[3] --type table --prop rows=6 --prop cols=4
```

`dataRange` is xlsx-only — a pptx chart embeds its data and has no host worksheet to reference. For
a deck chart, feed the series inline (see `officecli help pptx chart`).

### Reading a number off a model

```bash
officecli get out/model.xlsx /DCF/B34      # exact value the model computes
```

Do not retype a number you read off a screen, and do not let a chart image stand in for a number the
reader is expected to verify.

## Pre-delivery QA

**Do not ship an unviewed deck.** Render and actually look at it:

```bash
officecli view out/deck.pptx issues           # low contrast, distorted pictures, empty fields
officecli view out/deck.pptx outline          # title per slide — read the argument back
officecli view out/deck.pptx screenshot -o out/preview.png --page 1-3
```

`view issues` catches `low_contrast` (text that won't survive a projector), `picture_aspect_distorted`,
and `slide_field_not_evaluated` (empty slide numbers or dates). Then read `outline` — if the titles
in sequence don't form a coherent argument, the deck isn't done, no matter how it renders.

For deck-specific judgment — the visual floor, grid, palette discipline, connector canon, and the
Deliv checklist — load **`officecli-pitch-deck`**.

### The visual pass is a real step — do it, or say you didn't

`issues` and `outline` do **not** catch overlapping shapes, text running off-slide, unreadable
colours, or a slide that simply looks wrong. Those need someone to look at the render.

**If your model cannot accept images, delegate the look to a multimodal subagent** rather than
skipping the step. Give it the absolute path and tell it to open the file:

```
Read /abs/path/out/preview.png with your image-reading tool. Judge it as a viewer:
what does this show, does any text overflow or overlap, is anything unreadable or
cut off? If you cannot read images at all, say so plainly rather than guessing.
```

Then act on what it reports and re-render.

**If no vision is available at all — yours or a subagent's — say so in your final message.** Write
"validated and issue-free; the visual pass is unverified because this model has no image input and
no multimodal worker was reachable". Never report a visual pass that did not happen: a deck that
passes every machine gate and still renders badly is exactly the failure this step exists to catch.

## Common failures

| Error | Cause |
|---|---|
| `File already exists` | `create --force`, or `rm` first |
| Placeholder text shows empty | `layout=` is metadata only — pass `title=` / `text=` to materialize slots |
| Layout name not found | template's layouts differ; `officecli help pptx slide` to list them |
| Body text on one line | `\n` = new paragraph, `\v` = line break within one |
| Chart has no data | pptx charts embed data inline; xlsx `dataRange=` does not apply |
| Deck not flushed | `officecli close` before PowerPoint or a converter opens it |
