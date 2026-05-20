from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/release/auth_route_logout_delegate_status.json"
OUT_MD = ROOT / "docs/release/auth_route_logout_delegate_status.md"
TARGETS = ("logout", "revoke_all_tokens")
PARAM = "auth_service: AuthApplicationService = Depends(get_auth_application_service)"


@dataclass(frozen=True)
class TargetStatus:
    route: str
    exists: bool
    has_auth_service_param: bool
    delegates_to_service: bool
    direct_cookie_or_token_logic: list[str]
    passed: bool


@dataclass(frozen=True)
class Status:
    generated_at: str
    current_commit: str
    status: str
    targets: list[TargetStatus]
    blockers: list[str]


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def strip_malformed_auth_service_param_lines(source: str) -> str:
    bad = re.compile(r"^\s*,?\s*auth_service:\s*AuthApplicationService\s*=\s*Depends\(get_auth_application_service\)\s*,?\s*$")
    lines = [line for line in source.splitlines() if not bad.match(line)]
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def parse_source(source: str | None = None) -> ast.AST:
    return ast.parse(source if source is not None else strip_malformed_auth_service_param_lines(read(AUTH_ROUTER)) or "\n")


def find_func(tree: ast.AST, name: str) -> ast.AsyncFunctionDef | ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == name:
            return node
    return None


def call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        value = func.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        return ".".join(reversed(parts))
    if isinstance(func, ast.Name):
        return func.id
    return ""


def has_auth_service_param(node: ast.AsyncFunctionDef | ast.FunctionDef | None) -> bool:
    if node is None:
        return False
    args = list(node.args.args) + list(node.args.kwonlyargs)
    return any(arg.arg == "auth_service" for arg in args)


def delegates(node: ast.AsyncFunctionDef | ast.FunctionDef | None, route: str) -> bool:
    if node is None:
        return False
    return any(isinstance(child, ast.Call) and call_name(child) == f"auth_service.{route}" for child in ast.walk(node))


def direct_logic(node: ast.AsyncFunctionDef | ast.FunctionDef | None) -> list[str]:
    if node is None:
        return []
    found: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            name = call_name(child)
            if name.endswith("delete_cookie") or name.endswith("set_cookie"):
                found.add(name)
            if name in {"consume_refresh_token", "revoke_all_refresh_tokens", "create_access_token"}:
                found.add(name)
    return sorted(found)


def insert_import(source: str, line: str) -> str:
    if line in source:
        return source
    lines = source.splitlines()
    i = 0
    if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
        quote = lines[0][:3]
        i = 1
        while i < len(lines) and not lines[i].endswith(quote):
            i += 1
        i = min(i + 1, len(lines))
    while i < len(lines) and (lines[i].strip() == "" or lines[i].startswith("from __future__")):
        i += 1
    lines.insert(i, line)
    return "\n".join(lines) + "\n"


def provider_import() -> str:
    deps = ROOT / "app/api_v2_deps"
    if deps.exists():
        for path in deps.rglob("*.py"):
            text = read(path)
            if "get_auth_application_service" in text:
                module = path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
                return f"from {module} import get_auth_application_service"
    return "from app.api_v2_deps.auth_service import get_auth_application_service"


def ensure_imports(source: str) -> str:
    if "from app.services.auth_application_service import AuthApplicationService" not in source:
        source = insert_import(source, "from app.services.auth_application_service import AuthApplicationService")
    if "import get_auth_application_service" not in source and "def get_auth_application_service" not in source:
        source = insert_import(source, provider_import())
    if not re.search(r"(?m)^from fastapi import .*\bDepends\b", source):
        source = insert_import(source, "from fastapi import Depends")
    return source


def signature_end(lines: list[str], start: int) -> int:
    depth = 0
    started = False
    for i in range(start, len(lines)):
        line = lines[i]
        if "def " in line:
            started = True
        depth += line.count("(") - line.count(")")
        if started and depth <= 0 and line.rstrip().endswith(":"):
            return i
    return start


def ensure_param(source: str, route: str) -> str:
    tree = parse_source(source)
    node = find_func(tree, route)
    if node is None or has_auth_service_param(node):
        return source
    lines = source.splitlines()
    start = node.lineno - 1
    end = signature_end(lines, start)
    if start == end:
        idx = lines[start].rfind(")")
        if idx >= 0:
            lines[start] = lines[start][:idx] + f", {PARAM}" + lines[start][idx:]
    else:
        base_indent = re.match(r"^(\s*)", lines[start]).group(1)
        lines.insert(end, f"{base_indent}    {PARAM},")
    return "\n".join(lines) + "\n"


def body_kwargs(node: ast.AsyncFunctionDef | ast.FunctionDef) -> str:
    args = list(node.args.args) + list(node.args.kwonlyargs)
    names = [arg.arg for arg in args if arg.arg != "auth_service"]
    return ", ".join(f"{name}={name}" for name in names)


def replace_body(source: str, route: str) -> str:
    tree = parse_source(source)
    node = find_func(tree, route)
    if node is None or delegates(node, route):
        return source
    lines = source.splitlines()
    start = node.body[0].lineno - 1 if node.body else node.lineno
    end = node.end_lineno or start + 1
    indent = re.match(r"^(\s*)", lines[start]).group(1) if start < len(lines) else "    "
    kwargs = body_kwargs(node)
    call = f"return await auth_service.{route}({kwargs})" if kwargs else f"return await auth_service.{route}()"
    return "\n".join(lines[:start] + [indent + call] + lines[end:]) + "\n"


def repair() -> Status:
    source = strip_malformed_auth_service_param_lines(read(AUTH_ROUTER))
    source = ensure_imports(source)
    parse_source(source)
    for route in TARGETS:
        source = ensure_param(source, route)
        parse_source(source)
        source = replace_body(source, route)
        parse_source(source)
    AUTH_ROUTER.write_text(source, encoding="utf-8")
    return write_status()


def build_status() -> Status:
    tree = parse_source()
    targets: list[TargetStatus] = []
    blockers: list[str] = []
    for route in TARGETS:
        node = find_func(tree, route)
        exists = node is not None
        has_param = has_auth_service_param(node)
        has_delegate = delegates(node, route)
        direct = direct_logic(node)
        passed = exists and has_param and has_delegate and not direct
        if not passed:
            blockers.append(f"{route} route is not fully delegated to auth service")
        targets.append(TargetStatus(route, exists, has_param, has_delegate, direct, passed))
    return Status(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        current_commit=current_commit(),
        status="auth-route-logout-delegation-passing" if not blockers else "auth-route-logout-delegation-not-proven",
        targets=targets,
        blockers=blockers,
    )


def write_status() -> Status:
    status = build_status()
    OUT_JSON.write_text(json.dumps(asdict(status), indent=2), encoding="utf-8")
    lines = [
        "# Auth Route Logout/Revoke Delegation Status",
        "",
        f"Generated at: `{status.generated_at}`",
        f"Commit: `{status.current_commit}`",
        "",
        f"**Status:** `{status.status}`",
        "",
        "| Route | Exists | Auth service param | Delegates | Direct route logic | Passed |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for t in status.targets:
        lines.append(f"| `{t.route}` | {t.exists} | {t.has_auth_service_param} | {t.delegates_to_service} | `{', '.join(t.direct_cookie_or_token_logic) or '-'}` | {t.passed} |")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {b}" for b in status.blockers)
    if not status.blockers:
        lines.append("- None")
    lines.extend(["", "## No false-closure rules", "", "- Route body delegation does not prove HTTP behavior.", "- Logout/revoke HTTP proof remains separate.", "- This cleanup does not approve beta release.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    return status
