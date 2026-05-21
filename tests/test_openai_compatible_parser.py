from llmspy.models import CapturedHTTPExchange
from llmspy.parsers.openai_compatible import OpenAICompatibleParser


def test_openai_compatible_parser():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="localhost",
        path="/v1/chat/completions",
        request_body='{"model":"local","messages":[{"role":"user","content":"Hi"}]}',
        response_body='{"choices":[{"message":{"content":"Hello"}}]}',
    )
    parser = OpenAICompatibleParser()
    assert parser.can_handle(
        exchange.host, exchange.path, exchange.request_body, exchange.response_body
    )
    assert parser.normalize(exchange).model == "local"
