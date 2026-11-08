# Learning-Tools

Small, open tools from **[Aleph Innovation](https://www.alephinnovation.com)** that help people learn faster and keep what they learn.

## aleph-recap

`aleph-recap` turns an online lesson into a **short, visual Word recap** that you can read offline in a minute.
You finish a lesson, run one command, and the lesson appears in your notes as:

- one heading per section of the lesson,
- one plain sentence with the key idea,
- one simple diagram (steps, concept cards or a side-by-side comparison).

No more copying and pasting from the browser into Word while you are trying to study.

> **Version 0.1 scope.** This first version supports **Claude Academy** (`academy.claude.com`) as a source and uses the **Claude API** for the summaries.
> New versions will add **local models** (for example through Ollama on your own machine, so no lesson text leaves your computer)
> and **more sources** beyond Claude Academy (other course platforms, saved web pages, video transcripts). See the [roadmap](#roadmap).

### How it works

The tool follows the Aleph approach: the AI is one component inside an engineered, testable system, and a person always makes the final decision.

```
READ  →  SUMMARISE  →  VALIDATE  →  REVIEW  →  WRITE
```

| Step | Layer | What happens |
|---|---|---|
| Read | deterministic | Opens the lesson with your own logged-in browser profile and splits it into sections. |
| Summarise | probabilistic (Claude) | Returns a fixed JSON structure: per section a takeaway, a supporting quote, and a diagram description. |
| Validate | deterministic gate | Every takeaway must cite a passage that really exists in that section. Anything that cannot be traced to the source is rejected and shown to you. |
| Review | human decision | You see the recap in the terminal and confirm before anything is written. |
| Write | deterministic | Diagrams are drawn locally (same style every time) and the lesson is added to the Word file. Running it again on the same lesson replaces it instead of duplicating it. A backup of the Word file is made first. |

More detail in [docs/architecture.md](docs/architecture.md).

### Install (Windows, macOS, Linux)

Requires Python 3.10 or newer.

```bash
pip install git+https://github.com/lupoleo/Learning-Tools.git
playwright install chromium
```

Set your Claude API key (from <https://platform.claude.com>):

```powershell
# Windows PowerShell
setx ANTHROPIC_API_KEY "sk-ant-..."
```
```bash
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Use

Sign in to Claude Academy once. A browser window opens; log in, then close it. The session is kept in `~/.aleph-recap/browser-profile` on your computer only.

```bash
aleph-recap login
```

After each lesson:

```bash
aleph-recap add https://academy.claude.com/courses/claude-101/your-first-conversation-with-claude --number 2 --doc "Claude Academy.docx"
```

The course name (`Claude 101`) is taken from the URL; `--number 2` gives the heading `Lesson 2 <title>`.
Close the Word file before running the command (Word and OneDrive lock open files).

Other options:

| Option | Purpose |
|---|---|
| `--html page.html` | Use a page you saved from the browser instead of opening the URL. |
| `--text notes.md --title "..."` | Use plain text or Markdown (`#` lines start sections). |
| `--course "Claude 101"` | Set the course name (Heading 1) yourself. |
| `--model <id>` | Claude model (default `claude-opus-5-5`, or `ALEPH_RECAP_MODEL`). |
| `--yes` | Skip the confirmation step. |

**Cost.** One lesson is one API call; with the default model this is typically a few cents.

**Your notes, your use.** The recaps are personal study notes. Course content belongs to its authors: each user generates their own recaps, and the tool never shares or uploads them anywhere.

### Word layout

```
Title       Course notes
Heading 1   Claude 101
Heading 2   Lesson 2 Your first conversation with Claude
Heading 3   <section>
            <one-sentence takeaway>
            <diagram, full page width>
```

This matches notes written by hand, so you can mix both in the same file.

### Roadmap

| Version | What is planned |
|---|---|
| 0.1 (this) | Claude Academy source, Claude API, validated recaps, Aleph-style diagrams, Word output. |
| next | **Local models** (Ollama or the future Aleph server) behind the same interface, so recaps can run fully offline and no text leaves the machine. |
| next | **More sources**: other course platforms, saved web pages, PDFs, YouTube and video transcripts. |
| later | Export to Markdown and PDF; Italian and English output; workshop mode for Aleph training sessions. |

Ideas and issues are welcome in GitHub Issues. Decisions, tests and failures are documented in the open, as part of the work.

### Develop

```bash
pip install -e ".[dev]"
pytest
```

The tests run without network access or an API key (the Claude call is replaced by a fixed response).

## Licence

MIT. See [LICENSE](LICENSE).
