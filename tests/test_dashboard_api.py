from fastapi.testclient import TestClient

from llmspy.dashboard import create_app
from llmspy.models import ParsedCall


def test_dashboard_api_routes(store):
    store.insert_call(ParsedCall(provider="openai", model="gpt-4o-mini"))
    client = TestClient(create_app(store))
    assert client.get("/api/stats").json()["total_calls"] == 1
    assert len(client.get("/api/calls").json()) == 1


def test_dashboard_pages_render(store):
    call = store.insert_call(
        ParsedCall(provider="openai", model="gpt-4o-mini", response_content="ok")
    )
    client = TestClient(create_app(store))
    for path in ["/", "/calls", f"/calls/{call.id}", "/sessions", "/stats", "/settings", "/diff"]:
        response = client.get(path)
        assert response.status_code == 200, path
    assert client.get(f"/diff?call_a={call.id}&call_b={call.id}").status_code == 200
    settings_response = client.post("/settings", data={"daily": "1.23"})
    assert settings_response.status_code == 200
    assert "Saved" in settings_response.text
