"""Plain loop: a baseline ReAct turn. The A-arm of the MVP comparison.

Tool use is provider-neutral: when the model asks for tools, their results go
back as text in a follow-up call (see core/adapters.py).
"""

MAX_TOOL_ROUNDS = 3


class PlainLoop:
    name = "plain"

    def run_turn(self, host, user_content: str) -> str:
        tools = [t.spec for t in host.tools]
        completion = host.client.complete(host.messages, host.system_prompt,
                                          tools, host.config.model.temperature,
                                          purpose_tag=host.purpose_tag)
        calls = 1
        while completion.tool_calls and calls <= MAX_TOOL_ROUNDS:
            results = _execute_tools(host, completion)
            host.messages.append({"role": "user", "content": results})
            completion = host.client.complete(
                host.messages, host.system_prompt, tools,
                host.config.model.temperature, purpose_tag=host.purpose_tag)
            calls += 1
        host.emit("draft_response", "agent",
                  {"text": completion.text, "model_calls": calls})
        return completion.text


def _execute_tools(host, completion) -> str:
    parts = ["Tool results:"]
    for call in completion.tool_calls:
        tool = next((t for t in host.tools if t.spec.name == call.name), None)
        host.emit("tool_call", "agent", {"tool": call.name, "args": call.arguments})
        result = tool.execute(call.arguments) if tool \
            else f"error: unknown tool '{call.name}'"
        host.emit("tool_result", "agent",
                  {"tool": call.name, "chars": len(result)})
        parts.append(f"{call.name}: {result}")
    return "\n".join(parts)
