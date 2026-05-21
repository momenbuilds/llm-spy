# Comparison

llm-spy is simpler than Langfuse and LangSmith for local debugging because it does not require SDK instrumentation or a cloud account. It can coexist with those platforms.

| Tool | Setup time | Cloud needed | SDK instrumentation | Local-first | Terminal UI | Target user |
| --- | --- | --- | --- | --- | --- | --- |
| llm-spy | Minutes | No | No | Yes | Yes | Local AI developers |
| Langfuse | Moderate | Usually | Usually | Self-host possible | No | Teams needing observability |
| LangSmith | Moderate | Yes | Yes | No | No | LangChain teams |
| Helicone | Low | Usually | Proxy/SDK | No | No | Hosted gateway users |
| Custom logging | Variable | No | Yes | Depends | No | App-specific debugging |
