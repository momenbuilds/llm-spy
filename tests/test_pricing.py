from llmspy.models import ParsedCall
from llmspy.pricing import apply_pricing


def test_cost_calculation_and_token_estimation():
    call = ParsedCall(
        provider="openai",
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "hello"}],
        response_content="hi",
    )
    priced = apply_pricing(call)
    assert priced.estimated_tokens is True
    assert priced.total_tokens > 0
    assert priced.total_cost_usd is not None


def test_openai_compatible_known_openai_model_pricing():
    call = ParsedCall(
        provider="openai-compatible",
        model="gpt-4o-mini",
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
    )
    priced = apply_pricing(call)
    assert priced.total_cost_usd is not None


def test_provider_reported_cost_is_used_when_pricing_unknown():
    call = ParsedCall(
        provider="openai-compatible",
        model="deepseek/deepseek-v4-flash",
        prompt_tokens=10,
        completion_tokens=25,
        total_tokens=35,
        raw_response={
            "usage": {
                "cost": 0.000008316,
                "cost_details": {
                    "upstream_inference_prompt_cost": 0.0000014,
                    "upstream_inference_completions_cost": 0.000007,
                },
            }
        },
    )
    priced = apply_pricing(call)
    assert priced.total_cost_usd == 0.00000832
    assert priced.input_cost_usd == 0.0000014
    assert priced.output_cost_usd == 0.000007
