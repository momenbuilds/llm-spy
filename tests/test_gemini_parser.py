from llmspy.models import CapturedHTTPExchange
from llmspy.parsers.gemini import GeminiParser


def test_gemini_parser():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="generativelanguage.googleapis.com",
        path="/v1beta/models/gemini-1.5-flash:generateContent",
        request_body='{"contents":[{"role":"user","parts":[{"text":"Hi"}]}]}',
        response_body='{"candidates":[{"content":{"parts":[{"text":"Hello"}]},"finishReason":"STOP"}],"usageMetadata":{"promptTokenCount":2,"candidatesTokenCount":2,"totalTokenCount":4}}',
    )
    call = GeminiParser().normalize(exchange)
    assert call.provider == "gemini"
    assert call.model == "gemini-1.5-flash"
    assert call.response_content == "Hello"
