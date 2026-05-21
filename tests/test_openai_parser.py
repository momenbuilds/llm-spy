from llmspy.models import CapturedHTTPExchange
from llmspy.parsers.openai import OpenAIParser


def test_openai_parser_request_response():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="api.openai.com",
        path="/v1/chat/completions",
        request_body='{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hi"}],"temperature":0}',
        response_body='{"choices":[{"message":{"content":"Hello"},"finish_reason":"stop"}],"usage":{"prompt_tokens":3,"completion_tokens":2,"total_tokens":5}}',
        response_status=200,
    )
    call = OpenAIParser().normalize(exchange)
    assert call.provider == "openai"
    assert call.model == "gpt-4o-mini"
    assert call.response_content == "Hello"
    assert call.total_tokens == 5


def test_openai_responses_api_parser():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="api.openai.com",
        path="/v1/responses",
        request_body='{"model":"gpt-4.1-mini","instructions":"Be concise","input":"What is Paris?","tools":[{"type":"web_search_preview"}],"temperature":0}',
        response_body='{"output":[{"type":"message","content":[{"type":"output_text","text":"Paris is France’s capital."}]}],"usage":{"input_tokens":10,"output_tokens":5,"total_tokens":15}}',
        response_status=200,
    )
    call = OpenAIParser().normalize(exchange)
    assert call.provider == "openai"
    assert call.system_prompt == "Be concise"
    assert call.messages == [{"role": "user", "content": "What is Paris?"}]
    assert call.tools == [{"type": "web_search_preview"}]
    assert call.response_content == "Paris is France’s capital."
    assert call.prompt_tokens == 10
