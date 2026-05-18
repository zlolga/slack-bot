"""
Claude Agent SDK wrapper for the workspace-setup skill.

This is a STUB for the first scaffolding pass. The real implementation
will load the skill, configure MCP servers, and stream results back to
Slack via the thread_callback.

References:
- Claude Agent SDK docs: https://docs.claude.com/en/docs/agent-sdk/
- Skills:                https://platform.claude.com/docs/en/agent-sdk/skills
- MCP integration:       https://docs.claude.com/en/docs/agent-sdk/mcp

API names below need confirmation against current SDK release.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Awaitable, Callable

log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
MCP_CONFIG = PROJECT_ROOT / "mcp_config.json"

ThreadCallback = Callable[[str], Awaitable[None]]


async def run_workspace_setup(
    url: str,
    linkedin: str | None,
    drive_folder_id: str,
    thread_callback: ThreadCallback,
) -> None:
    """
    Run the workspace-context-and-icp-spec skill against `url`.

    Args:
        url:            company website URL
        linkedin:       optional LinkedIn company page URL
        drive_folder_id: ID of the per-run Drive folder
        thread_callback: async function used to post status messages
                         back to the Slack thread

    This is a stub. Next iteration will:
        1. Build ClaudeAgentOptions with skills_dir + mcp_config
        2. Build a prompt that invokes the workspace-setup skill
        3. Use `query(prompt, options)` to stream results
        4. For each agent message, call thread_callback to push to Slack
    """
    log.info("Stub run_workspace_setup invoked for %s", url)
    await thread_callback(
        f"🚧 Stub agent received: url={url}, linkedin={linkedin}, "
        f"drive_folder={drive_folder_id}. Real skill invocation comes next."
    )

    # TODO (next iteration):
    # from claude_agent_sdk import query, ClaudeAgentOptions
    #
    # options = ClaudeAgentOptions(
    #     cwd=str(PROJECT_ROOT),
    #     # skills_dir or setting_sources — confirm in SDK docs
    #     allowed_tools=["Skill", "WebFetch", "WebSearch", "Read", "Write"],
    #     mcp_config_path=str(MCP_CONFIG),  # confirm parameter name
    #     anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
    # )
    #
    # prompt = f"""
    # Run the workspace-context-and-icp-spec skill on company {url}.
    # LinkedIn: {linkedin or 'not provided'}.
    # Save all artifacts to Drive folder {drive_folder_id}.
    # Stream progress updates as you go.
    # """
    #
    # async for message in query(prompt, options=options):
    #     # message is an AssistantMessage; extract text and push to Slack
    #     text = _extract_text(message)
    #     if text:
    #         await thread_callback(text)
