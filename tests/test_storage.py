from llmspy.models import ParsedCall


def test_storage_insert_fetch_list_search_clear_diff(store):
    a = store.insert_call(
        ParsedCall(provider="openai", model="gpt-4o-mini", response_content="Paris")
    )
    b = store.insert_call(ParsedCall(provider="openai", model="gpt-4o", response_content="Lyon"))
    assert store.get_call(a.id).response_content == "Paris"
    assert len(store.list_calls()) == 2
    assert store.search_calls("Paris")[0].id == a.id
    assert "model" in store.diff_calls(a.id, b.id)
    store.clear_calls()
    assert store.list_calls() == []
