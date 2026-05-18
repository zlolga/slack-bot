#!/usr/bin/env python3
"""
Run once on a machine with a browser (e.g. Olga's Mac) to mint the
google_token.json file that the server will use forever after.

Usage:
    uv run python scripts/first_run_oauth.py

Reads:
    GOOGLE_OAUTH_CLIENT_PATH from .env
Writes:
    GOOGLE_TOKEN_PATH        from .env
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

# scripts/ → repo root → src
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.google.oauth import SCOPES  # noqa: E402

load_dotenv(REPO_ROOT / ".env")


def main() -> None:
    client_path = Path(os.environ["GOOGLE_OAUTH_CLIENT_PATH"])
    token_path = Path(os.environ["GOOGLE_TOKEN_PATH"])

    if not client_path.exists():
        sys.exit(
            f"OAuth client file not found at {client_path}.\n"
            f"Download it from Google Cloud Console "
            f"(APIs & Services → Credentials → your Desktop OAuth client → Download JSON)."
        )

    token_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading OAuth client from {client_path}")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_path), SCOPES)

    print("Opening browser for consent. Sign in as outrizz.bot@gmail.com.")
    creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json())
    print(f"Token saved to {token_path}")
    print(
        "Next: copy this token to the server with:\n"
        f"  scp {token_path} user@hetzner:{token_path}"
    )


if __name__ == "__main__":
    main()
