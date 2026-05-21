from typer.testing import CliRunner

from llmspy.cli import app


def test_cli_help():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Local-first" in result.output


def test_cli_history_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_SPY_DB_PATH", str(tmp_path / "x.db"))
    result = CliRunner().invoke(app, ["history"])
    assert result.exit_code == 0
    assert "No captured calls" in result.output


def test_cli_doctor(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_SPY_HOME", str(tmp_path))
    monkeypatch.setenv("LLM_SPY_DB_PATH", str(tmp_path / "doctor.db"))
    result = CliRunner().invoke(
        app, ["doctor", "--proxy-port", "18080", "--dashboard-port", "14000"]
    )
    assert result.exit_code == 0
    assert "Dashboard templates" in result.output
    assert "Helpful next commands" in result.output
