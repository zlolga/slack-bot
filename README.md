# outrizz-lab-bot

Slack bot that wraps the `workspace-context-and-icp-spec` skill for Outrizz Phase 0 lab mode.

Design and spec docs live in the sibling repo at `../Outrizz Agents in Slack/`:
- Project overview: `../Outrizz Agents in Slack/CLAUDE.md`
- Phase 0 (lab mode) spec: `../Outrizz Agents in Slack/agents/00_workspace_lab.md`
- Runtime setup runbook: `../Outrizz Agents in Slack/setup/phase_0_runtime.md`

This repo is the **executable code**. The docs repo is the **design**.

---

## Quick start (local dev on Mac)

Prerequisites: Python 3.12+, `uv`, Node.js 20+ (for MCP servers), a Slack app, a Google Cloud OAuth client.

```bash
# 1. Install dependencies
uv sync

# 2. Copy .env template and fill in secrets
cp .env.example .env
# edit .env with your tokens

# 3. Run the OAuth bootstrap once (opens browser for Google consent)
uv run python scripts/first_run_oauth.py

# 4. Start the bot
uv run python -m src.app
```

The bot will connect to Slack via Socket Mode. Mention it in `#workspace-lab`:

```
@outrizz-bot setup https://stripe.com
```

---

## Repo layout

```
outrizz-lab-bot/
├── pyproject.toml          # dependencies and build config
├── .env.example            # template for secrets
├── .gitignore
├── mcp_config.json         # MCP servers (Slack, Google Drive) config
├── README.md               # this file
├── src/
│   ├── app.py              # Slack Bolt entrypoint
│   ├── agent.py            # Claude Agent SDK wrapper
│   ├── state.py            # state.json read/write
│   ├── handlers/
│   │   ├── mentions.py     # @bot setup, add, revise, cancel
│   │   ├── reactions.py    # ✅, ❌, 👍, 💬, ⏭ gates
│   │   └── commands.py     # /lab runs, /lab status
│   └── google/
│       ├── oauth.py        # OAuth bootstrap helpers
│       └── drive_helpers.py # Drive workarounds (write/update gap)
├── scripts/
│   └── first_run_oauth.py  # run once on a machine with a browser
├── deploy/
│   ├── outrizz-lab-bot.service  # systemd unit for Hetzner
│   ├── deploy.sh                # rsync + restart script
│   └── README.md                # Hetzner deployment guide
└── skills/
    └── workspace-context-and-icp-spec/  # unpacked Outrizz skill
        ├── SKILL.md
        ├── INT_*.md (5 files)
        ├── OUT_*.md (4 files)
        └── QA_Checklist.md
```

---

## Deployment

For local dev: see Quick start above.
For Hetzner production: see `deploy/README.md`.

---

## Status

Phase 0 — lab mode. One channel (`#workspace-lab`), runs against example companies, outputs into `Outrizz / Lab / <Example>/` on Google Drive.

---

*Outrizz Delivery | v0.1 — 2026-05-18*
