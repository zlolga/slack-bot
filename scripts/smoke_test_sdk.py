#!/usr/bin/env python3
"""
Minimal smoke test for claude-agent-sdk.

Calls query() with a trivial prompt and prints every message it gets.
If this hangs for >60s, the problem is the SDK / env / API, not our code.

Usage:
    uv run python scripts/smoke_test_sdk.py
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

from claude_agent_sdk import ClaudeAgentOptions, query  # noqa: E402


async def main() -> None:
    print("=== smoke test: claude-agent-sdk ===")
    print(f"Time: {time.strftime('%H:%M:%S')}")

    options = ClaudeAgentOptions(
        system_prompt="You are a calculator. Answer with just the number.",
        allowed_tools=[],
    )

    prompt = "What is 2 + 2?"

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
    except Exception as e:
        elapsed = time.monotonic() - start
        print(f"[{elapsed:6.2f}s] ERROR: {type(e).__name__}: {e}")
        sys.exit(1)

    elapsed = time.monotonic() - start
    print(f"\n=== done in {elapsed:.2f}s ({msg_count} messages) ===")


if __name__ == "__main__":
    asyncio.run(main())
