"""Real LLM provider placeholder.

The implementation intentionally fails closed until a reviewed provider
adapter is added in a later batch.
"""
from __future__ import annotations

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GeneratedLesson,
    LessonGenerationRequest,
)


class LLMContentGenerationProvider:
    provider_name = "llm"
    model_name = "disabled-unconfigured"

    async def generate_diagnostic_items(
        self,
        request: DiagnosticGenerationRequest,
    ) -> list[GeneratedDiagnosticItem]:
        raise RuntimeError("LLM content generation provider is not configured.")

    async def generate_lessons(
        self,
        request: LessonGenerationRequest,
    ) -> list[GeneratedLesson]:
        raise RuntimeError("LLM content generation provider is not configured.")

    async def generate_assessment_blueprints(
        self,
        request: dict,
    ) -> list[dict]:
        raise RuntimeError("LLM content generation provider is not configured.")

    async def generate_study_plan_templates(
        self,
        request: dict,
    ) -> list[dict]:
        raise RuntimeError("LLM content generation provider is not configured.")
