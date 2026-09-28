# Device-local notes (this machine only)

Not part of the skill corpus — this file documents quirks of **this specific setup** so a future
session doesn't rediscover them. It is not installed as a skill and does not travel with the repo.

---

## Visual verification: this model cannot see images

The primary model on this device (`stealth/space-bunny-alpha`) has **no image input**. The
`read_image` tool exists but fails:

```
Error: cannot read "preview.png" as an image: model "stealth/space-bunny-alpha"
does not declare image input; switch to an image-capable model to read images
```

This matters because the Office-document skills in this repo end their delivery gates with a
**visual pass** — open the rendered file and judge it. That step is genuinely required: a deck can
pass `validate`, `view issues`, and `view outline` cleanly and still be visually wrong (overlapping
shapes, text running off-slide, a chart with unreadable colours, a table that renders as
`###`). Machine gates do not catch those.

**Do not silently skip the visual pass, and do not claim you did it.**

### The workaround: delegate to a multimodal subagent

Two worker models on this device **do** accept images, verified 2026-09-28 by having each read a
generated 4×4 red PNG and report its dimensions and colour correctly:

| Tool | Vision | Notes |
|---|---|---|
| `subagent_opencode` | **yes** | Confirmed working. Good default for visual QA. |
| `subagent_copilot` | **yes** | Confirmed working. Reads images and shells out to `sips`. |
| `subagent_kilo` | — | Failed with a transport error; not a vision answer. Unusable at time of writing. |
| `subagent_mistral` | — | Failed with a transport error; not a vision answer. Unusable at time of writing. |

`subagent_opencode` is the first thing to reach for. `subagent_copilot` is the fallback.

### The pattern

1. Render the artifact:
   ```bash
   officecli view out/deck.pptx screenshot -o out/preview.png --page 1-5
   officecli view out/deck.pptx screenshot -o out/contact.png --grid     # whole-doc thumbnails
   officecli view out/model.xlsx  screenshot -o out/sheets.png
   ```
2. Delegate the inspection — the subagent cannot see this conversation, so give it the absolute
   path and say explicitly that it must actually open the file:
   ```
   subagent_opencode:
   Read <absolute path> with your image-reading tool. Then judge it as a viewer:
   what does this slide show, does any text overflow or overlap, is anything
   unreadable or cut off, and would you send this to a client? If you cannot
   read images at all, say so plainly rather than guessing.
   ```
3. Act on the findings, re-render, and re-inspect. Repeat until it converges (three rounds is
   usually the ceiling).

### The rules that matter

- **Never report a visual pass you did not run.** If the subagents are unavailable or fail, say the
  visual pass is unverified. An honest "validated, but the visual pass is unverified — no image
  input on this model and no multimodal worker reachable" is a correct answer. A confident
  "I checked it and it looks good" when nothing looked at it is a lie that ships.
- **A subagent saying "this looks good" is a signal, not a verdict.** It is a separate model with
  its own blind spots. Weigh it, and keep the machine gates as well.
- **For text documents, you can substitute the HTML view** when no vision is available:
  ```bash
  officecli view out/doc.docx html      # then read the HTML directly
  officecli view out/doc.docx outline   # structure and headings
  ```
  This catches structure and content problems but **not** layout, contrast, or pagination.

---

## `jq` is not installed

Nine skills in `~/.dsh/skills` (`officecli-docx`, `officecli-pptx`, `officecli-xlsx`,
`officecli-pitch-deck`, `officecli-financial-model`, `officecli-academic-paper`,
`officecli-data-dashboard`, `officecli-word-form`, `morph-ppt`) use `jq` in their delivery gates.
Those gates will fail until it is installed:

```bash
brew install jq
```

The skills in **this** repo avoid `jq` entirely and use `python3` instead, so they are unaffected.

---

## `monid` sandbox quirk

`monid` writes config via XDG paths, which the sandbox denies under `~/.config`. Always run it as:

```bash
XDG_CONFIG_HOME="/Users/Mitesh Gada/Documents/Projects/.monid/xdg" monid ...
```

And note `/search` takes its body via `--query` while **`/fetch` takes it via `-i`** — passing
`--query` to `/fetch` returns `HTTP_400 body.urls: expected array, received undefined`.
