---
id: PT014
version: 1.0
name: Structured Output
description: "Specify the exact output schema (JSON, XML, markdown headers, function call) the agent must produce. USE FOR: Outputs consumed by other code/agents, repeatable workflows, anything that needs parsing. DO NOT USE FOR: Open-ended creative work, conversational responses, tasks where format is the user's choice."
category: output-format
tags: [structured-output, schema, integration, parsing, contract]
signals: [downstream-consumer, sequential-steps]
recommended-tier: all
prevents: "Downstream integration failures — free-form text output consumed by code or another agent requires fragile post-processing that breaks on minor format variations; a schema enforces a contract."
---

# Structured Output

## Reasoning

Free-form text is fine for humans but expensive to parse downstream. Specifying a schema turns the agent's output into a contract: the next step (code, agent, UI) knows exactly what to expect. This eliminates a category of integration bugs and reduces the need for fragile post-processing.

For agent orchestration, structured output is the bridge between sub-agents. A sub-agent returning `{"status": "complete", "result": "...", "confidence": 0.9}` is consumable; one returning a paragraph requires another LLM call to parse.

## Examples

- JSON schema: `{"findings": [...], "recommendations": [...], "confidence": 0..1}`
- Markdown sections: required H2 headers the next stage parses by name.
- Tool/function calling APIs: native structured output enforced by the runtime.
- XML tags for sections that need precise extraction (e.g. `<answer>`, `<reasoning>`).
