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
    repo_path = Path(repo_path)
    docs: list[dict] = []
    # Scan known high-value tracking paths first
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
        # simple one-section doc
        sections = [{"heading": "body", "content": body}]
        docs.append({
            "path": str(p.relative_to(repo_path)),
            "doc_type": p.suffix.lstrip("."),
            "title": p.name,
            "metadata": fm,
            "sections": sections,
            "sentiment": sentiment,
        })

    # Fallback: if none found, scan docs/ top-level markdown files
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
    parser.add_argument("--first-parent", action="store_true", help="Use --first-parent for git log")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)

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
    md_path.write_text(narrative.to_markdown(), encoding="utf-8")

    print(f"[cli] Report artifacts: {ing_path}, {tl_path}, {narrative_path}, {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
