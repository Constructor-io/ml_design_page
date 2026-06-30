# ML Design

Interactive architecture documentation for Constructor.io ML systems.

**Live:** https://constructor-io.github.io/ml_design_page/
<img width="1699" height="899" alt="Screenshot 2026-06-30 at 15 31 38" src="https://github.com/user-attachments/assets/8c3bfea6-70b3-49a2-a3c6-b7fcbe785c1e" />

## Products

| Product | Status |
|---------|--------|
| Search | Current + Target architecture |
| Search Suggestions | Current state documented |
| Recommendations | Current state documented |
| Browse | Placeholder |
| Autocomplete | Placeholder |
| Offsite Discovery | Placeholder |
| Related Searches | Placeholder |
| ASA | Placeholder |
| Quizzes | Placeholder |

## Structure

```
products/{product}/{current|target}/{online|offline}/
  diagram.svg          — clickable architecture diagram
  {section}/*.md       — block descriptions (shown on click)
  {section}/*.svg      — inline diagrams referenced from md
```

## Build

```bash
python build.py              # → index.html
python build.py --watch      # dev server with livereload
```

Requires Python 3.10+. Optional: `pip install markdown` for better markdown rendering.

## Adding content

1. Create `products/{product}/{variant}/{view}/{section}/block.md` with frontmatter:

```yaml
---
id: block_id          # must match data-click in diagram SVG
title: "Block Title"
type: block
position: 1           # display order in panel
---
```

2. Reference SVG diagrams from markdown: `![](diagram.svg)`

3. Make diagram blocks clickable: `<g data-click="block_id" style="cursor:pointer">`

4. Run `python build.py` — deploys automatically on push to master.
