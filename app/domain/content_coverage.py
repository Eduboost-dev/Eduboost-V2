"""Domain types for Content Factory coverage targets."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContentLayer(str, Enum):
    TOPIC_MAP = "topic_map"
    DIAGNOSTIC_ITEMS = "diagnostic_items"
    LESSONS = "lessons"
    ASSESSMENT_BLUEPRINTS = "assessment_blueprints"
    STUDY_PLAN_TEMPLATES = "study_plan_templates"


class CoverageTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_id: str = Field(min_length=1)
    caps_ref: str = Field(min_length=1)
    targets: dict[str, int] = Field(default_factory=dict)


class CoverageTargetRegistryDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    targets: list[CoverageTarget]
