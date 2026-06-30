#!/usr/bin/env python3
"""
Build script for ML Search Architecture documentation.

Reads markdown files from blocks/ and proposals/, converts to HTML,
assembles into a single interactive page using template.html.

Usage:
    python build.py                    # outputs to search_ml_design_v2.html
    python build.py -o output.html     # custom output path
    python build.py --watch            # rebuild on file changes (requires watchdog)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Optional: use markdown lib if available, otherwise basic conversion
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


ROOT = Path(__file__).parent
PRODUCTS_DIR = ROOT / "products"
TEMPLATE_PATH = ROOT / "template.html"
DEFAULT_OUTPUT = ROOT / "index.html"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML-like frontmatter from markdown file.

    Returns (metadata_dict, body_text).
    Simple parser — no PyYAML dependency required.
    """
    if not text.startswith("---"):
        return {}, text

    end = text.find("---", 3)
    if end == -1:
        return {}, text

    fm_text = text[3:end].strip()
    body = text[end + 3:].strip()

    meta = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # Handle simple types
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            elif val.isdigit():
                val = int(val)
            meta[key] = val

    return meta, body


def resolve_svgs(html: str, base_path: Path) -> str:
    """Replace <img src="...svg"> with inline SVG content.

    Supports both relative paths (resolved from base_path) and
    project-root-relative paths (resolved from ROOT).
    SVGs are wrapped in a styled container for proper display.
    """
    def replace_svg_img(match):
        src = match.group(1)
        alt = match.group(2) if match.group(2) else ""

        # Resolve path: try relative to base_path first, then ROOT
        svg_path = base_path / src
        if not svg_path.exists():
            svg_path = ROOT / src
        if not svg_path.exists():
            print(f"  WARNING: SVG not found: {src}")
            return match.group(0)  # leave original img tag

        svg_content = svg_path.read_text(encoding="utf-8")
        # Strip XML declaration if present
        svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content).strip()

        caption = f'<div style="font-size:11px;color:#64748b;margin-top:6px">{alt}</div>' if alt else ""
        return f'<div class="svg-inline" style="margin:16px 0;background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06);overflow-x:auto">{svg_content}{caption}</div>'

    # Match <img> tags with .svg src — handle any attribute order
    def _extract_and_replace(m):
        tag = m.group(0)
        src_match = re.search(r'src="([^"]+\.svg)"', tag)
        alt_match = re.search(r'alt="([^"]*)"', tag)
        if not src_match:
            return tag
        # Create a mock match object for replace_svg_img
        class FakeMatch:
            def group(self, i):
                if i == 0:
                    return tag
                elif i == 1:
                    return src_match.group(1)
                elif i == 2:
                    return alt_match.group(1) if alt_match else ""
        return replace_svg_img(FakeMatch())

    html = re.sub(r'<img\s+[^>]*\.svg"[^>]*/?\s*>', _extract_and_replace, html)
    return html


def md_to_html(text: str, source_path: Path = None) -> str:
    """Convert markdown to HTML.

    Uses python-markdown if available, otherwise a basic converter.
    SVG image references (![alt](path.svg)) are inlined automatically.
    """
    if HAS_MARKDOWN:
        html = markdown.markdown(
            text,
            extensions=["tables", "fenced_code", "nl2br"],
            output_format="html5",
        )
    else:
        html = _basic_md_to_html(text)

    # Resolve SVG references to inline SVG
    base = source_path.parent if source_path else ROOT
    html = resolve_svgs(html, base)
    return html


def _basic_md_to_html(text: str) -> str:
    """Basic markdown to HTML conversion without dependencies."""
    lines = text.split("\n")
    html_parts = []
    in_code_block = False
    in_table = False
    in_list = False
    table_rows = []
    list_items = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_parts.append("</code></pre>")
                in_code_block = False
            else:
                lang = line.strip()[3:].strip()
                html_parts.append(f"<pre><code>")
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            html_parts.append(_escape_html(line))
            html_parts.append("\n")
            i += 1
            continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                in_table = True
                table_rows = []
            # Skip separator rows
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                i += 1
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            # End of table
            html_parts.append(_render_table(table_rows))
            in_table = False
            table_rows = []
            # Don't increment, re-process this line

        # List items
        if re.match(r"^\s*[-*]\s+", line):
            if not in_list:
                in_list = True
                list_items = []
            content = re.sub(r"^\s*[-*]\s+", "", line)
            list_items.append(_inline_format(content))
            i += 1
            continue
        elif in_list:
            html_parts.append("<ul>" + "".join(f"<li>{item}</li>" for item in list_items) + "</ul>")
            in_list = False
            list_items = []

        # Headers
        if line.startswith("####"):
            html_parts.append(f"<h4>{_inline_format(line[4:].strip())}</h4>")
        elif line.startswith("###"):
            html_parts.append(f"<h3>{_inline_format(line[3:].strip())}</h3>")
        elif line.startswith("##"):
            html_parts.append(f"<h2>{_inline_format(line[2:].strip())}</h2>")
        elif line.startswith("#"):
            html_parts.append(f"<h1>{_inline_format(line[1:].strip())}</h1>")
        elif line.strip() == "":
            html_parts.append("")
        else:
            html_parts.append(f"<p>{_inline_format(line)}</p>")

        i += 1

    # Close any open blocks
    if in_code_block:
        html_parts.append("</code></pre>")
    if in_table:
        html_parts.append(_render_table(table_rows))
    if in_list:
        html_parts.append("<ul>" + "".join(f"<li>{item}</li>" for item in list_items) + "</ul>")

    return "\n".join(html_parts)


def _render_table(rows: list[list[str]]) -> str:
    """Render table rows as HTML table."""
    if not rows:
        return ""
    html = "<table>"
    # First row is header
    html += "<tr>" + "".join(f"<th>{_inline_format(c)}</th>" for c in rows[0]) + "</tr>"
    for row in rows[1:]:
        html += "<tr>" + "".join(f"<td>{_inline_format(c)}</td>" for c in row) + "</tr>"
    html += "</table>"
    return html


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline_format(text: str) -> str:
    """Apply inline markdown formatting (bold, italic, code, links, images, cross-refs)."""
    # Code (backticks) — do first to avoid processing inside code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # Cross-references: [[block_id]] or [[block_id|display text]]
    text = re.sub(
        r"\[\[([^\]|]+)\|([^\]]+)\]\]",
        r'<a href="#" class="block-ref" onclick="show(\'\1\'); return false;">\2</a>',
        text,
    )
    text = re.sub(
        r"\[\[([^\]]+)\]\]",
        r'<a href="#" class="block-ref" onclick="show(\'\1\'); return false;">\1</a>',
        text,
    )
    # Images (must come before links to avoid conflict)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2" />', text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def load_blocks_from_dir(base_dir: Path) -> dict:
    """Load .md block files from section subdirs within a directory.

    Scans base_dir/{section}/*.md where section dirs contain block files.
    Ignores .svg files, non-directory items, and _-prefixed dirs.
    """
    blocks = {}
    if not base_dir.exists():
        return blocks

    for section_dir in sorted(base_dir.iterdir()):
        if not section_dir.is_dir() or section_dir.name.startswith("_"):
            continue
        for md_file in sorted(section_dir.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            text = md_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)
            if not meta.get("id"):
                print(f"WARNING: {md_file.name} has no 'id' in frontmatter, skipping")
                continue

            block_id = meta["id"]
            blocks[block_id] = {
                "meta": meta,
                "html": md_to_html(body, source_path=md_file),
                "variants": [],
                "source": str(md_file.relative_to(ROOT)),
                "source_abs": str(md_file),
            }

    return blocks


def load_teams(blocks: dict, teams_dir: Path) -> dict:
    """Load team-owned block overrides from teams/{team_name}/*.md."""
    if not teams_dir.exists():
        return blocks

    for team_dir in sorted(teams_dir.iterdir()):
        if not team_dir.is_dir():
            continue
        team_name = team_dir.name

        for md_file in sorted(team_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)

            if not meta.get("id"):
                print(f"WARNING: {md_file} has no 'id' in frontmatter, skipping")
                continue

            block_id = meta["id"]
            team_html = md_to_html(body, source_path=md_file)

            source_rel = str(md_file.relative_to(ROOT))
            source_abs = str(md_file)

            if block_id in blocks:
                # Add as a team variant (shown as tab)
                variant = {
                    "id": f"{team_name}_{block_id}",
                    "title": meta.get("title", block_id),
                    "author": meta.get("team", team_name),
                    "status": meta.get("status", "accepted"),
                    "summary": meta.get("summary", f"Owned by {team_name} team"),
                    "html": team_html,
                    "source": source_rel,
                    "source_abs": source_abs,
                }
                blocks[block_id]["variants"].insert(0, variant)
            else:
                # New block from team
                blocks[block_id] = {
                    "meta": meta,
                    "html": team_html,
                    "variants": [],
                    "team": team_name,
                    "source": source_rel,
                    "source_abs": source_abs,
                }

    return blocks


def load_proposals(blocks: dict, proposals_dir: Path) -> dict:
    """Load proposal .md files from proposals/ subdirectories."""
    if not proposals_dir.exists():
        return blocks

    for author_dir in sorted(proposals_dir.iterdir()):
        if not author_dir.is_dir():
            continue
        author = author_dir.name

        for md_file in sorted(author_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(text)

            if not meta.get("id"):
                print(f"WARNING: {md_file} has no 'id' in frontmatter, skipping")
                continue

            target = meta.get("target")
            variant_type = meta.get("type", "alternative")

            variant = {
                "id": meta["id"],
                "title": meta.get("title", meta["id"]),
                "author": meta.get("author", author),
                "status": meta.get("status", "proposal"),
                "summary": meta.get("summary", ""),
                "html": md_to_html(body, source_path=md_file),
                "source": str(md_file.relative_to(ROOT)),
                "source_abs": str(md_file),
            }

            if variant_type == "alternative" and target and target in blocks:
                blocks[target]["variants"].append(variant)
            elif variant_type == "new_stream" or variant_type == "new_block":
                # New block — add to blocks dict
                blocks[meta["id"]] = {
                    "meta": meta,
                    "html": md_to_html(body, source_path=md_file),
                    "variants": [],
                    "is_proposal": True,
                }
            elif variant_type == "extension" and target and target in blocks:
                # Append to existing block
                blocks[target]["html"] += f'\n<hr style="margin:32px 0;border:none;border-top:1px solid #e8e8e8">\n'
                blocks[target]["html"] += f'<div class="author-tag">Extension by {variant.get("author", author)}: {variant.get("title", "")}</div>\n'
                blocks[target]["html"] += variant["html"]
            else:
                print(f"WARNING: {md_file} has target='{target}' but block not found or unknown type='{variant_type}'")

    return blocks


def load_diagrams(diagrams_dir: Path) -> list[dict]:
    """Load SVG diagrams from a diagrams/ directory.

    Supports two structures:
      1. Subdirectories as groups:
         diagrams/current/pipeline.svg → group "current", sublabel "Pipeline"
         diagrams/target/online.svg   → group "target", sublabel "Online"

      2. Flat files (legacy fallback):
         diagrams/00_current.svg      → group "current", sublabel "Current"
         diagrams/01_target_online.svg → group "target", sublabel "Online"

    Returns list of {id, label, group, sublabel, svg} dicts.
    """
    diagrams = []
    if not diagrams_dir.exists():
        return diagrams

    # Check if subdirectory structure exists
    subdirs = sorted([d for d in diagrams_dir.iterdir() if d.is_dir() and not d.name.startswith("_")])

    if subdirs:
        # Subdirectory mode: each subdir is a group
        for subdir in subdirs:
            group = subdir.name.lower()
            for svg_file in sorted(subdir.glob("*.svg")):
                svg_content = svg_file.read_text(encoding="utf-8")
                svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content).strip()

                name = svg_file.stem
                name = re.sub(r"^\d+_?", "", name)  # strip leading digits
                sublabel = name.replace("_", " ").title()

                diagrams.append({
                    "id": f"{group}_{svg_file.stem}",
                    "label": f"{group.title()} {sublabel}",
                    "group": group,
                    "sublabel": sublabel,
                    "svg": svg_content,
                })
    else:
        # Flat file fallback
        for svg_file in sorted(diagrams_dir.glob("*.svg")):
            svg_content = svg_file.read_text(encoding="utf-8")
            svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content).strip()

            name = svg_file.stem
            name = re.sub(r"^\d+_?", "", name)
            parts = name.split("_", 1)

            if len(parts) > 1:
                group = parts[0].lower()
                sublabel = parts[1].replace("_", " ").title()
            else:
                group = parts[0].lower()
                sublabel = parts[0].replace("_", " ").title()

            diagrams.append({
                "id": svg_file.stem,
                "label": name.replace("_", " ").title(),
                "group": group,
                "sublabel": sublabel,
                "svg": svg_content,
            })

    return diagrams




def load_products_config() -> list[dict]:
    """Load product list from products/_products.yaml."""
    config_path = PRODUCTS_DIR / "_products.yaml"
    if not config_path.exists():
        print(f"ERROR: {config_path} not found", file=sys.stderr)
        sys.exit(1)

    products = []
    text = config_path.read_text(encoding="utf-8")
    current = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- id:"):
            if current:
                products.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
        elif line.startswith("label:"):
            current["label"] = line.split(":", 1)[1].strip()
    if current:
        products.append(current)

    return products


def build_product(product_dir: Path) -> dict:
    """Build a single product from nested structure.

    Structure: product_dir/{group}/{variant}/
      - diagram.svg (or any .svg) = the diagram for this view
      - {section}/*.md = block files

    Blocks are scoped per view (diagram). Each view has its own set of blocks.
    Also loads proposals from product_dir/proposals/.
    """
    proposals_dir = product_dir / "proposals"

    # Discover group/variant structure
    # Groups are top-level dirs (current, target)
    # Variants are dirs within groups (online, offline)
    diagrams = []
    blocks_by_view = {}  # view_id -> {block_id -> block_data}

    for group_dir in sorted(product_dir.iterdir()):
        if not group_dir.is_dir() or group_dir.name.startswith("_"):
            continue
        if group_dir.name in {"proposals", "diagrams"}:
            continue

        group = group_dir.name

        # Check if this dir contains variant subdirs or is itself a variant
        variant_dirs = sorted([
            d for d in group_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ])
        has_svg = any(group_dir.glob("*.svg"))

        if variant_dirs and not has_svg:
            # group/variant/ structure
            for variant_dir in variant_dirs:
                variant = variant_dir.name
                view_id = f"{group}_{variant}"
                # Load diagram from variant dir
                for svg_file in sorted(variant_dir.glob("*.svg")):
                    svg_content = svg_file.read_text(encoding="utf-8")
                    svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content).strip()
                    diagrams.append({
                        "id": view_id,
                        "label": f"{group.title()} {variant.title()}",
                        "group": group,
                        "sublabel": variant.replace("_", " ").title(),
                        "svg": svg_content,
                    })
                    break  # one diagram per variant

                # Load blocks scoped to this view
                variant_blocks = load_blocks_from_dir(variant_dir)
                if variant_blocks:
                    blocks_by_view[view_id] = variant_blocks
        else:
            # Flat: group dir itself is the variant (e.g. single diagram + sections)
            view_id = group
            for svg_file in sorted(group_dir.glob("*.svg")):
                svg_content = svg_file.read_text(encoding="utf-8")
                svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content).strip()
                diagrams.append({
                    "id": view_id,
                    "label": group.replace("_", " ").title(),
                    "group": group,
                    "sublabel": group.replace("_", " ").title(),
                    "svg": svg_content,
                })
                break

            # Load blocks scoped to this view
            group_blocks = load_blocks_from_dir(group_dir)
            if group_blocks:
                blocks_by_view[view_id] = group_blocks

    # Legacy fallback: flat blocks/ directory
    if not blocks_by_view:
        legacy_blocks_dir = product_dir / "blocks"
        if legacy_blocks_dir.exists():
            legacy_blocks = {}
            for md_file in sorted(legacy_blocks_dir.glob("*.md")):
                if md_file.name.startswith("_"):
                    continue
                text = md_file.read_text(encoding="utf-8")
                meta, body = parse_frontmatter(text)
                if not meta.get("id"):
                    continue
                block_id = meta["id"]
                legacy_blocks[block_id] = {
                    "meta": meta,
                    "html": md_to_html(body, source_path=md_file),
                    "variants": [],
                    "source": str(md_file.relative_to(ROOT)),
                    "source_abs": str(md_file),
                }
            if legacy_blocks:
                # Assign legacy blocks to all diagrams
                for d in diagrams:
                    blocks_by_view[d["id"]] = legacy_blocks

    # Legacy fallback: diagrams/ directory
    legacy_diagrams_dir = product_dir / "diagrams"
    if legacy_diagrams_dir.exists() and not diagrams:
        diagrams = load_diagrams(legacy_diagrams_dir)

    # Load proposals into each view's blocks
    for view_id in blocks_by_view:
        blocks_by_view[view_id] = load_proposals(blocks_by_view[view_id], proposals_dir)

    # Prepare blocks JSON per view
    blocks_by_view_json = {}
    total_blocks = 0
    for view_id, view_blocks in blocks_by_view.items():
        view_json = {}
        for block_id, block_data in view_blocks.items():
            meta = block_data.get("meta", {})
            view_json[block_id] = {
                "html": block_data["html"],
                "variants": block_data["variants"],
                "source": block_data.get("source", ""),
                "title": meta.get("title", block_id),
                "position": meta.get("position", 999),
            }
        blocks_by_view_json[view_id] = view_json
        total_blocks += len(view_json)

    return {
        "blocks_by_view": blocks_by_view_json,
        "diagrams": diagrams,
        "block_count": total_blocks,
        "diagram_count": len(diagrams),
    }


def build(output_path: Path):
    """Main build function."""
    print(f"Building ML Design docs...")

    # Load product config
    products = load_products_config()
    print(f"  Found {len(products)} products")

    # Build each product
    products_data = {}
    for product in products:
        pid = product["id"]
        product_dir = PRODUCTS_DIR / pid
        if not product_dir.exists():
            continue
        data = build_product(product_dir)
        if data["block_count"] == 0 and data["diagram_count"] == 0:
            continue  # skip empty products
        products_data[pid] = data
        print(f"  {product['label']}: {data['block_count']} blocks, {data['diagram_count']} diagrams")

    # Products menu list (only non-empty)
    products_menu = [p for p in products if p["id"] in products_data]

    # Load template
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Inject content
    output = template.replace("{{PRODUCTS_JSON}}", json.dumps(products_menu, ensure_ascii=False))
    output = output.replace("{{PRODUCTS_DATA}}", json.dumps(products_data, ensure_ascii=False))

    # Write output
    output_path.write_text(output, encoding="utf-8")
    print(f"  Output: {output_path}")
    print(f"  Done!")


def get_source_mtimes() -> dict[str, float]:
    """Get modification times of all source files."""
    mtimes = {}
    # Watch all files under products/
    if PRODUCTS_DIR.exists():
        for p in PRODUCTS_DIR.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                mtimes[str(p)] = p.stat().st_mtime
    mtimes[str(TEMPLATE_PATH)] = TEMPLATE_PATH.stat().st_mtime
    return mtimes


LIVERELOAD_SNIPPET = '''<script>
(function() {
  let lastCheck = Date.now();
  setInterval(async () => {
    try {
      const resp = await fetch('/__reload?t=' + lastCheck);
      const data = await resp.json();
      if (data.reload) { lastCheck = Date.now(); location.reload(); }
    } catch(e) {}
  }, 800);
})();
</script>'''


def serve_with_watch(output_path: Path, port: int = 3333):
    """Serve HTML with auto-rebuild on file changes."""
    import http.server
    import threading
    import time
    import urllib.parse

    build(output_path)

    last_build_time = [time.time()]
    prev_mtimes = [get_source_mtimes()]

    def check_and_rebuild():
        """Check for file changes and rebuild if needed."""
        while True:
            time.sleep(0.5)
            current = get_source_mtimes()
            if current != prev_mtimes[0]:
                prev_mtimes[0] = current
                print(f"\n  File changed, rebuilding...", flush=True)
                try:
                    build(output_path)
                    last_build_time[0] = time.time()
                    print(f"  Reload triggered.", flush=True)
                except Exception as e:
                    print(f"  ERROR: {e}", flush=True)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)

            # Livereload endpoint
            if parsed.path == '/__reload':
                query = urllib.parse.parse_qs(parsed.query)
                client_t = float(query.get('t', [0])[0]) / 1000.0
                should_reload = last_build_time[0] > client_t
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"reload": should_reload}).encode())
                return

            # Serve the built HTML at root
            if parsed.path == '/' or parsed.path == f'/{output_path.name}':
                content = output_path.read_text(encoding='utf-8')
                # Inject livereload script before </body>
                content = content.replace('</body>', LIVERELOAD_SNIPPET + '</body>')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode())
                return

            super().do_GET()

        def log_message(self, format, *args):
            # Suppress noisy reload polling logs
            if '/__reload' not in str(args[0]):
                super().log_message(format, *args)

    # Start file watcher thread
    watcher = threading.Thread(target=check_and_rebuild, daemon=True)
    watcher.start()

    server = http.server.HTTPServer(('localhost', port), Handler)
    url = f"http://localhost:{port}"
    print(f"\n  Serving at {url}")
    print(f"  Watching for changes in blocks/, teams/, proposals/")
    print(f"  Press Ctrl+C to stop\n")

    # Open in browser
    import webbrowser
    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Build ML Search Architecture docs")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output HTML file path")
    parser.add_argument("-w", "--watch", action="store_true",
                        help="Watch for changes and serve with livereload")
    parser.add_argument("-p", "--port", type=int, default=3333,
                        help="Port for watch server (default: 3333)")
    args = parser.parse_args()

    if args.watch:
        serve_with_watch(args.output, args.port)
    else:
        build(args.output)


if __name__ == "__main__":
    main()
