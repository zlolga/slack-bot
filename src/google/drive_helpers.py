"""
Google Drive helpers — workarounds for the MCP's current limitations.

The first-party `@anthropic/mcp-google-drive` MCP supports CREATE and READ
but NOT update/move/rename/delete of existing items. For Phase 0 we route
those operations through the direct google-api-python-client here.

What this module provides:
    - get_drive_service(): returns an authenticated Drive v3 client
    - create_run_folder(parent_id, name): create a subfolder under Lab/
    - touch_doc(folder_id, name, content): create a Google Doc with content

Used by the agent's tools and by scripts/first_run_oauth.py.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from googleapiclient.discovery import build

from .oauth import load_credentials

log = logging.getLogger(__name__)


def get_drive_service():
    """Return an authenticated Drive v3 client."""
    token_path = Path(os.environ["GOOGLE_TOKEN_PATH"])
    creds = load_credentials(token_path)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def get_docs_service():
    """Return an authenticated Docs v1 client."""
    token_path = Path(os.environ["GOOGLE_TOKEN_PATH"])
    creds = load_credentials(token_path)
    return build("docs", "v1", credentials=creds, cache_discovery=False)


def create_run_folder(parent_folder_id: str, name: str) -> str:
    """
    Create a subfolder under the Lab parent folder.
    Returns the new folder's ID.
    """
    drive = get_drive_service()
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }
    folder = drive.files().create(body=metadata, fields="id, name").execute()
    log.info("Created Drive folder %s (id=%s)", folder["name"], folder["id"])
    return folder["id"]


def create_doc(folder_id: str, title: str, body_text: str = "") -> str:
    """
    Create a native Google Doc inside `folder_id` with optional body text.
    Returns the new doc's ID.
    """
    drive = get_drive_service()
    metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    doc = drive.files().create(body=metadata, fields="id, name").execute()
    doc_id = doc["id"]

    if body_text:
        docs = get_docs_service()
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {"insertText": {"location": {"index": 1}, "text": body_text}}
                ]
            },
        ).execute()

    log.info("Created Google Doc %s (id=%s)", title, doc_id)
    return doc_id
