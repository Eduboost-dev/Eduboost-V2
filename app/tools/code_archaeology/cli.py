"""Simple CLI to produce a Code Archaeology report from a git repo.

Usage (from workspace root):
  python -m app.tools.code_archaeology.cli --repo temp/Git --output artifacts/code_archaeology/sample

The CLI will:
 - ingest git history (uses GitPython if available, subprocess fallback)
 - scan known tracking docs under the repo for minimal doc metadata
 - build a synced timeline correlating commits ↔ docs
 - produce JSON outputs and a narrative markdown
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from . import git_ingester, sync_engine, narrative_generator, doc_ingester, TEMPLATES_PATH


def _load_docs_minimal(repo_path: Path) -> List[dict]:
    # Prefer the richer parser in doc_ingester if available
    try:
        return doc_ingester.parse_tracking_docs(repo_path)
    except Exception:
        # Fallback to prior minimal loader if parse fails
        repo_path = Path(repo_path)
        docs: list[dict] = []
        for rel in getattr(doc_ingester, "TRACKING_SUBPATHS", set()):
            p = repo_path / rel
            if not p.exists():
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            fm, body = doc_ingester._parse_frontmatter(text)
            sentiment = doc_ingester._sentiment_score(body)
            sections = [{"heading": "body", "content": body}]
            docs.append({
                "path": str(p.relative_to(repo_path)),
                "doc_type": p.suffix.lstrip("."),
                "title": p.name,
                "metadata": fm,
                "sections": sections,
                "sentiment": sentiment,
            })

        if not docs:
            docs_dir = repo_path / "docs"
            if docs_dir.exists() and docs_dir.is_dir():
                for p in sorted(docs_dir.glob("**/*.md")):
                    try:
                        text = p.read_text(encoding="utf-8")
                    except Exception:
                        continue
                    fm, body = doc_ingester._parse_frontmatter(text)
                    sentiment = doc_ingester._sentiment_score(body)
                    sections = [{"heading": "body", "content": body}]
                    docs.append({
                        "path": str(p.relative_to(repo_path)),
                        "doc_type": p.suffix.lstrip("."),
                        "title": p.name,
                        "metadata": fm,
                        "sections": sections,
                        "sentiment": sentiment,
                    })

        return docs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="code-archaeology")
    parser.add_argument("--repo", required=True, help="Path to repository to analyze")
    parser.add_argument("--output", required=True, help="Output directory for report files")
    parser.add_argument("--branch", default="HEAD", help="Git branch or rev to inspect")
    parser.add_argument("--public-base-url", default=None, help="Public base URL where report artifacts will be published (used to build full URLs)")
    parser.add_argument("--first-parent", action="store_true", help="Use --first-parent for git log")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    public_base = args.public_base_url
    if public_base and not public_base.endswith('/'):
        public_base = public_base + '/'

    print(f"[cli] Repo: {repo}")
    print(f"[cli] Output: {out}")

    # 1) Ingest git history
    try:
        result = git_ingester.ingest_git_history(repo, branch=args.branch, first_parent=args.first_parent)
    except Exception as exc:
        print(f"[cli] Git ingestion failed: {exc}")
        return 2

    ing_path = out / "ingestion.json"
    git_ingester.save_result_json(result, ing_path)

    # 2) Load docs (minimal)
    docs = _load_docs_minimal(repo)
    print(f"[cli] ✓ {len(docs)} docs loaded for analysis")

    # 3) Build synced timeline
    timeline = sync_engine.build_synced_timeline(result.to_dict().get("commits", []), docs, repo_name=repo.name)
    tl_path = out / "timeline.json"
    sync_engine.save_timeline_json(timeline, tl_path)

    # 4) Generate narrative
    narrative = narrative_generator.generate_narrative(timeline.to_dict() if hasattr(timeline, "to_dict") else timeline)
    narrative_path = out / "narrative.json"
    narrative_generator.save_narrative_json(narrative, narrative_path)
    md_path = out / "narrative.md"
    narrative_md = narrative.to_markdown()
    md_path.write_text(narrative_md, encoding="utf-8")

    # 5) Render HTML report using packaged template (inject narrative as preformatted)
    try:
        from html import escape as _escape
        # Prefer a `report_base.html` shipped in the target repo (so users can customize),
        # otherwise fall back to the packaged template in TEMPLATES_PATH.
        repo_tpl = repo / "report_base.html"
        tpl_path = repo_tpl if repo_tpl.exists() else (TEMPLATES_PATH / "report_base.html")
        if tpl_path.exists():
            tpl = tpl_path.read_text(encoding="utf-8")
            start = tpl.find("<main>")
            end = tpl.find("</main>")
            if start != -1 and end != -1 and end > start:
                # Build a richer injection: links to JSON artifacts and a JS object
                # so the template (or client-side code) can fetch and render charts.
                ing_name = ing_path.name
                tl_name = tl_path.name
                nar_name = narrative_path.name
                md_name = md_path.name
                pre = (
                    f"<main>\n<h1>Code Archaeology — {repo.name}</h1>\n"
                    f"<p>Generated: {timeline.generated_at}</p>\n"
                    "<section id=\"report-links\">\n"
                    "<h2>Report Artifacts</h2>\n<ul>\n"
                    f"<li><a href=\"{ing_name}\">{ing_name}</a></li>\n"
                    f"<li><a href=\"{tl_name}\">{tl_name}</a></li>\n"
                    f"<li><a href=\"{nar_name}\">{nar_name}</a></li>\n"
                    f"<li><a href=\"{md_name}\">{md_name}</a></li>\n"
                    "</ul>\n</section>\n"
                    "<section id=\"narrative\">\n<pre>"
                    f"{_escape(narrative_md)}"
                    "</pre>\n</section>\n"
                    "<script>\n"
                        "// Structured report descriptor available to client-side scripts\n"
                        f"window.__CA_REPORT = {{ ingestion: \"{ing_name}\", timeline: \"{tl_name}\", narrative: \"{nar_name}\", narrative_md: \"{md_name}\" }};\n"
                        "window.__CA_REPORT.urls = window.__CA_REPORT.urls || {};\n"
                        + (f"window.__CA_REPORT.urls = {{ ingestion: \"{public_base + ing_name}\", timeline: \"{public_base + tl_name}\", narrative: \"{public_base + nar_name}\", narrative_md: \"{public_base + md_name}\" }};\n" if public_base else "")
                        "</script>\n"
                    "</main>"
                )
                html_out = tpl[:start] + pre + tpl[end + len("</main>") :]
            else:
                html_out = tpl.replace("</body>", f"<pre>{_escape(narrative_md)}</pre></body>")
            html_path = out / "index.html"
            html_path.write_text(html_out, encoding="utf-8")
            print(f"[cli] HTML report written → {html_path}")
        else:
            print("[cli] Template not found; skipping HTML render")
    except Exception as exc:
        print(f"[cli] HTML render failed: {exc}")

    print(f"[cli] Report artifacts: {ing_path}, {tl_path}, {narrative_path}, {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
