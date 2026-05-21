from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from llmspy.export import export_data
from llmspy.models import ReplayOptions
from llmspy.replay import replay_call
from llmspy.storage import Storage
from llmspy.utils import parse_since

BASE = Path(__file__).parent


def create_app(storage: Storage | None = None) -> FastAPI:
    store = storage or Storage()
    app = FastAPI(title="llm-spy dashboard")
    templates = Jinja2Templates(directory=str(BASE / "templates"))
    app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return templates.TemplateResponse(request, "index.html", {"stats": _stats(store)})

    @app.get("/calls", response_class=HTMLResponse)
    def calls_page(request: Request, search: str | None = None):
        return templates.TemplateResponse(
            request,
            "calls.html",
            {"calls": store.list_calls(limit=100, search=search), "search": search or ""},
        )

    @app.get("/calls/{call_id}", response_class=HTMLResponse)
    def call_detail(request: Request, call_id: str):
        return templates.TemplateResponse(
            request, "call_detail.html", {"call": store.get_call(call_id)}
        )

    @app.get("/sessions", response_class=HTMLResponse)
    def sessions_page(request: Request):
        return templates.TemplateResponse(
            request, "sessions.html", {"sessions": store.list_sessions()}
        )

    @app.get("/stats", response_class=HTMLResponse)
    def stats_page(request: Request):
        return templates.TemplateResponse(request, "stats.html", {"stats": _stats(store)})

    @app.get("/settings", response_class=HTMLResponse)
    def settings_page(request: Request):
        return templates.TemplateResponse(
            request, "settings.html", {"daily": store.load_budget("daily")}
        )

    @app.post("/settings", response_class=HTMLResponse)
    def save_settings(request: Request, daily: str = Form("")):
        if daily:
            store.save_budget("daily", daily)
        return templates.TemplateResponse(
            request,
            "settings.html",
            {"daily": store.load_budget("daily"), "saved": True},
        )

    @app.get("/diff", response_class=HTMLResponse)
    def diff_page(request: Request, call_a: str | None = None, call_b: str | None = None):
        diff = store.diff_calls(call_a, call_b) if call_a and call_b else None
        return templates.TemplateResponse(
            request,
            "diff.html",
            {"diff": diff, "call_a": call_a or "", "call_b": call_b or ""},
        )

    @app.get("/api/calls")
    def api_calls(
        since: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        limit: int = 100,
        errors_only: bool = False,
        search: str | None = None,
    ):
        return [
            c.model_dump(mode="json")
            for c in store.list_calls(
                limit=limit,
                provider=provider,
                model=model,
                since=parse_since(since),
                errors_only=errors_only,
                search=search,
            )
        ]

    @app.get("/api/calls/{call_id}")
    def api_call(call_id: str):
        call = store.get_call(call_id)
        return call.model_dump(mode="json") if call else {"error": "not found"}

    @app.get("/api/sessions")
    def api_sessions():
        return store.list_sessions()

    @app.get("/api/stats")
    def api_stats():
        return _stats(store)

    @app.get("/api/cost/today")
    def api_cost_today():
        return {"total_cost_usd": store.daily_cost()}

    @app.get("/api/export")
    def api_export(format: str = "json"):
        media = "application/json" if format == "json" else "text/plain"
        return PlainTextResponse(export_data(store, format), media_type=media)

    @app.post("/api/calls/{call_id}/replay")
    def api_replay(call_id: str, options: ReplayOptions):
        ok, message = replay_call(store, call_id, options)
        return {"ok": ok, "message": message}

    @app.get("/api/diff")
    def api_diff(call_a: str, call_b: str):
        return store.diff_calls(call_a, call_b)

    @app.get("/api/settings")
    def api_settings():
        return {"daily_budget": store.load_budget("daily"), "config": store.list_config()}

    @app.post("/api/settings")
    def api_save_settings(settings: dict):
        if "daily_budget" in settings:
            store.save_budget("daily", str(settings["daily_budget"]))
        for key, value in settings.get("config", {}).items():
            store.save_config(key, str(value))
        return {"ok": True}

    return app


def _stats(store: Storage) -> dict:
    calls = store.list_calls(limit=100000)
    return {
        "total_calls": len(calls),
        "total_cost": sum(c.total_cost_usd or 0 for c in calls),
        "avg_latency": round(sum(c.latency_ms or 0 for c in calls) / len(calls), 2) if calls else 0,
        "total_tokens": sum(c.total_tokens or 0 for c in calls),
        "providers": store.provider_stats(),
        "models": store.model_stats(),
        "pii_warnings": sum(1 for c in calls if c.has_pii_warning),
        "injection_warnings": sum(1 for c in calls if c.has_injection_warning),
    }
