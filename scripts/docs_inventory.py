#!/usr/bin/env python3
"""docs_inventory.py

Scan the workspace for documentation files, extract metadata, classify,
and emit:

- docs_inventory.json
- docs_inventory.md
- docs_gap_report.md
- docs_generation_plan.md

This is intended as a small, dependency-free first-pass tool to seed
higher-level automation (Docling, MarkItDown, LlamaIndex, etc.).
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TEXT_EXTS = {'.md', '.markdown', '.rst', '.html', '.htm', '.txt', '.json', '.yml', '.yaml', '.csv'}
DOC_EXTS = TEXT_EXTS.union({'.pdf', '.docx', '.pptx', '.ppt', '.xlsx'})
EXCLUDE_DIRS = {'.git', '.venv', 'venv', 'node_modules', 'coverage_html', '__pycache__'}

DELIVERABLE_KEYWORDS: List[Tuple[str, List[str]]] = [
    ("System Overview", [
        "system overview", "system architecture", "architecture overview", "overview",
        "test", "doc", "report", "design", "document", "summary", "implementation", "guide", "plan", "api",
    ]),
    ("Architecture Handoff", [
        "architecture handoff", "architecture decision record", "adr", "handoff",
        "status", "context", "required", "release", "purpose", "final", "audit", "documentation", "adrs", "checklist",
    ]),
    ("Production Readiness Report", [
        "production readiness", "production ready", "readiness", "prr",
        "deep", "contracts", "runtime", "data", "meta", "contract", "report", "backend", "implementation", "status",
    ]),
    ("Roadmap Consolidation", [
        "roadmap", "product roadmap", "road map",
        "production", "implementation", "phase", "baseline", "status", "execution", "readiness", "required", "agent", "post",
    ]),
    ("Audit Evidence Index", [
        "audit evidence", "audit", "evidence", "audit trail",
        "release", "purpose", "required", "runtime", "contract", "popia", "consent", "backend", "final", "data",
    ]),
    ("Developer Onboarding Guide", [
        "onboarding", "developer onboarding", "getting started", "contributor guide", "developer guide",
        "boundary", "ether", "consent", "questions", "authentication", "auth", "production", "contract", "endpoint", "policy",
    ]),
    ("API Documentation Index", [
        "api documentation", "api", "openapi", "swagger", "endpoints", "api reference",
        "data", "meta", "contract", "resource", "error", "routers", "index", "frontend", "github", "fastapi",
    ]),
    ("Compliance / POPIA Pack", [
        "popia", "compliance", "gdpr", "privacy", "data protection",
        "consent", "audit", "evidence", "rights", "boundary", "authorization", "wiring", "purpose", "lifecycle", "check",
    ]),
    ("Beta Launch Pack", [
        "beta launch", "beta", "launch", "release plan", "go-live",
        "data", "meta", "param", "managed", "agents", "tool", "block", "result", "code", "error",
    ]),
]

MAX_READ = 256 * 1024  # read up to 256KB of text files


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def find_doc_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if is_excluded(p):
            continue
        if p.suffix.lower() in DOC_EXTS or p.name.lower().endswith(('.md', '.markdown')):
            files.append(p)
    return sorted(files)


def read_text(path: Path) -> str:
    try:
        with path.open('rb') as f:
            data = f.read(MAX_READ)
        # quick binary check
        if b"\x00" in data:
            return ""
        return data.decode('utf-8', errors='replace')
    except Exception:
        return ""


def parse_frontmatter(text: str) -> Dict[str, Any]:
    fm: Dict[str, Any] = {}
    if text.startswith('---'):
        parts = text.splitlines()
        if len(parts) > 1:
            fm_lines = []
            for line in parts[1:]:
                if line.strip() in ('---', '...'):
                    break
                fm_lines.append(line)
            for line in fm_lines:
                if ':' in line:
                    k, v = line.split(':', 1)
                    fm[k.strip().lower()] = v.strip().strip('"\'')
    return fm


def extract_headings(text: str) -> List[Tuple[int, str]]:
    headings: List[Tuple[int, str]] = []
    for m in re.finditer(r'^(#{1,6})\s+(.*)$', text, flags=re.MULTILINE):
        level = len(m.group(1))
        headings.append((level, m.group(2).strip()))
    # rudimentary reST underlined headings
    for m in re.finditer(r'^(?P<title>.+)\n(?P<under>[-=~`^\*]+)\n', text, flags=re.MULTILINE):
        headings.append((1, m.group('title').strip()))
    return headings


def extract_links(text: str) -> List[str]:
    links: List[str] = []
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
        links.append(m.group(2).strip())
    for m in re.finditer(r'(https?://[^\s)]+)', text):
        links.append(m.group(1).strip())
    # file paths
    for m in re.finditer(r'([\w/\.-]+\.(?:md|markdown|pdf|docx|pptx|xlsx))', text):
        links.append(m.group(1))
    return sorted(set(links))


def extract_status(text: str, fm: Dict[str, Any]) -> Optional[str]:
    if 'status' in fm:
        return str(fm['status'])
    m = re.search(r'(?i)^status[:\s]+([A-Za-z0-9 _-]+)$', text, flags=re.MULTILINE)
    if m:
        return m.group(1).strip()
    if re.search(r'(?i)\bdraft\b', text):
        return 'draft'
    return None


def extract_dates(text: str, path: Path, fm: Dict[str, Any]) -> str:
    if 'date' in fm:
        return fm['date']
    m = re.search(r'(?i)last updated[:\s]+(.+)$', text, flags=re.MULTILINE)
    if m:
        return m.group(1).strip()
    try:
        ts = path.stat().st_mtime
        return datetime.utcfromtimestamp(ts).isoformat()
    except Exception:
        return ''


def find_evidence_refs(links: List[str]) -> List[str]:
    ev = []
    for l in links:
        if re.search(r'(?i)(evidence|audit|artifact|review|audits|artifacts)', l):
            ev.append(l)
    return ev


def classify_tags(text: str, title: str) -> List[str]:
    found: List[str] = []
    hay = (title + '\n' + text).lower()
    for name, kws in DELIVERABLE_KEYWORDS:
        for kw in kws:
            if kw in hay:
                found.append(name)
                break
    return sorted(set(found))


def analyze_file(path: Path) -> Dict[str, Any]:
    ext = path.suffix.lower()
    text = read_text(path) if ext in TEXT_EXTS else ''
    fm = parse_frontmatter(text) if text else {}
    title = fm.get('title') or ''
    if not title:
        # first H1
        m = re.search(r'(?m)^#\s+(.+)$', text)
        if m:
            title = m.group(1).strip()
        else:
            title = path.stem
    headings = extract_headings(text) if text else []
    links = extract_links(text) if text else []
    status = extract_status(text, fm)
    date = extract_dates(text, path, fm)
    evidence = find_evidence_refs(links)
    tags = classify_tags(text, title)
    doc_type = (
        'markdown' if ext in ('.md', '.markdown') else
        'restructuredtext' if ext == '.rst' else
        'html' if ext in ('.html', '.htm') else
        'pdf' if ext == '.pdf' else
        'presentation' if ext in ('.pptx', '.ppt') else
        'document' if ext == '.docx' else
        'spreadsheet' if ext in ('.xlsx',) else
        'data' if ext in ('.csv', '.json') else
        'other'
    )
    return {
        'path': str(path.as_posix()),
        'title': title,
        'type': doc_type,
        'ext': ext,
        'status': status or 'unknown',
        'date': date,
        'headings': [{'level': h[0], 'text': h[1]} for h in headings[:20]],
        'top_headings': [h[1] for h in headings[:3]],
        'links': links,
        'evidence_refs': evidence,
        'tags': tags,
    }


def emit_json(items: List[Dict[str, Any]], out_path: Path) -> None:
    out_path.write_text(json.dumps(items, indent=2, ensure_ascii=False))


def emit_markdown(items: List[Dict[str, Any]], out_path: Path) -> None:
    lines: List[str] = []
    lines.append('# Docs Inventory')
    lines.append(f'Generated: {datetime.utcnow().isoformat()}Z')
    lines.append('')
    lines.append('| Path | Title | Type | Status | Date | Tags | Top Headings | Evidence |')
    lines.append('|---|---|---|---|---|---|---|---|')
    for it in items:
        path_link = f'[{it["path"]}]({it["path"]})'
        title = it['title'].replace('|', '\\|')
        ttype = it['type']
        status = it.get('status', '')
        date = it.get('date', '')
        tags = ', '.join(it.get('tags', []))
        top_h = ', '.join(it.get('top_headings', []))
        ev = ', '.join(it.get('evidence_refs', []))
        lines.append(f'| {path_link} | {title} | {ttype} | {status} | {date} | {tags} | {top_h} | {ev} |')
    out_path.write_text('\n'.join(lines))


def make_gap_report(items: List[Dict[str, Any]], out_path: Path) -> None:
    lines: List[str] = []
    lines.append('# Docs Gap Report')
    lines.append(f'Generated: {datetime.utcnow().isoformat()}Z')
    lines.append('')
    by_tag: Dict[str, List[str]] = {}
    for name, _ in DELIVERABLE_KEYWORDS:
        by_tag[name] = []
    for it in items:
        for tag in it.get('tags', []):
            if tag in by_tag:
                by_tag[tag].append(it['path'])
    for name, _ in DELIVERABLE_KEYWORDS:
        found = by_tag.get(name, [])
        if found:
            lines.append(f'## {name}')
            lines.append(f'- Status: Present ({len(found)} document(s))')
            for p in found:
                lines.append(f'  - [{p}]({p})')
        else:
            # try weak matches: any doc containing any keyword in path/title
            candidates: List[str] = []
            kws = []
            for nm, ks in DELIVERABLE_KEYWORDS:
                if nm == name:
                    kws = ks
                    break
            for it in items:
                hay = (it['title'] + '\n' + '\n'.join(it.get('top_headings', []))).lower()
                if any(k in hay for k in kws):
                    candidates.append(it['path'])
            lines.append(f'## {name}')
            lines.append('- Status: Missing or incomplete')
            if candidates:
                lines.append('- Candidate source documents:')
                for p in candidates:
                    lines.append(f'  - [{p}]({p})')
            else:
                lines.append('- No obvious candidate documents found')
    out_path.write_text('\n'.join(lines))


def make_generation_plan(items: List[Dict[str, Any]], out_path: Path) -> None:
    lines: List[str] = []
    lines.append('# Docs Generation Plan')
    lines.append(f'Generated: {datetime.utcnow().isoformat()}Z')
    lines.append('')
    lines.append('This plan lists missing deliverables and recommended source documents and tools to generate them.')
    lines.append('')
    by_tag: Dict[str, List[str]] = {name: [] for name, _ in DELIVERABLE_KEYWORDS}
    for it in items:
        for tag in it.get('tags', []):
            if tag in by_tag:
                by_tag[tag].append(it['path'])
    for name, kws in DELIVERABLE_KEYWORDS:
        lines.append(f'## {name}')
        sources = by_tag.get(name, [])
        if sources:
            lines.append(f'- Status: Candidate content available ({len(sources)})')
            lines.append('- Candidate sources:')
            for s in sources:
                lines.append(f'  - [{s}]({s})')
            lines.append('- Recommended tools:')
            lines.append('  - Use Docling to extract structured sections and metadata')
            lines.append('  - Use MarkItDown to normalize/merge into a canonical Markdown doc')
            lines.append('  - Use LlamaIndex-style semantic indexing for retrieval and consolidation')
        else:
            lines.append('- Status: No clear source documents')
            lines.append('- Recommended actions:')
            lines.append('  - Interview stakeholders or search meeting notes, PRs, and release artifacts')
            lines.append('  - Draft a new document from the product/tech leads')
            lines.append('  - Use the Documents/Presentations/Spreadsheets skill to ingest non-markdown assets')
        lines.append('')
    out_path.write_text('\n'.join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.', help='Root directory to scan')
    parser.add_argument('--out', default='docs_inventory.json', help='JSON output path')
    parser.add_argument('--md', default='docs_inventory.md', help='Markdown inventory output path')
    parser.add_argument('--gap', default='docs_gap_report.md', help='Gap report output path')
    parser.add_argument('--plan', default='docs_generation_plan.md', help='Generation plan output path')
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f'Root not found: {root}')
        return

    files = find_doc_files(root)
    print(f'Found {len(files)} candidate documentation files under {root}')
    items: List[Dict[str, Any]] = []
    for f in files:
        try:
            items.append(analyze_file(f))
        except Exception as e:
            print(f'Error analyzing {f}: {e}')

    emit_json(items, Path(args.out))
    emit_markdown(items, Path(args.md))
    make_gap_report(items, Path(args.gap))
    make_generation_plan(items, Path(args.plan))

    print('Wrote:')
    for p in (args.out, args.md, args.gap, args.plan):
        print(f' - {p}')


if __name__ == '__main__':
    main()
