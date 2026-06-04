#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ $(id -u) -eq 0 ]]; then
  echo "This script should be run as a regular user with sudo privileges, not root."
  exit 1
fi

function require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command '$1' not found."
    exit 1
  fi
}

require_command sudo

# 1) System packages
sudo apt-get update
sudo apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  software-properties-common \
  build-essential \
  libffi-dev \
  libssl-dev \
  libpq-dev \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  python3.11-distutils

# 2) Docker Engine + Compose plugin
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 3) Add current user to docker group for convenience
if ! groups "$USER" | grep -qw docker; then
  echo "Adding $USER to docker group. You may need to log out and log back in for this to take effect."
  sudo usermod -aG docker "$USER"
fi

# 4) Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 5) Repo environment setup
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example. Please review and replace placeholder secrets before running the app."
fi

PYTHON=python3.11
VENV_DIR=.venv
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating Python venv at $VENV_DIR"
  $PYTHON -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements/base.txt

cat <<'EOF'

VM environment setup is complete.

Next steps:
  1) If you just installed Docker, log out and log back in or run:
       newgrp docker
  2) Review .env and replace all CHANGE_ME placeholders.
  3) Start the default stack from the repository root:
       docker compose up --build

Optional local Python dev environment:
  source .venv/bin/activate
  pip install -r requirements/dev.txt

Frontend development:
  cd app/frontend
  npm ci
  npm run dev

EOF
