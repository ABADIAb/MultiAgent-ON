---
name: presentation-designer
description: >
  Defines the standard format for generating slide decks in Markdown.
  Trigger: When user asks to create a presentation, slides, PowerPoint draft, or slide deck.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- When asked to draft a presentation.
- When generating content that will later be copied into PowerPoint or Google Slides.
- When summarizing an architecture or concept into a slide format.

## Critical Patterns

- **Slide Separators**: Use `---` on an empty line to clearly separate slides.
- **Scannable Content**: Avoid long paragraphs. Use H1 or H2 for slide titles and bullet points for the body. One main idea per slide.
- **Layout Suggestions**: Use a GitHub alert blockquote `> [!LAYOUT]` to suggest how the content should be visually distributed in the final presentation software (e.g., "Two-column layout. Left: Bullet points. Right: Mermaid diagram").
- **Image Suggestions**: Use standard markdown image syntax with a descriptive alt text acting as a placeholder if no image exists (e.g., `![Image Suggestion: Flowchart of MAS architecture]`).
- **Speaker Notes**: Use HTML comments `<!-- Speaker Notes: Your detailed script here -->` at the bottom of each slide. This is where the long explanatory text goes for the presenter.

## Code Examples

```markdown
---

## Slide 1: Introduction to Hybrid Memory

> [!LAYOUT]
> Title centered. Bullet points on the left. A conceptual graphic on the right.

- **Problem:** LLMs lose context over time.
- **Solution:** Tri-Partite Memory Architecture.
- **Components:** Wiki, Knowledge Graph, Vector RAG.

![Image Suggestion: Diagram showing the 3 pillars of memory]

<!-- Speaker Notes: Welcome everyone. Today we are addressing the fundamental limitation of Large Language Models: context window degradation. Our solution is the Tri-Partite Memory Architecture... -->

---
```

## Commands

No specific bash commands required. This is a pure structural formatting skill.

## Resources

- **Templates**: See this SKILL file for the layout structure.
