import json

from llmspy.ci import run_ci


def test_ci_mode_from_export(tmp_path):
    path = tmp_path / "calls.json"
    path.write_text(json.dumps([{"total_cost_usd": 2, "has_pii_warning": True}]))
    code, messages = run_ci(max_cost=1, fail_on_pii=True, input_file=path)
    assert code == 1
    assert len(messages) == 2
