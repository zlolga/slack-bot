#!/usr/bin/env python3
"""
Same SDK setup as our bot's agent.run_workspace_setup — but with
just a "hello" prompt. Tells us whether the huge inlined skill content
in system_prompt is what's hanging the agent.

Usage:
    uv run python scripts/smoke_test_with_skill.py
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT))

from claude_agent_sdk import ClaudeAgentOptions, query  # noqa: E402

from src.agent import _build_system_prompt  # noqa: E402


async def main() -> None:
    sys_prompt = _build_system_prompt()
    print(f"system_prompt size: {len(sys_prompt):,} chars")

    options = ClaudeAgentOptions(
        cwd=str(REPO_ROOT),
        system_prompt=sys_prompt,
        allowed_tools=["WebSearch", "WebFetch", "Read", "Write", "Bash"],
        permission_mode="bypassPermissions",
    )

    prompt = "Just respond with the word 'ack' and nothing else. Do not run any tools."

    print(f"Time: {time.strftime('%H:%M:%S')}")
    print("Calling query()...")

    start = time.monotonic()
    msg_count = 0
    try:
        async for message in query(prompt=prompt, options=options):
            msg_count += 1
            elapsed = time.monotonic() - start
            print(
                f"[{elapsed:6.2f}s] msg #{msg_count}: type={type(message).__name__}, "
                f"repr={repr(message)[:200]}"
            )
            if msg_count >= 5:
                print("\n(stopping after 5 messages — looks healthy)")
                break
    except Exception as e:
        elapsed = time.monotonic() - start
        print(f"[{elapsed:6.2f}s] ERROR: {type(e).__name__}: {e}")
        raise

    elapsed = time.monotonic() - start
    print(f"\n=== done in {elapsed:.2f}s ({msg_count} messages) ===")


if __name__ == "__main__":
    asyncio.run(main())
