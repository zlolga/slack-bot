"""
Reaction handlers — lightweight gates between stages.

| Reaction      | Context              | Effect                              |
|---------------|----------------------|-------------------------------------|
| white_check_mark (✅) | awaiting_confirm | Start Stage 1                       |
| x (❌)        | awaiting_confirm    | Cancel before any work              |
| +1 (👍)        | smell_test          | Proceed to Stage 2                  |
| speech_balloon (💬) | smell_test     | Wait for textual correction         |
| +1 (👍)        | open_question        | Accept best guess                   |
| speech_balloon (💬) | open_question  | Wait for textual answer             |
| track_next (⏭) | open_question        | Defer                               |
"""

from __future__ import annotations

import logging

from slack_bolt.async_app import AsyncApp

from ..agent import run_workspace_setup
from ..state import StateStore

log = logging.getLogger(__name__)


def register(app: AsyncApp, state: StateStore) -> None:
    @app.event("reaction_added")
    async def on_reaction(event, client):
        reaction = event.get("reaction", "")
        item = event.get("item", {})
        if item.get("type") != "message":
            return

        thread_ts = item.get("ts")
        channel_id = item.get("channel")
        run = state.find_by_thread(thread_ts)
        if run is None:
            # Reaction on a non-run message — ignore.
            return

        log.info(
            "Reaction %s on run %s (status=%s)", reaction, run.company, run.status
        )

        # --- Approve gate: start Stage 1 ---
        if run.status == "awaiting_confirm" and reaction == "white_check_mark":
            run.mark("running", note="user-confirmed via reaction")
            state.update(run)

            async def post(msg: str) -> None:
                await client.chat_postMessage(
                    channel=channel_id, thread_ts=thread_ts, text=msg
                )

            await post("🚀 Starting Stage 1 (Collect, Tier 0)...")
            await run_workspace_setup(
                url=run.url,
                linkedin=run.linkedin,
                drive_folder_id=run.drive_folder_id or "TBD",
                thread_callback=post,
            )
            return

        if run.status == "awaiting_confirm" and reaction == "x":
            run.mark("cancelled", note="user-rejected at handshake")
            state.update(run)
            await client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"❌ Cancelled before start: *{run.company}*.",
            )
            return

        # --- Smell test ---
        if run.status == "smell_test":
            if reaction == "+1":
                run.mark("extracting", note="smell test passed")
                state.update(run)
                # TODO: trigger Stage 2 in the agent
                await client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text="👍 Proceeding to Stage 2 (Extract)...",
                )
            elif reaction == "speech_balloon":
                # Wait for user text — handled by mention/message handler
                await client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text="✍️ Waiting for your correction. Reply in this thread.",
                )

        # TODO: open-question reactions (+1 / speech_balloon / track_next)
        # require agent-side context about which OQ a given message belongs to.
