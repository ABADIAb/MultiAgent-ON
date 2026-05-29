---
name: pdf-ingest
description: >
  High-fidelity PDF to Markdown extraction using pymupdf4llm.
  Trigger: extract pdf, ingest pdf, pdf to markdown, pdf to md
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- When adding a new source (paper, transcript, manual) to `docs/LLM_Wiki/raw/`.
- When raw text extraction from a PDF is needed for further analysis.
- To preserve tables and document structure in a format readable by LLMs.

## Critical Patterns

- **Format Preservation**: Always use `pymupdf4llm` to ensure headers and tables are correctly converted to Markdown.
- **MS Teams Transcriptions Protocol**: The `extract_pdf.py` script automatically detects MS Teams transcriptions and runs a built-in regex cleaner to remove OCR junk (like `picture intentionally omitted`), auto-generate the YAML frontmatter, and correctly format speaker tags as `**Speaker Name** [M:SS]:\n> spoken text`. If you are manually editing a transcript, ensure it strictly follows this layout.
- **Raw Storage**: The generated Markdown file MUST be placed in the same directory as the source PDF (usually `docs/LLM_Wiki/raw/`).
- **No Deletion**: NEVER delete the source PDF automatically.
- **Workflow Integration**: This skill is a prerequisite for the `ingest` operation in `wiki-protocol`.

## Commands

```bash
# Extract text from a PDF in the raw folder
uv run --with pymupdf4llm python .agent/skills/pdf-ingest/assets/extract_pdf.py path/to/file.pdf
```

## Resources

- **Scripts**: See [assets/extract_pdf.py](assets/extract_pdf.py) for the implementation.
