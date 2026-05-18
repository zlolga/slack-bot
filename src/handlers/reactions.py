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
import os
import shutil

from slack_bolt.async_app import AsyncApp

from ..agent import run_revision, run_workspace_setup
from ..google.drive_helpers import (
    create_run_folder,
    doc_link,
    fetch_doc_text,
    folder_link,
    list_files_in_folder,
    resolve_comment,
    upload_local_folder,
)
from ..state import StateStore

log = logging.getLogger(__name__)


def register(app: AsyncApp, state: StateStore) -> None:
    @app.event("reaction_added")
    async def on_reaction(event, client):
        reaction = event.get("reaction", "")
        item = event.get("item", {})
        if item.get("type") != "message":
            return

        msg_ts = item.get("ts")
        channel_id = item.get("channel")

        # The reaction might be on:
        #   (a) the user's original mention message (msg_ts == run.thread_ts), or
        #   (b) a bot-posted gate message inside the thread (msg_ts in run.gate_message_ts).
        # Try both lookups.
        run = state.find_by_thread(msg_ts) or state.find_by_gate_message(msg_ts)
        if run is None:
            log.debug("Reaction %s on message %s — no matching run", reaction, msg_ts)
            return
        thread_ts = run.thread_ts

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

            # Create per-run Drive folder under the Lab parent folder.
            try:
                lab_parent = os.environ["DRIVE_LAB_FOLDER_ID"]
                drive_folder_id = create_run_folder(lab_parent, run.company)
                run.drive_folder_id = drive_folder_id
                state.update(run)
                await post(
                    f"📁 Drive folder created: {folder_link(drive_folder_id)}"
                )
            except Exception as e:
                log.exception("Failed to create Drive folder")
                await post(f"❌ Could not create Drive folder: `{e}`")
                run.mark("failed", note=f"drive folder creation failed: {e}")
                state.update(run)
                return

            try:
                await run_workspace_setup(
                    url=run.url,
                    linkedin=run.linkedin,
                    company=run.company,
                    drive_folder_id=drive_folder_id,
                    thread_callback=post,
                )
                run.mark("v1_done", note="agent finished successfully")
                state.update(run)
            except Exception as e:
                log.exception("run_workspace_setup raised")
                await post(
                    f"❌ Bot crashed during agent run: "
                    f"`{type(e).__name__}: {e}`\n"
                    "Check terminal logs for full traceback."
                )
                run.mark("failed", note=f"agent raised: {type(e).__name__}: {e}")
                state.update(run)
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

        # --- Revision approve gate ---
        if run.status == "revision_pending":
            if reaction == "white_check_mark":
                await _apply_revision(run, channel_id, thread_ts, client, state)
                return
            if reaction == "x":
                run.pending_revision = None
                run.mark(
                    "v1_done_revised" if run.version != "v1" else "v1_done",
                    note="revision cancelled by user",
                )
                state.update(run)
                await client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text="❌ Revision cancelled. Run state restored.",
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


async def _apply_revision(run, channel_id, thread_ts, client, state):
    """Pull current doc texts from Drive, invoke agent.run_revision,
    upload revised .md files as new Google Docs with version suffix,
    resolve comments on the originals."""
    pending = run.pending_revision
    if not pending:
        return

    run.mark("revising", note=f"applying {pending['version_new']}")
    state.update(run)

    async def post(msg: str) -> None:
        await client.chat_postMessage(
            channel=channel_id, thread_ts=thread_ts, text=msg
        )

    await post(f"🔧 Building *{pending['version_new']}* from comments…")

    # Fetch current text of every doc in the run folder.
    try:
        files = list_files_in_folder(run.drive_folder_id)
    except Exception as e:
        await post(f"❌ Drive listing failed: `{e}`")
        run.mark("failed", note="drive listing failed during revision")
        state.update(run)
        return

    current_docs = []
    for f in files:
        if f["name"].startswith("CHANGES"):
            continue
        try:
            text = fetch_doc_text(f["id"])
        except Exception as e:
            log.warning("Could not read %s: %s", f["name"], e)
            continue
        current_docs.append({"filename": f["name"], "text": text})

    work_dir = None
    try:
        work_dir = await run_revision(
            company=run.company,
            drive_folder_id=run.drive_folder_id,
            current_docs=current_docs,
            comments=pending["comments"],
            additional_sources=pending.get("additional_sources", []),
            version_prev=pending["version_prev"],
            version_new=pending["version_new"],
            thread_callback=post,
        )
    except Exception as e:
        log.exception("run_revision raised")
        await post(
            f"❌ Revision crashed: `{type(e).__name__}: {e}`\n"
            "Check terminal logs for full traceback."
        )
        run.mark("failed", note=f"revision raised: {type(e).__name__}: {e}")
        state.update(run)
        return

    # Upload revised docs with version suffix.
    await post("📤 Uploading revised artifacts to Drive…")
    suffix = f"_{pending['version_new']}"
    uploaded = upload_local_folder(work_dir, run.drive_folder_id, version_suffix=suffix)

    # Resolve the original comments now that the new version is up.
    resolved = 0
    failed = 0
    for c in pending["comments"]:
        try:
            resolve_comment(c["file_id"], c["comment_id"])
            resolved += 1
        except Exception as e:
            log.warning("Could not resolve comment %s on %s: %s",
                        c["comment_id"], c["filename"], e)
            failed += 1

    # Cleanup local work dir.
    if work_dir:
        shutil.rmtree(work_dir, ignore_errors=True)

    # Compose final summary.
    if uploaded:
        lines = [
            f"✅ *{pending['version_new']} ready* — {len(uploaded)} artifact(s):"
        ]
        for name, url in uploaded:
            lines.append(f"• <{url}|{name}>")
        lines.append(f"\nResolved *{resolved}* comment(s)"
                     + (f" (failed: {failed})" if failed else "")
                     + f". 📁 {folder_link(run.drive_folder_id)}")
        await post("\n".join(lines))
    else:
        await post(
            "⚠️ Revision agent finished but produced no files. "
            "Check logs. Comments left unresolved."
        )

    # Update run state.
    run.version = pending["version_new"]
    run.pending_revision = None
    run.mark("v1_done_revised", note=f"revised to {pending['version_new']}")
    state.update(run)
