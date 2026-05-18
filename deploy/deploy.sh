#!/usr/bin/env bash
# Pull latest code on the server, sync dependencies, and restart the bot.
# Run this ON the Hetzner box (or via SSH from your Mac).
#
# Assumes:
#   - repo cloned at /opt/outrizz-lab-bot
#   - .env exists at /opt/outrizz-lab-bot/.env
#   - google_token.json exists at ~outrizz/.config/outrizz/
#   - systemd unit installed (see deploy/README.md)
#
# Usage on server:
#   sudo -u outrizz bash /opt/outrizz-lab-bot/deploy/deploy.sh
#
# Usage from Mac (one-liner):
#   ssh you@hetzner 'sudo -u outrizz bash /opt/outrizz-lab-bot/deploy/deploy.sh'

set -euo pipefail

REPO_DIR="/opt/outrizz-lab-bot"
SERVICE="outrizz-lab-bot"

cd "$REPO_DIR"

echo "==> Pulling latest from main"
git pull --ff-only origin main

echo "==> Syncing Python dependencies with uv"
uv sync --frozen

echo "==> Restarting systemd service"
sudo systemctl restart "$SERVICE"

echo "==> Status"
sudo systemctl status "$SERVICE" --no-pager --lines=5

echo ""
echo "Logs: journalctl -u $SERVICE -f"
