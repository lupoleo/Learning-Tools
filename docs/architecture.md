# aleph-recap architecture

## Pipeline and contracts

| Module | Layer | Input → output |
|---|---|---|
| `sources/academy.py`, `sources/base.py` | deterministic | URL / HTML / text → `Lesson` (course, title, sections) |
| `summarize.py` | probabilistic | `Lesson` → `LessonRecap` (structured output, schema in `models.py`) |
| `validate.py` | validation gate | `LessonRecap` + `Lesson` → accepted / rejected sections with reasons |
| `cli.py` | human decision | preview, explicit confirmation (or `--yes`) |
| `diagrams.py` | deterministic | `Diagram` spec → PNG |
| `docx_writer.py` | deterministic | sections + PNGs → Word file (add or replace, with backup) |

All data passed between stages is defined in `models.py` (pydantic). The model is asked for that exact schema, so its output is validated before any other code reads it.

## Decisions

### ADR-001 Diagrams are drawn locally from a spec, not generated as images
Claude Academy's "Visualize" diagrams exist only inside the Academy page and cannot be called through an API. Automating clicks on that page would tie the tool to one site and break on any interface change.
Claude therefore describes *what* to draw (kind, boxes, labels) and `diagrams.py` draws it with matplotlib in the Aleph palette. Three layouts cover most lesson content: `flow`, `cards`, `compare`.
Consequence: consistent, reproducible, offline rendering that works for any future source. The look differs from "Drawn by Claude".

### ADR-002 Every takeaway must be traceable to the source
Each section recap carries a `source_quote` that must appear verbatim (after normalising case, spaces and punctuation) in the matching section text. Sections that fail are rejected and listed in the preview, never written silently.
This catches invented content and wrong section mapping. It does not prove the takeaway is a *good* summary; that is what the human review step is for.

### ADR-003 Human confirmation before writing
The Word file is the user's own notes. The tool shows the recap and asks before writing; `--yes` exists for people who have already decided to trust it. A timestamped backup is made before every write.

### ADR-004 Model access behind one function
`summarize()` is the only place that talks to a model. The next version adds a local-model backend behind the same function and the same `LessonRecap` contract, so validation, diagrams and Word output do not change.

### ADR-005 Login through a persistent browser profile
Claude Academy requires a login. Instead of handling passwords, the tool opens a normal browser once (`aleph-recap login`) and reuses that profile, stored only on the user's machine.

## Known limits (v0.1)
- The Academy page structure is read generically (headings `h2`/`h3` inside `main`). If Academy changes its markup, use `--html` with a saved page while the reader is updated.
- Diagrams with very long labels are wrapped but can get crowded; the prompt asks for 2-5 word labels.
- Not yet tested against a live Academy page from CI (requires a login).
