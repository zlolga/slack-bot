"""
State persistence for the lab-mode bot.

One JSON file (state.json) holds the registry of runs. Each run = one
@bot setup invocation, tied to a Slack thread_ts.

Status state machine:
    awaiting_confirm -> running -> smell_test -> extracting
        -> drafting -> qa -> v1_done -> (revising | promoting | cancelled)
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

log = logging.getLogger(__name__)

ACTIVE_STATUSES = {
    "awaiting_confirm",
    "running",
    "smell_test",
    "extracting",
    "drafting",
    "qa",
    "revising",
}
TERMINAL_STATUSES = {"v1_done", "cancelled", "failed"}


@dataclass
class Run:
    thread_ts: str
    channel_id: str
    company: str
    url: str
    linkedin: Optional[str] = None
    status: str = "awaiting_confirm"
    tier_scope: str = "T0"
    version: str = "v1"
    drive_folder_id: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    stage_history: list[dict] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    def mark(self, new_status: str, note: str = "") -> None:
        self.stage_history.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "from": self.status,
                "to": new_status,
                "note": note,
            }
        )
        self.status = new_status
        if new_status in TERMINAL_STATUSES:
            self.completed_at = datetime.now(timezone.utc).isoformat()


class StateStore:
    """Thin JSON-file-backed registry. Single-process safe."""

    def __init__(self, path: Path):
        self.path = path
        if not self.path.exists():
            self.path.write_text(json.dumps({"runs": []}))
        raw = json.loads(self.path.read_text() or '{"runs": []}')
        self._runs: list[Run] = [Run(**r) for r in raw.get("runs", [])]

    # --- Persistence ----

    def save(self) -> None:
        self.path.write_text(
            json.dumps({"runs": [asdict(r) for r in self._runs]}, indent=2)
        )

    # --- Queries ----

    def has_active_run(self) -> bool:
        return any(r.is_active() for r in self._runs)

    def active_run(self) -> Optional[Run]:
        return next((r for r in self._runs if r.is_active()), None)

    def find_by_thread(self, thread_ts: str) -> Optional[Run]:
        return next((r for r in self._runs if r.thread_ts == thread_ts), None)

    def all_runs(self) -> list[Run]:
        return list(self._runs)

    # --- Mutations ----

    def create_run(
        self,
        thread_ts: str,
        channel_id: str,
        url: str,
        linkedin: Optional[str] = None,
    ) -> Run:
        run = Run(
            thread_ts=thread_ts,
            channel_id=channel_id,
            company=_infer_company(url),
            url=url,
            linkedin=linkedin,
        )
        self._runs.append(run)
        self.save()
        log.info("Created run for %s (thread=%s)", run.company, thread_ts)
        return run

    def update(self, run: Run) -> None:
        self.save()


def _infer_company(url: str) -> str:
    """https://stripe.com -> 'Stripe'"""
    host = urlparse(url).netloc.replace("www.", "")
    return host.split(".")[0].capitalize() if host else url
