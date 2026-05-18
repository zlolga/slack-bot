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

from ..google.drive_helpers import (
    list_files_in_folder,
    list_unresolved_comments,
)
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

    resp = await say(
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
    # Capture the bot message ts so the reaction handler can map reactions
    # on the handshake back to this run.
    if resp and "ts" in resp:
        run.gate_message_ts["handshake"] = resp["ts"]
        state.update(run)


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
    # Revise targets the most recent run for this channel.
    run = state.active_run() or _last_terminal(state)
    if run is None:
        await say(text="No run to revise.", thread_ts=message_ts)
        return
    if run.drive_folder_id is None:
        await say(
            text=f"Run for {run.company} has no Drive folder — nothing to revise.",
            thread_ts=message_ts,
        )
        return

    await say(
        text=f"📬 Fetching comments from `{run.company}/` …",
        thread_ts=message_ts,
    )

    try:
        files = list_files_in_folder(run.drive_folder_id)
    except Exception as e:
        log.exception("Failed to list files in folder")
        await say(text=f"❌ Drive listing failed: `{e}`", thread_ts=message_ts)
        return

    # Skip prior CHANGES files when collecting comments — we revise the
    # workspace artifacts themselves, not the changelog.
    files = [f for f in files if not f["name"].startswith("CHANGES")]

    per_doc_comments: list[dict] = []
    total = 0
    for f in files:
        try:
            comments = list_unresolved_comments(f["id"])
        except Exception as e:
            log.warning("Could not fetch comments for %s: %s", f["name"], e)
            comments = []
        if comments:
            per_doc_comments.append({"file": f, "comments": comments})
            total += len(comments)

    if total == 0:
        await say(
            text=(
                f"📭 No unresolved comments in `{run.company}/`. "
                "Add Google Docs comments on the artifacts you want changed, "
                "then `@outrizz-bot revise` again."
            ),
            thread_ts=message_ts,
        )
        return

    # Build summary
    lines = [
        f"📬 Found *{total}* unresolved comment(s) across *{len(per_doc_comments)}* doc(s):\n"
    ]
    n = 1
    for entry in per_doc_comments:
        lines.append(f"\n*{entry['file']['name']}*")
        for c in entry["comments"]:
            quote = c["content"].replace("\n", " ").strip()
            if len(quote) > 140:
                quote = quote[:135] + "…"
            anchor = f" `({c['anchor']})`" if c.get("anchor") else ""
            lines.append(f"  {n}. _{c['author_name']}_{anchor}: \"{quote}\"")
            n += 1

    next_version = run.next_version()
    lines.append(
        f"\nApply all and produce *{next_version}*? "
        "React ✅ to proceed / ❌ to cancel."
    )

    # Store the pending revision payload — used by the reaction handler.
    run.pending_revision = {
        "trigger": "comments",
        "comments": [
            {
                "filename": entry["file"]["name"],
                "file_id": entry["file"]["id"],
                "comment_id": c["id"],
                "author": c["author_name"],
                "anchor": c.get("anchor", ""),
                "text": c["content"],
            }
            for entry in per_doc_comments
            for c in entry["comments"]
        ],
        "additional_sources": [],
        "version_prev": run.version,
        "version_new": next_version,
    }
    run.mark("revision_pending", note=f"awaiting approval for {next_version}")
    state.update(run)

    resp = await say(text="\n".join(lines), thread_ts=message_ts)
    if resp and "ts" in resp:
        run.gate_message_ts["revision_summary"] = resp["ts"]
        state.update(run)


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
