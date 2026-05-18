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
from typing import Tuple  # noqa: F401

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
    Sets it to 'anyone with link can comment' so teammates can view/comment
    without explicit per-person sharing. All files created inside inherit
    this permission.
    Returns the new folder's ID.
    """
    drive = get_drive_service()
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id],
    }
    folder = drive.files().create(body=metadata, fields="id, name").execute()
    folder_id = folder["id"]

    try:
        drive.permissions().create(
            fileId=folder_id,
            body={"type": "anyone", "role": "commenter"},
        ).execute()
        log.info(
            "Created Drive folder %s (id=%s, anyone-with-link=commenter)",
            folder["name"], folder_id,
        )
    except Exception as e:
        log.warning(
            "Folder %s created but failed to set 'anyone with link' permission: %s",
            folder_id, e,
        )

    return folder_id


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


def folder_link(folder_id: str) -> str:
    return f"https://drive.google.com/drive/folders/{folder_id}"


def doc_link(doc_id: str) -> str:
    return f"https://docs.google.com/document/d/{doc_id}/edit"


def upload_markdown_as_doc(folder_id: str, title: str, md_text: str) -> tuple[str, str]:
    """
    Upload Markdown text as a Google Doc inside `folder_id`.
    Returns (doc_id, doc_url).
    """
    doc_id = create_doc(folder_id, title, body_text=md_text)
    return doc_id, doc_link(doc_id)


def upload_local_folder(
    local_dir: Path, drive_folder_id: str, version_suffix: str = ""
) -> list[tuple[str, str]]:
    """
    Walk `local_dir`, upload each .md file as a Google Doc into `drive_folder_id`.
    If `version_suffix` is set (e.g. "_v1.1"), it's appended to each doc title.
    Returns list of (file_name, doc_url) tuples.
    """
    uploaded: list[tuple[str, str]] = []
    if not local_dir.exists():
        log.warning("Upload source dir does not exist: %s", local_dir)
        return uploaded

    md_files = sorted(local_dir.rglob("*.md"))
    log.info("Uploading %d md files from %s to Drive folder %s (suffix=%r)",
             len(md_files), local_dir, drive_folder_id, version_suffix)

    for md_path in md_files:
        title = md_path.stem + version_suffix
        body = md_path.read_text()
        try:
            _, url = upload_markdown_as_doc(drive_folder_id, title, body)
            uploaded.append((title, url))
        except Exception as e:
            log.exception("Failed to upload %s: %s", md_path, e)
    return uploaded


# ----- Comments + revision-time helpers --------------------------------------

def list_files_in_folder(folder_id: str) -> list[dict]:
    """
    Return [{id, name, mimeType}] for non-trashed children of the folder.
    Only includes Google Docs (not folders, not other types).
    """
    drive = get_drive_service()
    resp = drive.files().list(
        q=(
            f"'{folder_id}' in parents "
            "and mimeType = 'application/vnd.google-apps.document' "
            "and trashed = false"
        ),
        fields="files(id, name, mimeType)",
        pageSize=200,
    ).execute()
    return resp.get("files", [])


def list_unresolved_comments(file_id: str) -> list[dict]:
    """
    Return unresolved comments on a Google Doc.
    Each item: {id, content, author_name, modified_time, anchor, replies: [...]}
    """
    drive = get_drive_service()
    resp = drive.comments().list(
        fileId=file_id,
        fields=(
            "comments("
            "id,content,resolved,createdTime,modifiedTime,anchor,"
            "author(displayName),replies(id,content,author(displayName))"
            ")"
        ),
        pageSize=100,
    ).execute()
    out = []
    for c in resp.get("comments", []):
        if c.get("resolved"):
            continue
        out.append({
            "id": c["id"],
            "content": c.get("content", ""),
            "author_name": (c.get("author") or {}).get("displayName", "?"),
            "modified_time": c.get("modifiedTime", ""),
            "anchor": c.get("anchor", ""),
            "replies": [
                {
                    "id": r.get("id"),
                    "content": r.get("content", ""),
                    "author_name": (r.get("author") or {}).get("displayName", "?"),
                }
                for r in c.get("replies", []) or []
            ],
        })
    return out


def resolve_comment(file_id: str, comment_id: str) -> None:
    """Mark a comment as resolved by replying with action=resolve."""
    drive = get_drive_service()
    # Drive API: resolve via replies.create with action="resolve"
    drive.replies().create(
        fileId=file_id,
        commentId=comment_id,
        fields="id,action",
        body={"action": "resolve"},
    ).execute()


def fetch_doc_text(doc_id: str) -> str:
    """
    Return the plain text content of a Google Doc.
    Concatenates all text runs in document order.
    """
    docs = get_docs_service()
    doc = docs.documents().get(documentId=doc_id).execute()
    parts: list[str] = []
    for el in (doc.get("body") or {}).get("content", []):
        para = el.get("paragraph")
        if not para:
            continue
        for run in para.get("elements", []):
            text_run = run.get("textRun")
            if text_run and text_run.get("content"):
                parts.append(text_run["content"])
    return "".join(parts)
