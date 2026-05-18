"""
Google OAuth helpers.

The first-run consent flow runs in a browser on a machine that has one
(i.e. Olga's Mac), produces `google_token.json`, and that token is then
copied to the server. The token auto-refreshes — the access token is short
lived (~1h) but the refresh token survives until manually revoked or
~6 months of disuse.

This module exposes:
    - SCOPES: the OAuth scopes the bot needs
    - load_credentials(): return refreshed Credentials from disk
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
]


def load_credentials(token_path: Path) -> Credentials:
    """
    Load cached credentials from disk and refresh if expired.

    Raises FileNotFoundError if token_path doesn't exist — that means the
    first-run OAuth has not been done yet on this machine.
    """
    if not token_path.exists():
        raise FileNotFoundError(
            f"No Google token at {token_path}. "
            f"Run scripts/first_run_oauth.py once on a machine with a browser."
        )

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.expired and creds.refresh_token:
        log.info("Refreshing Google access token")
        creds.refresh(Request())
        token_path.write_text(creds.to_json())
    return creds
