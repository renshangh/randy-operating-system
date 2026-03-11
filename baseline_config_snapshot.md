# Baseline Config Capture Summary (#56)

This document records the operational configuration values for heartbeats and model routing as of March 11, 2026.

## 1. Heartbeat & Model Defaults
| Key | Value | Notes |
|-----|-------|-------|
| `primary_model` | `vllm/openai/gpt-oss-120b` | Global default for all agents |
| `fallbacks` | `google-gemini-cli/gemini-3-pro-preview`, `google-gemini-cli/gemini-3-flash-preview`, `openai-codex/gpt-5.1-codex-mini`, `openai-codex/gpt-5.2`, `openai-codex/gpt-5.1` | Order of failover |
| `compaction_mode`| `safeguard` | Preserves context before reset |

## 2. Agent Specific Routing (Model Overrides)
| Agent | Primary Model | Fallbacks |
|-------|---------------|-----------|
| **Sarah** | `vllm/openai/gpt-oss-120b` | Inherits defaults |
| **Ember** | `vllm/openai/gpt-oss-120b` | `google-gemini-cli/gemini-3-flash-preview`, `openai-codex/gpt-5.4`, `openai-codex/gpt-5.1-codex-mini` |

## 3. Channel & Messaging Config
- **Telegram (Default):** `dmPolicy: pairing`, `streaming: off`.
- **Telegram (Sarah-tg):** `groupPolicy: open`, `requireMention: false` (for group `-5052138612`).

## 4. Scheduling Baseline
- **Active Cron Jobs:** None (verified via `openclaw cron list`).
- **Heartbeat Interval:** Managed via `agent_poll.sh` (currently 180 seconds / 3 minutes).
