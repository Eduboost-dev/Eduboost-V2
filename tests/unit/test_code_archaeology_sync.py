from app.tools.code_archaeology import sync_engine


def test_build_synced_timeline_minimal():
    commits = [
        {
            "hash": "abcd1234",
            "short": "abcd123",
            "date": "2024-01-01T00:00:00+00:00",
            "author": "Alice",
            "subject": "feat: add initial module",
            "body": "Initial work",
            "files_changed": ["app/__init__.py"],
            "stats": {"insertions": 10, "deletions": 0},
        }
    ]

    docs = [
        {
            "path": "docs/intro.md",
            "doc_type": "tracking",
            "title": "Introduction",
            "metadata": {},
            "sections": [{"heading": "Overview", "content": "initial setup and bootstrap"}],
            "sentiment": {"risk": 0.0},
        }
    ]

    timeline = sync_engine.build_synced_timeline(commits, docs, repo_name="testrepo")
    assert timeline.repo == "testrepo"
    assert timeline.total_commits == 1
    assert isinstance(timeline.epochs, list)
