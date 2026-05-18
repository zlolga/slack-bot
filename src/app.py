"""
Slack Bolt entrypoint for the Outrizz lab-mode workspace-setup bot.

Run with: uv run python -m src.app
Stops with: Ctrl+C
"""

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from .handlers import commands, mentions, reactions
from .state import StateStore

# --- Setup ------------------------------------------------------------------

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("outrizz-lab-bot")

REQUIRED_ENV = [
    "ANTHROPIC_API_KEY",
    "SLACK_BOT_TOKEN",
    "SLACK_SIGNING_SECRET",
    "SLACK_APP_TOKEN",
    "WORKSPACE_LAB_CHANNEL_ID",
    "GOOGLE_OAUTH_CLIENT_PATH",
    "GOOGLE_TOKEN_PATH",
    "DRIVE_LAB_FOLDER_ID",
]


def _check_env() -> None:
    missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {', '.join(missing)}. "
            f"Copy .env.example to .env and fill in values."
        )


# --- Slack app initialization -----------------------------------------------

_check_env()
app = AsyncApp(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)

state = StateStore(Path(os.environ.get("STATE_PATH", "./state.json")))

# --- Handler registration ---------------------------------------------------

mentions.register(app, state)
reactions.register(app, state)
commands.register(app, state)


@app.event("message")
async def _ignore_messages(body, logger):
    # Bolt warns if message events are unhandled; we listen only to mentions/reactions.
    pass


@app.error
async def global_error_handler(error, body, logger):
    logger.exception("Unhandled error: %s", error)


# --- Entrypoint -------------------------------------------------------------


async def main() -> None:
    log.info("Starting outrizz-lab-bot (Phase 0 lab mode)")
    log.info("Watching channel: %s", os.environ["WORKSPACE_LAB_CHANNEL_ID"])
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Stopped by user.")
