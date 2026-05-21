from llmspy.models import CapturedHTTPExchange
from llmspy.parsers.ollama import OllamaParser


def test_ollama_parser():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="localhost",
        path="/api/generate",
        request_body='{"model":"llama3","prompt":"Hi"}',
        response_body='{"response":"Hello","prompt_eval_count":2,"eval_count":2}',
    )
    call = OllamaParser().normalize(exchange)
    assert call.provider == "ollama"
    assert call.response_content == "Hello"
    assert call.total_tokens == 4


def test_ollama_chat_parser():
    exchange = CapturedHTTPExchange(
        method="POST",
        host="localhost",
        path="/api/chat",
        request_body='{"model":"llama3","messages":[{"role":"user","content":"Hi"}],"stream":false}',
        response_body='{"message":{"role":"assistant","content":"Hello chat"},"prompt_eval_count":3,"eval_count":2}',
    )
    call = OllamaParser().normalize(exchange)
    assert call.messages == [{"role": "user", "content": "Hi"}]
    assert call.response_content == "Hello chat"
