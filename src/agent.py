"""
Claude Agent SDK wrapper — v1 sync end-to-end run.

Flow:
    1. Caller creates a Drive folder for the run (via drive_helpers).
    2. We create a /tmp work directory for agent output.
    3. We build a prompt that inlines the SKILL.md content and tells the
       agent to write artifacts as .md files into the work dir.
    4. The Agent SDK is invoked; we stream its text output to Slack via
       the callback.
    5. After the agent finishes, we upload the .md files from the work
       dir into the Drive folder as Google Docs.
    6. We post a final summary with Drive links.

Notes:
    - No intermediate gates in v1 (smell test, OQs) — comes in v2.
    - Drive write via google-api-python-client (not Drive MCP) — the MCP
      doesn't support update operations cleanly.
    - Agent's web access via built-in WebSearch / WebFetch tools.
"""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Awaitable, Callable

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)

from .google.drive_helpers import folder_link, upload_local_folder

log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / "skills" / "workspace-context-and-icp-spec"
SKILL_MAIN = SKILL_DIR / "SKILL.md"

ThreadCallback = Callable[[str], Awaitable[None]]


def _build_system_prompt() -> str:
    """Compose the system prompt: skill content + supporting templates inline."""
    skill_text = SKILL_MAIN.read_text()
    template_blocks = []
    for tmpl_path in sorted(SKILL_DIR.glob("*.md")):
        if tmpl_path.name == "SKILL.md":
            continue
        template_blocks.append(
            f"\n\n--- TEMPLATE: {tmpl_path.name} ---\n\n{tmpl_path.read_text()}"
        )

    return f"""You are the Outrizz workspace-setup agent.

Your job is to execute the workspace-context-and-icp-spec skill end-to-end
(Stages 1 through 4) for a single company.

# Output rules

You will be given a local working directory path. Write ALL artifacts
there as .md files using the EXACT filenames from the skill:

- INT_Voice_Quotes.md
- INT_Product_Facts.md
- INT_Anti_Claims.md
- INT_Segment_Hypotheses.md
- INT_Role_Observations.md
- {{Company}}_Workspace_Context.md
- {{Company}}_Segment_{{Name}}_VPC.md  (one per segment)
- {{Company}}_Role_{{Name}}_VPC.md     (one per role)
- {{Company}}_Value_Artifacts.md
- QA_Results.md

Use the Write tool with the absolute path inside the working directory.

# Progress reporting

Post short status updates (each ≤200 characters) as you work. Aim for
one message at the START of each stage and one at the END. You may
optionally post 1-2 mid-stage progress notes if a stage is taking long
(e.g. "still pulling LinkedIn — slow site").

Examples (use this style):

    [Stage 1/4] Collecting Tier 0 sources for {{Company}}…
    [Stage 1/4] ✅ done — site, LinkedIn, G2, Crunchbase, press, hiring.
    [Stage 2/4] Extracting INT_* files…
    [Stage 2/4] ✅ done — 5 INT files written.
    [Stage 3/4] Drafting OUT artifacts (Workspace Context + N Segments + M Roles)…
    [Stage 3/4] ✅ done.
    [Stage 4/4] QA…
    [Stage 4/4] ✅ done — N warnings, see Workspace_Context §6.

Do NOT dump file contents, full quotes, or long lists into chat. Keep
text terse — these are status pings, not summaries.

Do not ask the user any questions during the run — log uncertainties as
described in the next section.

# Open Questions discipline

Open Questions in `{{Company}}_Workspace_Context.md` §6 are capped at **10
items maximum**. Only include uncertainties that materially block
downstream listbuilding, sequence-writing, or qualification. Curate
ruthlessly. Lower-priority uncertainties go inline as `[?]` notes in the
relevant section (not in §6).

# Web research

Use WebSearch and WebFetch tools liberally — that's the source of truth
for Tier 0 (public sources).

# Skill instructions and templates follow

{skill_text}

{''.join(template_blocks)}
"""


def _extract_text(message) -> str:
    """Pull plain text out of an Agent SDK message, if it's text content."""
    if isinstance(message, AssistantMessage):
        chunks = []
        for block in getattr(message, "content", []):
            if isinstance(block, TextBlock):
                chunks.append(block.text)
        return "\n".join(chunks).strip()
    return ""


async def run_workspace_setup(
    url: str,
    linkedin: str | None,
    company: str,
    drive_folder_id: str,
    thread_callback: ThreadCallback,
) -> None:
    """
    Run the full workspace-setup skill against `url`.

    Pre-conditions:
        - drive_folder_id points to a Drive folder owned by outrizz.bot
          (created by the caller before invoking the agent).

    On success: artifacts are uploaded to that Drive folder as Google Docs.
    On failure: callback receives an error message; raises.
    """
    work_dir = Path(tempfile.mkdtemp(prefix=f"outrizz_{company}_"))
    log.info("Agent work dir: %s", work_dir)
    await thread_callback(
        f"🚀 *Agent started.* Working on *{company}*.\n"
        f"Drive folder: {folder_link(drive_folder_id)}"
    )

    system_prompt = _build_system_prompt()

    user_prompt = f"""\
Company: {company}
Website: {url}
LinkedIn: {linkedin or '(not provided — find it via web search)'}

Working directory (write all .md outputs here):
{work_dir}

Begin Stage 1 (Collect, Tier 0) now. Work through all 4 stages.
Post brief status updates as text between tool calls.
"""

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        system_prompt=system_prompt,
        allowed_tools=["WebSearch", "WebFetch", "Read", "Write", "Bash"],
        permission_mode="bypassPermissions",
    )

    try:
        msg_count = 0
        async for message in query(prompt=user_prompt, options=options):
            msg_count += 1
            log.info("agent msg #%d: type=%s", msg_count, type(message).__name__)
            text = _extract_text(message)
            if text:
                if len(text) > 2000:
                    text = text[:1900] + "\n…(truncated)"
                await thread_callback(text)
        log.info("Agent finished after %d messages", msg_count)
    except Exception as e:
        log.exception("Agent run failed for %s", company)
        await thread_callback(f"❌ Agent failed: `{type(e).__name__}: {e}`")
        # cleanup, then re-raise so the reaction handler can update status
        shutil.rmtree(work_dir, ignore_errors=True)
        raise

    # Upload artifacts to Drive
    await thread_callback("📤 Uploading artifacts to Drive...")
    uploaded = upload_local_folder(work_dir, drive_folder_id)

    if uploaded:
        lines = [f"✅ *v1 ready* — {len(uploaded)} artifacts in Drive:"]
        for name, url in uploaded:
            lines.append(f"• <{url}|{name}>")
        lines.append(f"\n📁 {folder_link(drive_folder_id)}")
        await thread_callback("\n".join(lines))
    else:
        await thread_callback(
            "⚠️ Agent finished but no .md files were created in the work dir. "
            "Check logs."
        )

    # Cleanup local work dir
    shutil.rmtree(work_dir, ignore_errors=True)


def _build_revision_system_prompt() -> str:
    """System prompt for revision runs.

    Reuses the skill content (for context) but the *task* is different:
    incorporate user feedback into existing artifacts and produce a new
    version + an explicit changelog.
    """
    skill_text = SKILL_MAIN.read_text()
    return f"""You are the Outrizz workspace-setup agent, executing a REVISION
pass on existing artifacts.

# Task

You will receive:
  - the current text of each Workspace artifact (Workspace Context,
    Segment VPCs, Role VPCs, Value Artifacts)
  - a list of user comments on those artifacts, grouped per file
  - optionally additional source material (extracted text from pptx,
    pdf, youtube transcripts) — treat this as Tier 1/Tier 2 input

Produce:
  - A revised version of EVERY changed artifact, saved as .md to the
    provided working directory. Use the same filename (without version
    suffix) — the wrapper appends the version when uploading.
  - A `CHANGES.md` file in the same working directory that summarizes
    what changed and why, with explicit reference to which comment/source
    drove each change.

# Output rules

- Only re-emit files that actually changed. If a Role VPC has no
  comments and no new material affecting it, skip it.
- For each revised file: prepend a `## Changelog` section at the very
  top listing the bullet-point changes in this version.
- `CHANGES.md` format:

    # Changes — {{version_prev}} → {{version_new}}
    Generated: {{ISO timestamp}}

    ## <Filename>
    - <one-line change>
      → addresses comment from <author> at <anchor>: "<quote>"
    - <one-line change>
      → reflects new source material: <brief>

    ## <Filename>
    - (no changes — comments did not require revision)

  Include every file you considered (changed or unchanged) so the user
  can see what you reviewed.

- If a comment is ambiguous, interpret it as best you can and note your
  interpretation in CHANGES.md with `→ interpreted as: ...`. Do NOT ask
  the user — clarifications come in v2.1.

# Progress reporting

Post AT MOST 3 short messages (≤120 chars) during the run:
  1. "[revise] reading current docs and comments…"
  2. "[revise] generating v_new…"
  3. "[revise] ✅ done."

No other chat output.

# Skill reference (for context — DO NOT re-execute Stage 1–4)

{skill_text}
"""


async def run_revision(
    company: str,
    drive_folder_id: str,
    current_docs: list[dict],
    comments: list[dict],
    additional_sources: list[dict],
    version_prev: str,
    version_new: str,
    thread_callback: ThreadCallback,
) -> Path:
    """
    Run a revision pass against current_docs + comments + additional_sources.

    Args:
        company:             Stripe / Linear / ...
        drive_folder_id:     Drive folder for upload (caller uploads)
        current_docs:        [{filename, text}, ...] — what's in Drive now
        comments:            [{filename, comment_id, author, anchor, text}, ...]
        additional_sources:  [{source: "pptx"|"pdf"|"youtube", title, text}, ...]
        version_prev:        e.g. "v1.0"
        version_new:         e.g. "v1.1"
        thread_callback:     async fn(str) — posts to Slack

    Returns:
        Path to the work_dir containing revised .md files (caller uploads).
    """
    work_dir = Path(tempfile.mkdtemp(prefix=f"outrizz_revise_{company}_"))
    log.info("Revision work dir: %s", work_dir)

    system_prompt = _build_revision_system_prompt().replace(
        "{version_prev}", version_prev
    ).replace("{version_new}", version_new)

    # Build the user prompt with all materials inlined.
    docs_block = "\n\n".join(
        f"### {d['filename']}\n```\n{d['text']}\n```" for d in current_docs
    )
    comments_block = (
        "\n".join(
            f"- [{c['filename']}] {c['author']}: \"{c['text']}\""
            + (f" (anchor: {c['anchor']})" if c.get("anchor") else "")
            for c in comments
        )
        if comments
        else "(none)"
    )
    sources_block = (
        "\n\n".join(
            f"### Source: {s['source']} — {s.get('title', '(untitled)')}\n```\n{s['text']}\n```"
            for s in additional_sources
        )
        if additional_sources
        else "(none)"
    )

    user_prompt = f"""\
Company: {company}
Previous version: {version_prev}
New version: {version_new}

Working directory (write revised .md files here, plus CHANGES.md):
{work_dir}

# Current artifacts

{docs_block}

# Unresolved comments

{comments_block}

# Additional source material (Tier 1/Tier 2)

{sources_block}

Begin revision now.
"""

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        system_prompt=system_prompt,
        allowed_tools=["Read", "Write", "Bash"],
    )

    await thread_callback(f"🔧 Generating {version_new}...")

    try:
        msg_count = 0
        async for message in query(prompt=user_prompt, options=options):
            msg_count += 1
            log.info("revision msg #%d: type=%s", msg_count, type(message).__name__)
            text = _extract_text(message)
            if text:
                if len(text) > 2000:
                    text = text[:1900] + "\n…(truncated)"
                await thread_callback(text)
        log.info("Revision finished after %d messages", msg_count)
    except Exception as e:
        log.exception("Revision failed for %s", company)
        await thread_callback(f"❌ Revision failed: `{type(e).__name__}: {e}`")
        shutil.rmtree(work_dir, ignore_errors=True)
        raise

    return work_dir
