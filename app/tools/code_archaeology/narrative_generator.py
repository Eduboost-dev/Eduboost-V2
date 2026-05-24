"""
narrative_generator.py
-----------------------
Transforms a SyncedTimeline into a richly-written "Code Archaeology" expedition
log.  Template mode (offline) is provided for deterministic output.
"""

from __future__ import annotations

import json
import os
import textwrap
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class NarrativeChapter:
    epoch_name:    str
    heading:       str
    body:          str
    pull_quote:    str
    risk_callout:  Optional[str]
    themes:        list[str]
    velocity_note: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NarrativeReport:
    title:    str
    tagline:  str
    chapters: list[NarrativeChapter] = field(default_factory=list)
    epilogue: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["chapters"] = [c.to_dict() for c in self.chapters]
        return d

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", f"*{self.tagline}*", ""]
        for ch in self.chapters:
            lines += [f"## {ch.heading}", "", ch.body, "", f"> {ch.pull_quote}", ""]
        lines += ["## Epilogue", "", self.epilogue]
        return "\n".join(lines)


def generate_narrative_template(timeline: dict) -> NarrativeReport:
    epochs = timeline.get("epochs", [])
    chapters = []
    for epoch in epochs:
        name = epoch.get("name", "epoch")
        heading = f"Chapter: {name}"
        body = f"This epoch ({name}) had {epoch.get('commit_count',0)} commits."
        pull = f"{epoch.get('commit_count',0)} commits — {name}."
        chapters.append(NarrativeChapter(epoch_name=name, heading=heading, body=body, pull_quote=pull, risk_callout=None, themes=epoch.get('dominant_themes', []), velocity_note=""))

    return NarrativeReport(title=f"Code Archaeology: {timeline.get('repo','Repo')}", tagline="An expedition.", chapters=chapters, epilogue="Epilogue.", metadata={"mode":"template"})


def generate_narrative(timeline: dict, mode: str = "auto") -> NarrativeReport:
    return generate_narrative_template(timeline)


def save_narrative_json(report: NarrativeReport, output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"[narrative] Saved JSON → {output_path}")
