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


def test_anthropic_parser_handles_system_blocks_and_tools():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="api.anthropic.com",
        path="/v1/messages",
        request_body="""
        {
          "model": "claude-3-5-sonnet",
          "system": [
            {"type": "text", "text": "Follow the policy."},
            {"type": "text", "text": "Use tools only when needed."}
          ],
          "messages": [{"role": "user", "content": "Check the weather"}],
          "tools": [
            {
              "name": "get_weather",
              "description": "Look up forecast",
              "input_schema": {"type": "object"}
            }
          ],
          "temperature": 0.2,
          "max_tokens": 256
        }
        """,
        response_body="""
        {
          "content": [
            {"type": "tool_use", "id": "toolu_123", "name": "get_weather", "input": {"city": "Sydney"}},
            {"type": "text", "text": "It is 18C and clear."}
          ],
          "stop_reason": "tool_use",
          "usage": {"input_tokens": 17, "output_tokens": 9}
        }
        """,
        response_status=200,
    )
    call = AnthropicParser().normalize(exchange)
    assert call.model == "claude-3-5-sonnet"
    assert call.system_prompt == "Follow the policy.\nUse tools only when needed."
    assert call.tools == [
        {
            "name": "get_weather",
            "description": "Look up forecast",
            "input_schema": {"type": "object"},
        }
    ]
    assert call.parameters == {"temperature": 0.2, "max_tokens": 256}
    assert call.response_content == "It is 18C and clear."
    assert call.finish_reason == "tool_use"
    assert call.prompt_tokens == 17
    assert call.completion_tokens == 9
    assert call.total_tokens == 26


def test_anthropic_parser_joins_multiple_text_blocks():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="api.anthropic.com",
        path="/v1/messages",
        request_body='{"model":"claude-3-5-haiku","messages":[{"role":"user","content":"Hi"}]}',
        response_body="""
        {
          "content": [
            {"type": "text", "text": "Hello"},
            {"type": "thinking", "text": "hidden"},
            {"type": "text", "text": "How can I help?"}
          ],
          "stop_reason": "end_turn",
          "usage": {"input_tokens": 3, "output_tokens": 6}
        }
        """,
        response_status=200,
    )
    call = AnthropicParser().normalize(exchange)
    assert call.response_content == "Hello\nHow can I help?"
    assert call.finish_reason == "end_turn"
    assert call.total_tokens == 9


def test_anthropic_parser_falls_back_for_malformed_response_body():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="api.anthropic.com",
        path="/v1/messages",
        request_body='{"model":"claude-3-5-haiku","messages":[{"role":"user","content":"Hi"}]}',
        response_body="not-json",
        response_status=502,
    )
    call = AnthropicParser().normalize(exchange)
    assert call.provider == "anthropic"
    assert call.model == "claude-3-5-haiku"
    assert call.response_content == "not-json"
    assert call.raw_response == "not-json"
    assert call.error is None


def test_anthropic_parser_surfaces_error_message_from_response():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="api.anthropic.com",
        path="/v1/messages",
        request_body='{"model":"claude-3-5-haiku","messages":[{"role":"user","content":"Hi"}]}',
        response_body='{"error":{"type":"invalid_request_error","message":"messages: field required"}}',
        response_status=400,
    )
    call = AnthropicParser().normalize(exchange)
    assert call.response_content is None
    assert call.error == "messages: field required"
