from llmspy.models import CapturedHTTPExchange
from llmspy.parsers.registry import ParserRegistry


def test_unknown_provider_fallback():
    exchange = CapturedHTTPExchange(
        method="GET", host="example.com", path="/x", request_body="not json", response_body="ok"
    )
    parser = ParserRegistry().get_parser(
        exchange.host, exchange.path, exchange.request_body, exchange.response_body
    )
    call = parser.normalize(exchange)
    assert call.provider == "unknown"
    assert call.raw_request == "not json"
