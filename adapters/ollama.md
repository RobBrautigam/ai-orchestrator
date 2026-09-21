# Adapter: a local model through Ollama

*Checked against Ollama's documentation (CLI reference, OpenAI compatibility) on 2026-09-20. Ollama is not a coding agent; it serves a model that one of the other tools drives. This adapter says how to point each of them at it, and what a local model is for in this method. Where the documentation did not say, the line reads "not verified".*

---

## Serve the model

```
ollama pull <model>          # once; ask the operator first about anything large, and put the models on the drive they named
ollama serve                 # the server on http://localhost:11434 (the desktop app runs it for you)
ollama ps                    # what is loaded
ollama stop <model>          # unload
```

Ollama exposes an OpenAI-compatible API at `http://localhost:11434/v1/` (`/v1/chat/completions`, `/v1/responses`); the API key is required by clients and ignored (`ollama`). A hosted tier at `https://ollama.com/v1` takes a real key in `OLLAMA_API_KEY`.

## Point a coding tool at it

`ollama launch <tool>` configures and starts a supported integration against a local model: the documentation lists OpenCode, Claude Code, Codex, VS Code and Droid (`ollama launch claude --model <model>`; `--config` to configure without launching). Per tool:

| Tool | How |
|---|---|
| Claude Code | `ollama launch claude --model <model>`; the documentation's supported integration. Whether every Claude Code feature works against a non-Claude upstream: not verified, and the tool's own documentation says its prompt caching markers are ignored by other upstreams (see chapter 9, rule 8). |
| Codex | `codex exec --oss --local-provider ollama -m <model> "<prompt>"` (the flags are on the Codex CLI reference). |
| OpenCode | `ollama launch opencode`, or configure the `ollama` provider and run `opencode run --model ollama/<model>`. |
| Gemini CLI | not verified. |
| Cursor | not verified. |
| Hermes | `hermes model` lists providers; a custom OpenAI-compatible endpoint at `http://localhost:11434/v1` is the documented route for "your own endpoint". |
| OpenClaw | `openclaw agent exec --model ollama/<model> --local-model-lean` is on the `agent exec` page. |

## What a local model is for in this method

Chapter 9, rule 7: the local tier takes classification, extraction, summarizing, triage and batch passes over the operator's own data, at $0.00 and with a verification pass (quotes checked against the source) that is the same code path a paid model would get. It does not drive sessions. Measured on the workstation that wrote this: the graphics card had about 9.7 GiB free after the operator's browsers and editor took their share, which fits one agentic-class model of about 9 billion parameters; a 27-billion-parameter model at four-bit quantization ran at about 13 tokens a second at 50 to 60 thousand tokens of context on the same card. Those numbers decide what "local" can mean on a given machine, and the honest way to find yours is to measure, not to assume.

## A router is never the mechanism

Pointing a session's tool at a local model through a generic gateway loses the tool's prompt caching and its provider-specific features. When a local model is wanted inside a session, it is called as a tool (a small script that posts to `http://localhost:11434/v1/chat/completions` and returns the answer) from a session that stays on its own model. When a local model is wanted as the driver, it is driven by a CLI that supports it natively (`codex exec --oss`, `ollama launch <tool>`).

## Process hygiene

`ollama serve` started by a session is a process the session started; stop it by id at the close unless the operator runs it as their own service, in which case it is on the never-stopped list. A model kept loaded holds video memory the operator's other programs want; `ollama stop <model>` at the close.
