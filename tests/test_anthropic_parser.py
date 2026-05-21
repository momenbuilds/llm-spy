from llmspy.models import CapturedHTTPExchange
from llmspy.parsers.anthropic import AnthropicParser


def test_anthropic_parser_request_response():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="api.anthropic.com",
        path="/v1/messages",
        request_body='{"model":"claude-3-5-haiku","system":"Be brief","messages":[{"role":"user","content":"Hi"}],"tools":[{"name":"x"}]}',
        response_body='{"content":[{"type":"text","text":"Hello"}],"stop_reason":"end_turn","usage":{"input_tokens":5,"output_tokens":2}}',
        response_status=200,
    )
    call = AnthropicParser().normalize(exchange)
    assert call.system_prompt == "Be brief"
    assert call.response_content == "Hello"
    assert call.total_tokens == 7
