# ML Design Documents

## What is this

Interactive architecture documentation for Constructor.io ML systems. Builds into a single-page HTML (`index.html`) from markdown + SVG files.

## Structure

```
build.py                    — builds index.html from products/
template.html               — HTML template with JS logic
products/_products.yaml     — product registry (menu order)
products/{product}/{current|target}/{online|offline}/
  diagram.svg               — clickable architecture diagram
  {section}/*.md            — block descriptions (shown on click)
  {section}/*.svg           — diagrams, inlined via ![](file.svg)
```

## Build

```bash
python build.py              # → index.html
python build.py --watch      # dev server with livereload on :3333
```

## Context

SaaS product search. 200+ customers (e-commerce stores). Multi-tenant: shared infra, per-customer models/configs.

Related codebases for reference:
- `../lingoml` — ML library (reranker models, preprocessing, backends)
- `../data-pipeline` — training pipelines (Luigi/Spark, feature store, customer configs)
- `../autocomplete` — serving (reranker service, feature store client, SABR)

## Writing content

- Dense technical documentation. No fluff, no motivational framing.
- Target describes the desired end-state, current describes how things work today.
- Style: structured, concise, with examples and diagrams where needed.
- SVG diagrams are separate files, referenced from md via `![](diagram.svg)`.
- Each block md file must have frontmatter with `id` (matches `data-click` in SVG), `title`, `position`.
- Clickable elements in SVG: `<g data-click="block_id" style="cursor:pointer">`.

## Deploy

Push to master → GitHub Actions → GitHub Pages: https://constructor-io.github.io/ml_design_page/
