"""
@-mention handlers for the lab bot.

Commands the bot understands when mentioned (e.g. `@outrizz-bot setup ...`):
    setup <url> [linkedin]   start a new workspace-setup run
    add <url>                attach a public link (YouTube, podcast, news) — reflows Stage 2
    add (with attachment)    attach a file (pdf, pptx) — reflows Stage 2
    revise [N,M]             apply accumulated feedback
    qa                       re-run the QA checklist
    cancel                   stop the active run

Per Phase 0 decisions: only one active run at a time. Second `setup` while
another is running is rejected.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from slack_bolt.async_app import AsyncApp

from ..state import StateStore

log = logging.getLogger(__name__)

URL_RE = re.compile(r"https?://[^\s<>|]+")


def register(app: AsyncApp, state: StateStore) -> None:
    """Wire @mention handlers into the Bolt app."""

    @app.event("app_mention")
    async def on_mention(event, say, client):
        text = _strip_mentions(event.get("text", ""))
        channel_id = event["channel"]
        message_ts = event["ts"]

        log.info("Mention received: %r in %s", text, channel_id)

        cmd, *rest = text.split(maxsplit=1)
        rest_text = rest[0] if rest else ""

        if cmd == "setup":
            await _handle_setup(rest_text, channel_id, message_ts, state, say)
        elif cmd == "add":
            await _handle_add(rest_text, channel_id, message_ts, state, say)
        elif cmd == "revise":
            await _handle_revise(rest_text, channel_id, message_ts, state, say)
        elif cmd == "qa":
            await _handle_qa(channel_id, message_ts, state, say)
        elif cmd == "cancel":
            await _handle_cancel(channel_id, message_ts, state, say)
        else:
            await say(
                text=(
                    f"Unknown command `{cmd}`. Available: "
                    "`setup <url>`, `add <url>`, `revise`, `qa`, `cancel`."
                ),
                thread_ts=message_ts,
            )


# --- Commands ---------------------------------------------------------------


async def _handle_setup(
    text: str,
    channel_id: str,
    message_ts: str,
    state: StateStore,
    say,
) -> None:
    urls = URL_RE.findall(text)
    if not urls:
        await say(
            text="Need a URL. Usage: `@outrizz-bot setup https://stripe.com [linkedin.com/company/stripe]`",
            thread_ts=message_ts,
        )
        return

    if state.has_active_run():
        active = state.active_run()
        await say(
            text=(
                f"⏸️ Run for *{active.company}* is currently active "
                f"(status: `{active.status}`). Wait until it reaches v1 or "
                f"`cancel` it before starting a new one."
            ),
            thread_ts=message_ts,
        )
        return

    url = urls[0]
    linkedin = urls[1] if len(urls) > 1 else None
    run = state.create_run(
        thread_ts=message_ts, channel_id=channel_id, url=url, linkedin=linkedin
    )

    await say(
        text=(
            f"🆕 *New workspace-setup run requested*\n"
            f"*Company:* {run.company} (parsed from URL)\n"
            f"*URL:* {url}\n"
            + (f"*LinkedIn:* {linkedin}\n" if linkedin else "")
            + "*Tier scope:* T0 (public sources only, baseline)\n\n"
            "Confirm to start Stage 1? React ✅ to proceed, ❌ to cancel."
        ),
        thread_ts=message_ts,
    )


async def _handle_add(
    text: str, channel_id: str, message_ts: str, state: StateStore, say
) -> None:
    run = state.active_run()
    if run is None:
        await say(
            text="No active run. Start with `@outrizz-bot setup <url>` first.",
            thread_ts=message_ts,
        )
        return

    urls = URL_RE.findall(text)
    if not urls:
        await say(
            text=(
                "📎 Stub: file attachment handling for `add` will land in "
                "the next iteration. For now, supply a URL: `add <url>`."
            ),
            thread_ts=message_ts,
        )
        return

    # TODO: wire to agent reflow
    await say(
        text=f"📎 Stub: would reflow Stage 2 for {run.company} with new material: {urls[0]}",
        thread_ts=message_ts,
    )


async def _handle_revise(
    text: str, channel_id: str, message_ts: str, state: StateStore, say
) -> None:
    run = state.active_run() or _last_terminal(state)
    if run is None:
        await say(text="No run to revise.", thread_ts=message_ts)
        return
    # TODO: wire to agent revise
    await say(
        text=f"✍️ Stub: would apply feedback to {run.company} ({run.version}).",
        thread_ts=message_ts,
    )


async def _handle_qa(channel_id: str, message_ts: str, state: StateStore, say) -> None:
    run = state.active_run() or _last_terminal(state)
    if run is None:
        await say(text="No run to QA.", thread_ts=message_ts)
        return
    await say(
        text=f"✅ Stub: would re-run QA for {run.company}.", thread_ts=message_ts
    )


async def _handle_cancel(
    channel_id: str, message_ts: str, state: StateStore, say
) -> None:
    run = state.active_run()
    if run is None:
        await say(text="No active run to cancel.", thread_ts=message_ts)
        return
    run.mark("cancelled", note="user-cancelled via @mention")
    state.update(run)
    await say(
        text=f"❌ Cancelled run for *{run.company}*. Artifacts (if any) remain in Drive.",
        thread_ts=run.thread_ts,
    )


# --- Helpers ----------------------------------------------------------------


def _strip_mentions(text: str) -> str:
    """Remove leading <@U...> mentions and trim."""
    return re.sub(r"<@[UW][A-Z0-9]+>", "", text).strip()


def _last_terminal(state: StateStore):
    runs = state.all_runs()
    return runs[-1] if runs else None
