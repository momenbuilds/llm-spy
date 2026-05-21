from __future__ import annotations

import asyncio
import time
from pathlib import Path

from llmspy.display import TerminalDisplay
from llmspy.models import CapturedHTTPExchange, ParsedCall
from llmspy.parsers import registry
from llmspy.pricing import apply_pricing
from llmspy.safety import scan_injection, scan_pii
from llmspy.storage import Storage
from llmspy.utils import safe_json_dumps


def enrich_call(call: ParsedCall, storage: Storage | None = None) -> ParsedCall:
    text = safe_json_dumps(call.raw_request) + "\n" + (call.response_content or "")
    pii = scan_pii(text, "request/response")
    injection = scan_injection(text, "request/response")
    call.has_pii_warning = bool(pii)
    call.pii_findings = [finding.model_dump() for finding in pii]
    call.has_injection_warning = bool(injection)
    call.injection_findings = [finding.model_dump() for finding in injection]
    return apply_pricing(call, storage)


def normalize_exchange(
    exchange: CapturedHTTPExchange, session_id: str | None = None, storage: Storage | None = None
) -> ParsedCall:
    parser = registry.get_parser(
        exchange.host, exchange.path, exchange.request_body, exchange.response_body
    )
    call = parser.normalize(exchange)
    call.session_id = session_id
    return enrich_call(call, storage)


class MitmproxyAddon:
    def __init__(
        self, db_path: str, session_id: str, verbose: bool = False, no_display: bool = False
    ):
        self.storage = Storage(Path(db_path))
        self.session_id = session_id
        self.display = None if no_display else TerminalDisplay(verbose=verbose)
        self.started: dict[str, float] = {}

    def request(self, flow):  # pragma: no cover - exercised under mitmproxy runtime
        self.started[flow.id] = time.perf_counter()

    def response(self, flow):  # pragma: no cover - exercised under mitmproxy runtime
        latency = int((time.perf_counter() - self.started.get(flow.id, time.perf_counter())) * 1000)
        exchange = CapturedHTTPExchange(
            method=flow.request.method,
            host=flow.request.host,
            path=flow.request.path,
            request_headers=dict(flow.request.headers),
            request_body=flow.request.get_text(strict=False),
            response_status=flow.response.status_code if flow.response else None,
            response_headers=dict(flow.response.headers) if flow.response else {},
            response_body=flow.response.get_text(strict=False) if flow.response else None,
            latency_ms=latency,
        )
        call = normalize_exchange(exchange, self.session_id, self.storage)
        self.storage.insert_call(call)
        if self.display:
            budget_value = self.storage.load_budget("daily")
            daily_budget = float(budget_value) if budget_value else None
            self.display.show_call(
                call, daily_budget=daily_budget, daily_cost=self.storage.daily_cost()
            )


async def run_mitmproxy(
    host: str,
    port: int,
    db_path: str,
    session_id: str,
    verbose: bool = False,
    no_display: bool = False,
) -> None:
    from mitmproxy.options import Options
    from mitmproxy.tools.dump import DumpMaster

    opts = Options(listen_host=host, listen_port=port, ssl_insecure=True)
    master = DumpMaster(opts, with_termlog=verbose, with_dumper=False)
    master.addons.add(MitmproxyAddon(db_path, session_id, verbose, no_display))
    try:
        await master.run()
    except KeyboardInterrupt:
        master.shutdown()


def serve_proxy(
    host: str,
    port: int,
    db_path: str,
    session_id: str,
    verbose: bool = False,
    no_display: bool = False,
) -> None:
    asyncio.run(run_mitmproxy(host, port, db_path, session_id, verbose, no_display))
