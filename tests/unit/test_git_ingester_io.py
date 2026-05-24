from pathlib import Path

from app.tools.code_archaeology import git_ingester


def test_save_and_load_result_json(tmp_path: Path):
    # create a minimal GitIngestionResult
    result = git_ingester.GitIngestionResult(
        commits=[],
        author_profiles=[],
        churn_index=git_ingester.ChurnIndex(),
        hotspot_ranking=git_ingester.HotspotRanking(),
        burst_clusters=[],
    )
    out = tmp_path / "result.json"
    git_ingester.save_result_json(result, out)
    data = git_ingester.load_result_json(out)
    assert isinstance(data, dict)
    assert "commits" in data and "author_profiles" in data
