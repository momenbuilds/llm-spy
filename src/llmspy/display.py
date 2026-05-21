from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from llmspy.models import ParsedCall
from llmspy.utils import safe_json_dumps, truncate


class TerminalDisplay:
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.verbose = verbose
        self.count = 0

    def show_startup(self, host: str, port: int, db: str) -> None:
        self.console.print(
            Panel.fit(
                f"[bold]llm-spy proxy[/bold]\nListening on http://{host}:{port}\nDB: {db}\n\nRun your app with:\n[cyan]HTTPS_PROXY=http://{host}:{port} HTTP_PROXY=http://{host}:{port} python app.py[/cyan]\n\nHTTPS interception uses mitmproxy certificates. If HTTPS calls are not decoded yet, trust the mitmproxy CA certificate shown by mitmproxy or visit http://mitm.it through this proxy.",
                title="See every LLM call your app makes. Zero config. Stays local.",
            )
        )

    def show_call(
        self, call: ParsedCall, daily_budget: float | None = None, daily_cost: float | None = None
    ) -> None:
        self.count += 1
        cost = "unknown pricing" if call.total_cost_usd is None else f"${call.total_cost_usd:.6f}"
        header = f"CALL #{self.count} · {call.provider} · {call.model or 'unknown model'} · {call.latency_ms or 0}ms · {cost}"
        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold cyan", width=12)
        table.add_column()
        if call.system_prompt:
            table.add_row("SYSTEM", truncate(call.system_prompt))
        user_text = "\n".join(
            str(m.get("content", "")) for m in call.messages if m.get("role") != "system"
        )
        if user_text:
            table.add_row("USER", truncate(user_text))
        if call.response_content:
            table.add_row("RESPONSE", truncate(call.response_content))
        table.add_row(
            "TOKENS",
            f"prompt: {call.prompt_tokens or '?'}  completion: {call.completion_tokens or '?'}  total: {call.total_tokens or '?'}{' (estimated)' if call.estimated_tokens else ''}",
        )
        table.add_row(
            "COST",
            f"input: {call.input_cost_usd if call.input_cost_usd is not None else '?'}  output: {call.output_cost_usd if call.output_cost_usd is not None else '?'}  total: {cost}",
        )
        pii = (
            "none" if not call.has_pii_warning else ", ".join(f["type"] for f in call.pii_findings)
        )
        inj = (
            "none"
            if not call.has_injection_warning
            else ", ".join(f["type"] for f in call.injection_findings)
        )
        table.add_row("SAFETY", f"PII: {pii}\nPrompt injection: {inj}")
        if call.error:
            table.add_row("ERROR", f"[red]{call.error}[/red]")
        self.console.print(
            Panel(table, title=header, border_style="green" if not call.error else "red")
        )
        if daily_budget is not None and daily_cost is not None and daily_cost > daily_budget:
            self.console.print(
                f"[bold yellow]Budget warning:[/bold yellow] today is ${daily_cost:.4f}, above daily budget ${daily_budget:.4f}"
            )
        if self.verbose:
            self.console.print(Syntax(safe_json_dumps(call.raw_request), "json", word_wrap=True))
            self.console.print(Syntax(safe_json_dumps(call.raw_response), "json", word_wrap=True))
