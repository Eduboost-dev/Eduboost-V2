"""Archived legacy API entrypoint compatibility shim."""
from __future__ import annotations

from importlib import import_module

from fastapi import FastAPI, HTTPException

_canonical_app = import_module("app.api_v2").app

app = FastAPI(
    title=_canonical_app.title,
    version=_canonical_app.version,
    description=_canonical_app.description,
    docs_url=_canonical_app.docs_url,
    redoc_url=_canonical_app.redoc_url,
)
app.router.routes = list(_canonical_app.router.routes)
app.exception_handlers.update(_canonical_app.exception_handlers)


async def legacy_lesson_generate_gone() -> None:
    """Fail closed for the retired V1 lesson-generation endpoint."""

    raise HTTPException(
        status_code=410,
        detail="Legacy lesson generation moved to /api/v2/lessons/generate.",
    )


def _has_legacy_lesson_generate_route() -> bool:
    return any(getattr(route, "path", None) == "/api/v1/lessons/generate" for route in app.routes)


if not _has_legacy_lesson_generate_route():
    app.add_api_route(
        "/api/v1/lessons/generate",
        legacy_lesson_generate_gone,
        methods=["POST"],
        include_in_schema=False,
        name="legacy_lesson_generate_gone",
    )
