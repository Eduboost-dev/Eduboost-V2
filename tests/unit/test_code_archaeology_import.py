import importlib
from pathlib import Path


def test_import_modules():
    # ensure package imports cleanly
    mod = importlib.import_module("app.tools.code_archaeology")
    assert hasattr(mod, "doc_ingester")
    assert hasattr(mod, "narrative_generator")


def test_basic_doc_ingester_parse_frontmatter():
    mod = importlib.import_module("app.tools.code_archaeology.doc_ingester")
    fm, body = mod._parse_frontmatter("---\ntitle: Test\n---\nHello")
    assert fm.get("title") == "Test"
    assert "Hello" in body


def test_narrative_generation_template():
    ng = importlib.import_module("app.tools.code_archaeology.narrative_generator")
    timeline = {"repo": "X", "epochs": [{"name": "Foundation", "commit_count": 3}]}
    report = ng.generate_narrative_template(timeline)
    assert report.title.startswith("Code Archaeology")
