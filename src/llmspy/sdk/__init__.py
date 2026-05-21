"""Experimental SDK capture helpers.

Proxy mode is the primary llm-spy experience. SDK mode is intentionally small:
use ``spy_openai`` when a client cannot be routed through HTTP_PROXY.
"""

from llmspy.sdk.openai_wrapper import spy_openai

__all__ = ["spy_openai"]
