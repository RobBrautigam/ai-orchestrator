# Providers: Grok, GLM, DeepSeek and other models, reached through the tools

*Checked against each tool's own provider documentation on 2026-09-23. Grok, GLM and DeepSeek are models, not agentic coding tools: none of them ships its own background-session supervisor, worktree flag or helper-agent system in the shape the adapters describe. They are reached THROUGH a tool that has an adapter, and the method is the same: the launch names the model and its effort explicitly, and the chair's chat line says which. Where the documentation did not say, the cell reads "not verified".*

---

## The table

| Model family | OpenCode | Hermes | OpenClaw | Codex | Cursor | Ollama (local weights) | Claude Code |
|---|---|---|---|---|---|---|---|
| **Grok** (xAI) | the xAI provider is on OpenCode's providers page: `opencode run --model <provider>/<model>` (the id string: not verified) | the xAI provider, `XAI_API_KEY`, or the xAI OAuth login: `--provider xai --model <model>` | the xAI provider is on OpenClaw's providers page: `--model <provider>/<model>` (the id string: not verified) | a custom entry under `model_providers.<id>` in `config.toml` (`base_url`, `env_key`), then `--model <model>`; xAI's own endpoint shape: not verified | Grok models are in Cursor's own model list: `agent -p --model <model>` | not verified | not the path (below) |
| **GLM** (Z.ai) | the Z.AI provider: `--model <provider>/<model>` (the id string: not verified) | `z.ai / GLM` with `GLM_API_KEY`: `--provider <id> --model <model>` (the exact provider id: not verified) | the Z.AI (GLM) provider: `--model <provider>/<model>` (the id string: not verified) | a `model_providers.<id>` entry, as above | not verified | GLM models are in Ollama's library (`ollama pull <model>`), then any tool pointed at the local endpoint | not the path |
| **DeepSeek** | the DeepSeek provider: `--model <provider>/<model>` (the id string: not verified) | the DeepSeek provider, `DEEPSEEK_API_KEY`: `--provider deepseek --model <model>` | the DeepSeek provider, and a local DeepSeek entry: `--model <provider>/<model>` (the id string: not verified) | a `model_providers.<id>` entry, as above | not verified | DeepSeek models are in Ollama's library, as above | not the path |
| **Many at once** (OpenRouter) | the OpenRouter provider | the OpenRouter provider, `OPENROUTER_API_KEY` or an OAuth login | the OpenRouter provider | a `model_providers.<id>` entry | not verified | n/a | not the path |

Model names change monthly; each tool lists its current ones (for instance `agent --list-models` on Cursor, `hermes model` on Hermes, `ollama list` for local weights). The table names the ROUTE, never a model version, so it stays true longer than any model does.

## Four rules that do not change per provider

1. **Explicit model and effort on every launch** (chapter 9, rule 1). A provider's effort setting has its own name: OpenCode's `--variant`, OpenClaw's `--thinking`, Codex's `model_reasoning_effort`. An effort flag the documentation does not name is written "not verified", never guessed.
2. **A router is never the mechanism** (chapter 9, rule 8). Claude Code's gateway documentation (read 2026-09-19) says it does not route to non-Claude models through any gateway, and a gateway in front of a caching-dependent tool loses the prompt cache. When a Grok, GLM or DeepSeek model is wanted, it is driven by a tool that supports it natively, from the table above.
3. **Measure completion, not tokens** (chapter 9, rule 9). A trial of a cheaper provider is the same task, reviewed, with the same defect count, beside a session on the current default; "fewer tokens" alone proves nothing.
4. **Keys by name, never by value.** A provider key lives in the tool's own credential store or an environment variable the launch names; it never appears in a prompt, a briefing, a queue row or a commit.
