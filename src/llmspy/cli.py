from __future__ import annotations

import json
import shutil
import socket
import sys
import webbrowser
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import llmspy.dashboard.app as dashboard_app
from llmspy import __version__
from llmspy.ci import run_ci
from llmspy.config import APP_DIR, env_bool, env_int, load_environment
from llmspy.dashboard import create_app
from llmspy.diff import print_diff
from llmspy.display import TerminalDisplay
from llmspy.export import export_data
from llmspy.models import ReplayOptions
from llmspy.pricing import update_pricing
from llmspy.proxy import serve_proxy
from llmspy.replay import replay_call
from llmspy.storage import Storage
from llmspy.utils import parse_since

load_environment()
app = typer.Typer(
    help="Local-first LLM API inspector. Like Charles Proxy, but for AI apps.",
    invoke_without_command=True,
    no_args_is_help=True,
)
config_app = typer.Typer(help="Read and write local config")
pricing_app = typer.Typer(help="Pricing cache commands")
app.add_typer(config_app, name="config")
app.add_typer(pricing_app, name="pricing")
console = Console()


@app.callback()
def main(version: bool = typer.Option(False, "--version", help="Show version and exit")):
    if version:
        console.print(__version__)
        raise typer.Exit()


@app.command()
def start(
    port: int = typer.Option(env_int("LLM_SPY_PORT", 8080), "--port", "-p"),
    host: str = typer.Option("localhost", "--host"),
    verbose: bool = typer.Option(env_bool("LLM_SPY_VERBOSE"), "--verbose"),
    no_display: bool = typer.Option(False, "--no-display"),
    session_label: str | None = typer.Option(None, "--session-label"),
):
    """Start the local HTTP/HTTPS proxy."""
    store = Storage()
    session = store.create_session(label=session_label)
    display = TerminalDisplay(verbose=verbose)
    display.show_startup(host, port, str(store.path))
    console.print(
        "[yellow]HTTPS note:[/yellow] trust the mitmproxy CA certificate before expecting HTTPS bodies to be readable. Visit http://mitm.it while using this proxy for platform instructions."
    )
    try:
        serve_proxy(host, port, str(store.path), session.id, verbose, no_display)
    finally:
        store.end_session(session.id)


@app.command()
def stop():
    """Explain safe stop behavior."""
    console.print(
        "llm-spy runs in the foreground by default. Stop it with Ctrl+C in the terminal where it is running."
    )
    console.print(
        "If you launched it under a process manager, stop that process explicitly. llm-spy does not guess and kill unrelated Python processes."
    )


@app.command()
def history(
    last: int = typer.Option(20, "--last"),
    provider: str | None = typer.Option(None, "--provider"),
    model: str | None = typer.Option(None, "--model"),
    since: str | None = typer.Option(None, "--since"),
    json_output: bool = typer.Option(False, "--json"),
    errors_only: bool = typer.Option(False, "--errors-only"),
    search: str | None = typer.Option(None, "--search"),
):
    """Show recent captured calls."""
    store = Storage()
    calls = store.list_calls(last, provider, model, parse_since(since), errors_only, search)
    if json_output:
        console.print(json.dumps([c.model_dump(mode="json") for c in calls], indent=2))
        return
    table = Table(title="llm-spy history")
    for col in ["ID", "Time", "Provider", "Model", "Status", "Latency", "Cost", "Error"]:
        table.add_column(col)
    for c in calls:
        table.add_row(
            c.id,
            c.timestamp.isoformat(),
            c.provider,
            c.model or "",
            str(c.status_code or ""),
            f"{c.latency_ms or ''}ms",
            "unknown" if c.total_cost_usd is None else f"${c.total_cost_usd:.6f}",
            c.error or "",
        )
    console.print(table if calls else "No captured calls yet.")


@app.command()
def clear(yes: bool = typer.Option(False, "--yes", "-y")):
    """Clear local history."""
    if not yes and not typer.confirm("Delete all local llm-spy calls and sessions?"):
        raise typer.Abort()
    Storage().clear_calls()
    console.print("Local history cleared.")


@app.command()
def export(
    format: str = typer.Option("json", "--format"),
    output: Path | None = typer.Option(None, "--output"),
    provider: str | None = typer.Option(None, "--provider"),
    model: str | None = typer.Option(None, "--model"),
    since: str | None = typer.Option(None, "--since"),
    session: str | None = typer.Option(None, "--session"),
):
    """Export captured calls as json, csv, or promptfoo."""
    data = export_data(Storage(), format, provider, model, since, session)
    if output:
        output.write_text(data)
        console.print(f"Wrote {output}")
    else:
        console.print(data)


@app.command()
def cost(
    today: bool = typer.Option(False, "--today"),
    session: str | None = typer.Option(None, "--session"),
    provider: str | None = typer.Option(None, "--provider"),
    model: str | None = typer.Option(None, "--model"),
):
    """Show local estimated cost summary."""
    store = Storage()
    since = None
    if today:
        from datetime import datetime

        since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    summary = store.cost_summary(provider=provider, model=model, since=since, session=session)
    console.print_json(data=summary)


@app.command()
def dashboard(
    port: int = typer.Option(env_int("LLM_SPY_DASHBOARD_PORT", 4000), "--port"),
    open_browser: bool = typer.Option(True, "--open/--no-open"),
):
    """Start the local web dashboard."""
    url = f"http://localhost:{port}"
    if open_browser:
        webbrowser.open(url)
    console.print(f"Dashboard: {url}")
    uvicorn.run(create_app(Storage()), host="localhost", port=port)


@app.command("set-budget")
def set_budget(daily: float = typer.Option(..., "--daily")):
    """Store a local daily budget."""
    Storage().save_budget("daily", str(daily))
    console.print(f"Daily budget set to ${daily:.2f}")


@app.command()
def replay(
    call_id: str,
    model: str | None = typer.Option(None, "--model"),
    temperature: float | None = typer.Option(None, "--temperature"),
    max_tokens: int | None = typer.Option(None, "--max-tokens"),
):
    """Replay a captured call using provider API keys from environment variables."""
    ok, message = replay_call(
        Storage(),
        call_id,
        ReplayOptions(model=model, temperature=temperature, max_tokens=max_tokens),
    )
    console.print(message)
    if not ok:
        raise typer.Exit(1)


@app.command()
def diff(call_id_a: str, call_id_b: str):
    """Compare two captured calls."""
    print_diff(Storage().diff_calls(call_id_a, call_id_b))


@app.command()
def doctor(
    proxy_port: int = typer.Option(8080, "--proxy-port", "--port"),
    dashboard_port: int = typer.Option(4000, "--dashboard-port"),
):
    """Check install health."""
    store = Storage()
    table = Table(title="llm-spy doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")
    table.add_row("Python version", _status(sys.version_info >= (3, 10)), sys.version.split()[0])
    table.add_row("llm-spy version", "info", __version__)
    table.add_row("Home path", _status(APP_DIR.exists()), str(APP_DIR))
    table.add_row("DB path", "info", str(store.path))
    table.add_row("DB initialized", _status(_db_initialized(store)), "schema ready")
    table.add_row("Write permissions", _status(_can_write(APP_DIR)), str(APP_DIR))
    table.add_row(
        f"Proxy port {proxy_port}",
        _status(_port_free(proxy_port)),
        "available" if _port_free(proxy_port) else "in use",
    )
    table.add_row(
        f"Dashboard port {dashboard_port}",
        _status(_port_free(dashboard_port)),
        "available" if _port_free(dashboard_port) else "in use",
    )
    mitmproxy_path = shutil.which("mitmproxy") or shutil.which("mitmdump")
    mitmproxy_ok = bool(mitmproxy_path) or _mitmproxy_importable()
    mitmproxy_detail = mitmproxy_path or (
        "python package importable" if mitmproxy_ok else "not found"
    )
    table.add_row(
        "mitmproxy available",
        _status(mitmproxy_ok),
        mitmproxy_detail,
    )
    ca_path = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem"
    table.add_row(
        "mitmproxy CA cert",
        _status(ca_path.exists()),
        str(ca_path) if ca_path.exists() else "created after first proxy start",
    )
    dashboard_base = Path(dashboard_app.__file__).parent
    table.add_row(
        "Dashboard templates",
        _status((dashboard_base / "templates" / "index.html").exists()),
        str(dashboard_base / "templates"),
    )
    table.add_row(
        "Dashboard static files",
        _status((dashboard_base / "static" / "style.css").exists()),
        str(dashboard_base / "static"),
    )
    config = store.list_config()
    table.add_row("Config entries", "info", json.dumps(config) if config else "none")
    table.add_row("Daily budget", "info", store.load_budget("daily") or "not set")
    console.print(table)
    console.print(
        Panel.fit(
            "\n".join(
                [
                    "Try without an API key: python examples/fake_openai_provider.py",
                    f"Start proxy: llm-spy start --port {proxy_port}",
                    f"Run demo client: HTTP_PROXY=http://localhost:{proxy_port} python examples/openai_compatible_example.py",
                    f"Open dashboard: llm-spy dashboard --port {dashboard_port}",
                    "For HTTPS apps: trust the mitmproxy CA via http://mitm.it while using the proxy.",
                ]
            ),
            title="Helpful next commands",
        )
    )


@app.command("ci")
def ci_command(
    max_cost: float | None = typer.Option(None, "--max-cost"),
    fail_on_pii: bool = typer.Option(False, "--fail-on-pii"),
    fail_on_injection: bool = typer.Option(False, "--fail-on-injection"),
    input_file: Path | None = typer.Option(None, "--input"),
):
    """Run budget and safety gates in CI."""
    code, messages = run_ci(max_cost, fail_on_pii, fail_on_injection, input_file, Storage())
    for message in messages:
        console.print(message)
    raise typer.Exit(code)


@config_app.command("set")
def config_set(key: str, value: str):
    Storage().save_config(key, value)
    console.print(f"{key} set")


@config_app.command("get")
def config_get(key: str):
    value = Storage().load_config(key)
    console.print(value or "")
    if value is None:
        raise typer.Exit(1)


@config_app.command("list")
def config_list():
    console.print_json(data=Storage().list_config())


@pricing_app.command("update")
def pricing_update():
    ok, message = update_pricing(Storage())
    console.print(message)
    if not ok:
        raise typer.Exit(1)


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("localhost", port)) != 0


def _status(ok: bool) -> str:
    return "ok" if ok else "check"


def _db_initialized(store: Storage) -> bool:
    with store.connect() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('calls', 'sessions', 'config')"
        ).fetchall()
    return len(rows) == 3


def _can_write(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".doctor-write-test"
        probe.write_text("ok")
        probe.unlink()
        return True
    except OSError:
        return False


def _mitmproxy_importable() -> bool:
    try:
        import mitmproxy  # noqa: F401

        return True
    except ImportError:
        return False
