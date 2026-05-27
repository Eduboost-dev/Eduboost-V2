"""Domain types for file-backed Content Factory scopes."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContentScopeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ContentScope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope_id: str = Field(min_length=1)
    grade: int = Field(ge=0, le=12)
    subject_code: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=8)
    curriculum: str = Field(min_length=1)
    status: ContentScopeStatus
    topic_map_path: str = Field(min_length=1)
    caps_refs: list[str] = Field(default_factory=list)


class ContentScopeRegistryDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    scopes: list[ContentScope]
