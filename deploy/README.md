# Hetzner Deployment

Step-by-step setup for running `outrizz-lab-bot` on an Ubuntu Hetzner box as a systemd service.

Target environment: Ubuntu 22.04 or 24.04 LTS, SSH access with key auth, sudo available.

---

## 1. First-time server setup

SSH to the box as your usual user:

```bash
ssh you@your-hetzner-host
```

### 1.1 Install system packages

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv git curl
# Install Node.js 20+ (needed by Slack and Google Drive MCP servers)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs
# Install uv (Python package manager — fast)
curl -LsSf https://astral.sh/uv/install.sh | sh
# uv lives at ~/.cargo/bin/uv — make sure it's on PATH or symlink:
sudo ln -sf "$HOME/.cargo/bin/uv" /usr/local/bin/uv
```

### 1.2 Create a dedicated `outrizz` user

```bash
sudo useradd -m -s /bin/bash outrizz
sudo mkdir -p /home/outrizz/.config/outrizz
sudo chown -R outrizz:outrizz /home/outrizz/.config
```

### 1.3 Clone the repo

```bash
sudo mkdir -p /opt
sudo git clone git@github.com:OUR-ORG/outrizz-lab-bot.git /opt/outrizz-lab-bot
sudo chown -R outrizz:outrizz /opt/outrizz-lab-bot
```

(Or use HTTPS + a deploy token if SSH keys for the `outrizz` user aren't set up yet.)

### 1.4 Create `.env`

```bash
sudo -u outrizz bash -c '
cd /opt/outrizz-lab-bot
cp .env.example .env
'
```

Then edit `/opt/outrizz-lab-bot/.env` and fill in real values. Note: on the server, set:

```
GOOGLE_OAUTH_CLIENT_PATH=/home/outrizz/.config/outrizz/google_oauth_client.json
GOOGLE_TOKEN_PATH=/home/outrizz/.config/outrizz/google_token.json
```

### 1.5 Upload Google OAuth client + token

From your Mac, after running `scripts/first_run_oauth.py` locally:

```bash
scp /Users/you/.config/outrizz/google_oauth_client.json \
    you@your-hetzner-host:/tmp/

scp /Users/you/.config/outrizz/google_token.json \
    you@your-hetzner-host:/tmp/

# On the server:
sudo mv /tmp/google_oauth_client.json /home/outrizz/.config/outrizz/
sudo mv /tmp/google_token.json /home/outrizz/.config/outrizz/
sudo chown outrizz:outrizz /home/outrizz/.config/outrizz/*.json
sudo chmod 600 /home/outrizz/.config/outrizz/*.json
```

### 1.6 Install Python dependencies

```bash
cd /opt/outrizz-lab-bot
sudo -u outrizz uv sync
```

This creates `.venv/` inside the repo with all dependencies.

### 1.7 Install the systemd unit

```bash
sudo cp /opt/outrizz-lab-bot/deploy/outrizz-lab-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable outrizz-lab-bot
sudo systemctl start outrizz-lab-bot
```

### 1.8 Verify

```bash
sudo systemctl status outrizz-lab-bot
journalctl -u outrizz-lab-bot -f
```

You should see the bot connecting to Slack in the logs. In `#workspace-lab`, mention it:

```
@outrizz-bot setup https://stripe.com
```

---

## 2. Subsequent deploys

After pushing new commits to GitHub:

```bash
# From your Mac:
ssh you@your-hetzner-host 'sudo -u outrizz bash /opt/outrizz-lab-bot/deploy/deploy.sh'
```

Or SSH in and run `bash /opt/outrizz-lab-bot/deploy/deploy.sh` manually.

---

## 3. Common commands

```bash
# Restart
sudo systemctl restart outrizz-lab-bot

# Stop
sudo systemctl stop outrizz-lab-bot

# Tail logs
journalctl -u outrizz-lab-bot -f

# Last 100 log lines
journalctl -u outrizz-lab-bot -n 100 --no-pager

# Check service status
sudo systemctl status outrizz-lab-bot
```

---

## 4. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Missing required env vars` at startup | `.env` not filled / wrong path | Check `EnvironmentFile=` in the systemd unit; verify `.env` exists at `/opt/outrizz-lab-bot/.env` |
| `No Google token at ...` | `google_token.json` not uploaded | Run `scripts/first_run_oauth.py` on Mac, scp to server |
| Bot connects but ignores mentions | Wrong bot token / wrong channel ID | Verify `SLACK_BOT_TOKEN` and `WORKSPACE_LAB_CHANNEL_ID` in `.env` |
| `npx` errors when MCP starts | Node.js not installed | `sudo apt install nodejs` (need v20+) |
| Permission denied on `/home/outrizz/.config/outrizz` | Wrong ownership | `sudo chown -R outrizz:outrizz /home/outrizz/.config` |

---

## 5. Backup considerations

For Phase 0:
- `state.json` — gets regenerated easily, but if you want to back up: `cp /opt/outrizz-lab-bot/state.json /home/outrizz/backups/`
- Drive artifacts — Google handles Drive backups
- `.env` — keep a copy in 1Password / Keychain on your Mac

For Phase 1+ when state.json grows: consider Litestream → S3, or migrate to SQLite/Postgres.
