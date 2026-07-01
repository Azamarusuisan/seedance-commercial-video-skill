#!/usr/bin/env python3
"""Build a local storyboard board/contact sheet HTML from a storyboard-board.json file.

This never calls image/video generation. It creates a human review surface from existing
composition sources and planned photoreal key visual slots.
"""

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def src(path: str) -> str:
    if not path or path.startswith("derived_"):
        return ""
    normalized = path.replace("\\", "/")
    if normalized.startswith("workspace/"):
        return "/" + normalized
    return normalized


def image_block(path: str, alt: str) -> str:
    image_src = src(path)
    if not image_src:
        return f"<div class='missing'>{html.escape(path or 'pending')}</div>"
    return f"<img src='{html.escape(image_src)}' alt='{html.escape(alt)}'>"


def panel_html(panel: dict) -> str:
    tone = "primary" if panel.get("primary_keyvisual_candidate") else "support"
    return f"""
      <article class="panel-card {tone}">
        <div class="thumb">{image_block(panel.get("source_path", ""), panel.get("title", panel.get("panel_id", "panel")))}</div>
        <div class="panel-meta">
          <span>{html.escape(panel.get("panel_id", ""))} / {html.escape(panel.get("time", ""))}</span>
          <strong>{html.escape(panel.get("title", ""))}</strong>
          <p>{html.escape(panel.get("content", ""))}</p>
          <em>{html.escape(panel.get("seedance_use", ""))}</em>
        </div>
      </article>
    """


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", required=True, help="Path to storyboard-board.json")
    parser.add_argument("--out", default="", help="Output HTML path")
    args = parser.parse_args()

    board_path = Path(args.board)
    board = read_json(board_path)
    out = Path(args.out) if args.out else board_path.with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)

    panels = board.get("panels", [])
    primary = [p for p in panels if p.get("primary_keyvisual_candidate")]
    support = [p for p in panels if not p.get("primary_keyvisual_candidate")]
    hero = board.get("hero", {})

    doc = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(board.get("title", "Storyboard Board"))}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #050b14;
      --panel: #0a1420;
      --line: #12d9ff;
      --gold: #f2c14e;
      --text: #eef7ff;
      --muted: #8ba9bb;
      --danger: #ff3f6e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        linear-gradient(90deg, rgba(18,217,255,.08) 1px, transparent 1px),
        linear-gradient(0deg, rgba(18,217,255,.06) 1px, transparent 1px),
        radial-gradient(circle at 70% 10%, rgba(18,217,255,.16), transparent 34%),
        var(--bg);
      background-size: 32px 32px, 32px 32px, auto, auto;
      color: var(--text);
      font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      padding: 28px;
    }}
    .board {{
      max-width: 1440px;
      margin: 0 auto;
      border: 1px solid rgba(18,217,255,.65);
      background: rgba(5, 11, 20, .82);
      box-shadow: 0 0 48px rgba(18,217,255,.18);
      padding: 22px;
    }}
    header {{
      display: grid;
      grid-template-columns: 1.2fr .8fr;
      gap: 18px;
      align-items: stretch;
      margin-bottom: 18px;
    }}
    .title, .status, .hero, .panel-card {{
      border: 1px solid rgba(18,217,255,.55);
      background: linear-gradient(135deg, rgba(15,30,45,.92), rgba(3,8,18,.96));
      border-radius: 10px;
      overflow: hidden;
    }}
    .title {{ padding: 20px; }}
    .title span, .status span, .section-label {{
      color: var(--line);
      font-weight: 800;
      letter-spacing: .04em;
      text-transform: uppercase;
      font-size: 12px;
    }}
    h1 {{ margin: 8px 0 6px; font-size: 42px; line-height: 1; }}
    .title p {{ margin: 0; color: var(--muted); max-width: 860px; }}
    .status {{ padding: 16px; }}
    .status strong {{ display: block; margin-top: 8px; font-size: 20px; color: var(--gold); }}
    .hero-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }}
    .hero img {{ width: 100%; height: 310px; object-fit: cover; display: block; }}
    .hero div {{ padding: 14px; }}
    .hero h2 {{ margin: 4px 0 8px; }}
    .panels {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
    .panel-card {{ min-height: 365px; display: flex; flex-direction: column; }}
    .panel-card.primary {{ border-color: var(--gold); }}
    .panel-card.support {{ border-color: rgba(18,217,255,.45); }}
    .thumb {{ height: 170px; background: #020611; display: grid; place-items: center; }}
    .thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .missing {{ color: var(--muted); padding: 18px; text-align: center; }}
    .panel-meta {{ padding: 12px; display: flex; flex-direction: column; gap: 8px; }}
    .panel-meta span {{ color: var(--line); font-size: 12px; font-weight: 700; }}
    .panel-meta strong {{ font-size: 16px; }}
    .panel-meta p {{ margin: 0; color: #d8e7f0; }}
    .panel-meta em {{ color: var(--gold); font-style: normal; font-size: 12px; margin-top: auto; }}
    .rules {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
    }}
    .rule {{
      border: 1px solid rgba(18,217,255,.35);
      padding: 14px;
      border-radius: 10px;
      background: rgba(6, 15, 27, .85);
    }}
    .rule strong {{ color: var(--gold); display: block; margin-bottom: 6px; }}
    .rule p {{ margin: 0; color: var(--muted); }}
  </style>
</head>
<body>
  <main class="board">
    <header>
      <section class="title">
        <span>AI Generated Storyboard Board</span>
        <h1>{html.escape(board.get("title", ""))}</h1>
        <p>{html.escape(board.get("summary", ""))}</p>
      </section>
      <aside class="status">
        <span>Approval Gate</span>
        <strong>{html.escape(board.get("approval_status", "pending"))}</strong>
        <p>{html.escape(board.get("gate_note", ""))}</p>
      </aside>
    </header>
    <section class="hero-grid">
      <article class="hero">
        {image_block(hero.get("image_path", ""), hero.get("title", "hero"))}
        <div><span class="section-label">Hero / Mood</span><h2>{html.escape(hero.get("title", ""))}</h2><p>{html.escape(hero.get("note", ""))}</p></div>
      </article>
      <article class="hero">
        <div><span class="section-label">Primary Candidates</span><h2>{len(primary)} key visuals</h2><p>{html.escape(board.get("primary_note", ""))}</p></div>
        <div><span class="section-label">Support Panels</span><h2>{len(support)} support panels</h2><p>{html.escape(board.get("support_note", ""))}</p></div>
      </article>
    </section>
    <section class="panels">
      {''.join(panel_html(panel) for panel in panels)}
    </section>
    <section class="rules">
      <article class="rule"><strong>Blender</strong><p>composition_only / Seedance input not allowed</p></article>
      <article class="rule"><strong>Photoreal storyboard</strong><p>visual_truth / candidate only after human approval</p></article>
      <article class="rule"><strong>Seedance</strong><p>motion_truth / use only approved photoreal key visuals</p></article>
    </section>
  </main>
</body>
</html>
"""
    doc = "\n".join(line.rstrip() for line in doc.splitlines()) + "\n"
    out.write_text(doc, encoding="utf-8")
    try:
        print(out.resolve().relative_to(ROOT))
    except ValueError:
        print(out)


if __name__ == "__main__":
    main()
