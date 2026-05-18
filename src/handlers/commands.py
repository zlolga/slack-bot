"""
Slash commands for the lab bot.

| Command         | Effect                                |
|-----------------|---------------------------------------|
| /lab runs       | List all runs in this channel        |
| /lab status <ts> | Summary for one run (thread_ts as id) |
"""

from __future__ import annotations

import logging

from slack_bolt.async_app import AsyncApp

from ..state import StateStore

log = logging.getLogger(__name__)


def register(app: AsyncApp, state: StateStore) -> None:
    @app.command("/lab")
    async def on_lab(ack, command, say):
        await ack()
        text = (command.get("text") or "").strip()
        sub, *rest = text.split() or [""]

        if sub == "runs" or sub == "":
            await say(text=_format_runs(state))
        elif sub == "status" and rest:
            await say(text=_format_status(state, rest[0]))
        else:
            await say(
                text=(
                    "Usage:\n"
                    "  `/lab runs` — list all runs\n"
                    "  `/lab status <thread_ts>` — show one run"
                )
            )


def _format_runs(state: StateStore) -> str:
    runs = state.all_runs()
    if not runs:
        return "No runs yet. Start one with `@outrizz-bot setup <url>`."
    lines = ["*Lab runs:*"]
    for r in runs:
        marker = "▶️" if r.is_active() else "✅" if r.status == "v1_done" else "⏹"
        lines.append(
            f"{marker} *{r.company}* — {r.version} — `{r.status}` "
            f"(started {r.started_at[:16]})"
        )
    return "\n".join(lines)


def _format_status(state: StateStore, thread_ts: str) -> str:
    run = state.find_by_thread(thread_ts)
    if run is None:
        return f"No run with thread_ts `{thread_ts}`."
    lines = [
        f"*Run for {run.company}* — `{run.status}`",
        f"URL: {run.url}",
        f"Version: {run.version} ({run.tier_scope})",
        f"Started: {run.started_at}",
    ]
    if run.completed_at:
        lines.append(f"Completed: {run.completed_at}")
    if run.drive_folder_id:
        lines.append(f"Drive folder: {run.drive_folder_id}")
    if run.stage_history:
        lines.append("Stage history:")
        for h in run.stage_history[-5:]:
            lines.append(f"  • {h['ts'][:19]}  {h['from']} → {h['to']}  {h['note']}")
    return "\n".join(lines)
