from llmspy.safety.pii import scan_text


def test_pii_scanner():
    findings = scan_text(
        "email person@example.com phone 415-555-1212 key sk-abcdefghijklmnopqrst "
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456 "
        "jwt eyJabc.def123.ghi456"
    )
    assert {f.type for f in findings} >= {"email", "phone", "openai_key", "bearer_token", "jwt"}
