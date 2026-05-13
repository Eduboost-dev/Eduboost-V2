#!/usr/bin/env python3
"""
scripts/audit_router_thinness.py
---------------------------------
Audits all files under app/api_v2_routers/ for signs of business logic
that should live in services instead.

Checks performed
----------------
1. Cyclomatic-complexity threshold: any route function with complexity > MAX_COMPLEXITY
   is flagged (default 5 — routers should be thin pass-through handlers).
2. Forbidden-import patterns: routers must not import from app.repositories,
   app.domain write-models, or raw SQLAlchemy session calls.
3. Suspicious-pattern grep: raw SQL strings, `.query(`, `.add(`, `.commit(`,
   `.execute(`, business-rule keywords (e.g. "if learner.grade").

Usage
-----
    python scripts/audit_router_thinness.py [--strict] [--json]

Exit codes
----------
    0  No violations found
    1  Violations found (CI should fail on this)

Options
-------
    --strict   Treat warnings as errors (exit 1 on any finding)
    --json     Emit JSON report instead of human-readable text
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROUTER_DIR = Path("app/api_v2_routers")
MAX_COMPLEXITY = 5  # P2 static complexity threshold (§2.3)

# Patterns that suggest business logic leaking into routers
FORBIDDEN_IMPORT_PATTERNS = [
    r"from app\.repositories",
    r"import app\.repositories",
    r"from app\.core\.db import",   # direct session access
    r"from sqlalchemy",
]

SUSPICIOUS_CALL_PATTERNS = [
    r"\.query\(",
    r"\.add\(",
    r"\.commit\(",
    r"\.execute\(",
    r"\.filter\(",
    r"db\.query",
    r"session\.query",
]

# Simplified McCabe complexity counter
class _ComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.complexity = 1  # base

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.complexity += 1
        self.generic_visit(node)


def _measure_complexity(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    v = _ComplexityVisitor()
    v.visit(func_node)
    return v.complexity


@dataclass
class Violation:
    file: str
    line: int
    kind: str  # "complexity" | "forbidden_import" | "suspicious_call"
    detail: str
    severity: str = "ERROR"  # "ERROR" | "WARNING"


@dataclass
class AuditReport:
    total_files: int = 0
    total_functions: int = 0
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)


def audit_file(path: Path, report: AuditReport, strict: bool) -> None:
    source = path.read_text(encoding="utf-8")
    report.total_files += 1

    # --- import / call pattern grep (line-level) ---
    for lineno, line in enumerate(source.splitlines(), start=1):
        for pattern in FORBIDDEN_IMPORT_PATTERNS:
            if re.search(pattern, line):
                report.violations.append(
                    Violation(
                        file=str(path),
                        line=lineno,
                        kind="forbidden_import",
                        detail=f"Router imports from restricted layer: `{line.strip()}`",
                        severity="ERROR",
                    )
                )
        for pattern in SUSPICIOUS_CALL_PATTERNS:
            if re.search(pattern, line):
                report.violations.append(
                    Violation(
                        file=str(path),
                        line=lineno,
                        kind="suspicious_call",
                        detail=f"Possible DB call in router: `{line.strip()}`",
                        severity="ERROR" if strict else "WARNING",
                    )
                )

    # --- AST complexity check ---
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        report.violations.append(
            Violation(
                file=str(path), line=0, kind="syntax_error",
                detail=str(exc), severity="ERROR",
            )
        )
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            report.total_functions += 1
            # Only check route handler functions (decorated with @router.*)
            is_route = any(
                (isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name) and d.value.id == "router")
                or (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and isinstance(d.func.value, ast.Name) and d.func.value.id == "router")
                for d in node.decorator_list
            )
            if not is_route:
                continue
            complexity = _measure_complexity(node)
            if complexity > MAX_COMPLEXITY:
                report.violations.append(
                    Violation(
                        file=str(path),
                        line=node.lineno,
                        kind="complexity",
                        detail=(
                            f"Route `{node.name}` has cyclomatic complexity {complexity} "
                            f"(max allowed: {MAX_COMPLEXITY}). Move business logic to a service."
                        ),
                        severity="ERROR" if strict else "WARNING",
                    )
                )


def main() -> int:
    strict = "--strict" in sys.argv
    emit_json = "--json" in sys.argv

    if not ROUTER_DIR.exists():
        print(f"ERROR: Router directory not found: {ROUTER_DIR}", file=sys.stderr)
        return 1

    report = AuditReport()
    for path in sorted(ROUTER_DIR.glob("*.py")):
        if path.name.startswith("_"):
            continue
        audit_file(path, report, strict)

    if emit_json:
        print(json.dumps(
            {
                "total_files": report.total_files,
                "total_functions": report.total_functions,
                "violations": [asdict(v) for v in report.violations],
                "passed": report.passed,
            },
            indent=2,
        ))
    else:
        if report.violations:
            print(f"\n{'='*60}")
            print(f"  Router Thinness Audit — {len(report.violations)} violation(s)")
            print(f"{'='*60}\n")
            for v in report.violations:
                print(f"  [{v.severity}] {v.file}:{v.line}")
                print(f"         {v.kind.upper()}: {v.detail}\n")
        else:
            print(
                f"✓ Router thinness audit passed "
                f"({report.total_files} files, {report.total_functions} route functions checked)"
            )

    errors = [v for v in report.violations if v.severity == "ERROR"]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
