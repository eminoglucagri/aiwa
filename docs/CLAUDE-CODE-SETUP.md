# Claude Code Setup

## Overview

Claude Code is configured to use the Minimax M2.7 API proxy at `https://api.minimax.io/anthropic`.

## Configuration

Claude Code settings are stored in `/home/paperclip/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "sk-cp-...",
    "ANTHROPIC_MODEL": "MiniMax-M2.7",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "MiniMax-M2.7",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "MiniMax-M2.7",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "MiniMax-M2.7",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

## Verification

API connectivity verified 2026-04-28:
- API endpoint: `https://api.minimax.io/anthropic/v1/messages`
- Model: `MiniMax-M2.7`
- Status: **operational** (HTTP 200, response time OK)

## Claude Code Binary

- Path: `/usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`
- Entrypoint env: `CLAUDE_CODE_ENTRYPOINT=sdk-cli`