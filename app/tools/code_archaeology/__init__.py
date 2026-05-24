"""Code Archaeology tools package (integrated from temp/Git).

Expose lightweight helpers for test-time imports.
"""
from . import doc_ingester as doc_ingester
from . import git_ingester as git_ingester
from . import narrative_generator as narrative_generator
from . import sync_engine as sync_engine
from pathlib import Path

# Path to bundled templates
TEMPLATES_PATH = Path(__file__).parent / "templates"

__all__ = ["doc_ingester", "git_ingester", "narrative_generator", "sync_engine", "TEMPLATES_PATH"]
