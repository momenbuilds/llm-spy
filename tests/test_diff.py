from llmspy.models import ParsedCall


def test_diff(store):
    a = store.insert_call(ParsedCall(model="a"))
    b = store.insert_call(ParsedCall(model="b"))
    assert store.diff_calls(a.id, b.id)["model"]["a"] == "a"
