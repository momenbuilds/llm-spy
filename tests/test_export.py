from llmspy.models import ParsedCall


def test_exports(store):
    store.insert_call(ParsedCall(provider="openai", model="gpt-4o-mini", response_content="ok"))
    assert store.export_json()[0]["provider"] == "openai"
    assert "provider,model" in store.export_csv()
    assert "promptfoo" in store.export_promptfoo()
